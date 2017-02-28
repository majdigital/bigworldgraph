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

    def requires(self):
        return luigi.LocalTarget(self.corpus_path)

    def output(self):
        return luigi.LocalTarget(FRENCH_SENTENCES_PATH)

    def run(self):
        with codecs.open(self.corpus_path, "rb", "utf-8") as corpus_file:
            with codecs.open(self.output(), "rb", "utf-8") as sentences_file:
                # TODO: Split sentences from corpus
                line = corpus_file.readline()
                while line:
                    sentences_file.write(sentences_file)
                    line = corpus_file.readline()


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
        with codecs.open(self.input(), "rb", "utf-8") as sentences_file:
            with codecs.open(self.output(), "rb", "utf-8") as nes_file:
                for line in sentences_file.readlines():
                    tokenized_line = self.tokenizer.tokenize(line)
                    ner_tagged_line = self.ner_tagger.tag(tokenized_line)
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
        with codecs.open(self.input(), "rb", "utf-8") as sentences_file:
            with codecs.open(self.output(), "rb", "utf-8") as dependency_file:
                for line in dependency_file.readlines():
                    parsed_text = self.dependency_parser.raw_parse(line)
                    sentences_file.write(parsed_text)


class OpenRelationExtractionTask(luigi.Task):
    """
    Luigi task that performs Open Relation extraction on a corpus.
    """
    def requires(self):
        return {
            "nes": NERTask(),
            "dependency": DependencyParseTask()
        }

    def output(self):
        return luigi.LocalTarget(FRENCH_RELATIONS_PATH)

    def run(self):
        # TODO: Do Open Relation Extraction
        pass


def pipeline_french():
    pipeline = OpenRelationExtractionTask()
    return pipeline.run()


if __name__ == "__main__":
    print(pipeline_french())
