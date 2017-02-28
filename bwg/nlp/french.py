# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

# STD
import codecs

# EXT
import luigi
from nltk.tokenize.stanford import StanfordTokenizer
from nltk.tag.stanford import StanfordNERTagger
from nltk.parse.stanford import StanfordDependencyParser

# PROJECT
from config import (
	FRENCH_CORPUS_PATH,
	FRENCH_DEPENDENCY_PATH,
	FRENCH_NES_PATH,
	FRENCH_RELATIONS_PATH,
	FRENCH_SENTENCES_PATH,
	FRENCH_STANFORD_MODELS_PATH,
	FRENCH_STANFORD_NER_MODEL_PATH,
	STANDFORD_CORENLP_MODELS_PATH,
	FRENCH_STANFORD_DEPENDENCY_MODEL_PATH
)


# TODO: Pass data structures directly instead of writing into files?


class ReadCorpusTask(luigi.Task):
	"""
	Luigi task that reads a corpus.
	"""
	corpus_path = luigi.Parameter()

	def output(self):
		return luigi.LocalTarget(FRENCH_SENTENCES_PATH)

	def run(self):
		with codecs.open(self.corpus_path, "rb", "utf-8") as corpus_file:
			with self.output().open("w") as sentences_file:
				# TODO: Split sentences from corpus
				for line in corpus_file.readlines():
					print(line)
					sentences_file.write(line)


class NERTask(luigi.Task):
	"""
	Luigi task that performs Named Entity Recognition on a corpus.
	"""
	tokenizer = StanfordTokenizer(FRENCH_STANFORD_MODELS_PATH, encoding='utf-8')
	ner_tagger = StanfordNERTagger(FRENCH_STANFORD_NER_MODEL_PATH, FRENCH_STANFORD_MODELS_PATH, encoding='utf-8')

	def requires(self):
		return ReadCorpusTask(corpus_path=FRENCH_CORPUS_PATH)

	def output(self):
		return luigi.LocalTarget(FRENCH_NES_PATH)

	def run(self):
		with self.input().open("r") as sentences_file:
			with self.output().open("w") as nes_file:
				for line in sentences_file:
					tokenized_line = self.tokenizer.tokenize(line)
					ner_tagged_line = self.ner_tagger.tag(tokenized_line)
					print(ner_tagged_line)
					nes_file.write(ner_tagged_line)


class DependencyParseTask(luigi.Task):
	"""
	Luigi task that dependency-parses sentences in a corpus.
	"""
	dependency_parser = StanfordDependencyParser(
		FRENCH_STANFORD_DEPENDENCY_MODEL_PATH,
		STANDFORD_CORENLP_MODELS_PATH
	)

	def requires(self):
		return ReadCorpusTask(corpus_path=FRENCH_CORPUS_PATH)

	def output(self):
		return luigi.LocalTarget(FRENCH_DEPENDENCY_PATH)

	def run(self):
		with self.input().open("r") as sentences_file:
			with self.output().open("w") as dependency_file:
				for line in sentences_file:
					parsed_text = self.dependency_parser.raw_parse(line)
					print(parsed_text)
					dependency_file.write(parsed_text)


class OpenRelationExtractionTask(luigi.Task):
	"""
	Luigi task that performs Open Relation extraction on a corpus.
	"""
	def requires(self):
		return NERTask(), DependencyParseTask()

	def output(self):
		return luigi.LocalTarget(FRENCH_RELATIONS_PATH)

	def run(self):
		# TODO: Do Open Relation Extraction
		results = self.requires()
		print(results)


def _anti_pipeline():
	# TODO: Remove this later, just to make sure that paths etc. are correct
	tokenizer = StanfordTokenizer(FRENCH_STANFORD_MODELS_PATH, encoding='utf-8')
	ner_tagger = StanfordNERTagger(FRENCH_STANFORD_NER_MODEL_PATH, FRENCH_STANFORD_MODELS_PATH, encoding='utf-8')
	dependency_parser = StanfordDependencyParser(
		FRENCH_STANFORD_DEPENDENCY_MODEL_PATH,
		STANDFORD_CORENLP_MODELS_PATH
	)

	with codecs.open(FRENCH_CORPUS_PATH, "rb", "utf-8") as corpus_file:
			for line in corpus_file.readlines():
				tokenized_line = tokenizer.tokenize(line)
				ner_tagged_line = ner_tagger.tag(tokenized_line)
				print(ner_tagged_line)

				parsed_text = dependency_parser.raw_parse(line)
				print(parsed_text)


if __name__ == "__main__":
	_anti_pipeline()
	#luigi.build([OpenRelationExtractionTask()], local_scheduler=True)  # TODO: Use remote scheduler for server deployment
	#luigi.run(["OpenRelationExtractionTask"])
