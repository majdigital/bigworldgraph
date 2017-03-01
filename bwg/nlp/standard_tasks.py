# -*- coding: utf-8 -*-
"""
Defining standard tasks for the NLP pipeline.
"""

# STD
import codecs
import uuid

# EXT
import luigi
from nltk.tokenize.stanford import StanfordTokenizer
from nltk.tag.stanford import StanfordNERTagger
from nltk.parse.stanford import StanfordDependencyParser

# PROJECT
from bwg.nlp.utilities import serialize_dependency_parse_tree, serialize_ne_tagged_sentence


class ReadCorpusTask(luigi.Task):
    """
    Luigi task that reads a corpus.
    """
    task_config = luigi.DictParameter()
    resources = {'overwrite_resource': 1}

    def output(self):
        sentences_file_path = self.task_config["sentences_file_path"]
        return luigi.LocalTarget(sentences_file_path)

    def run(self):
        # Init necessary resources
        corpus_file_path = self.task_config["corpus_file_path"]

        # Main work
        with codecs.open(corpus_file_path, "rb", "utf-8") as corpus_file:
            with self.output().open("w") as sentences_file:
                for line in corpus_file.readlines():
                    sentence_id = uuid.uuid4()
                    sentences_file.write("{}\t{}\n".format(sentence_id, line.strip()))


class NERTask(luigi.Task):
    """
    Luigi task that performs Named Entity Recognition on a corpus.
    """
    task_config = luigi.DictParameter()
    resources = {'overwrite_resource': 1}

    def requires(self):
        return ReadCorpusTask(task_config=self.task_config)

    def output(self):
        nes_file_path = self.task_config["nes_file_path"]
        return luigi.LocalTarget(nes_file_path)

    def run(self):
        # Init necessary resources
        pretty_serialization = self.task_config["pretty_serialization"]
        stanford_models_path = self.task_config["stanford_models_path"]
        stanford_ner_model_path = self.task_config["stanford_ner_model_path"]
        tokenizer = StanfordTokenizer(stanford_models_path, encoding='utf-8')
        ner_tagger = StanfordNERTagger(stanford_ner_model_path, stanford_models_path, encoding='utf-8')

        # Main work
        with self.input().open("r") as sentences_file:
            with self.output().open("w") as nes_file:
                for line in sentences_file:
                    sentence_id, sentence = line.split("\t")
                    tokenized_sentence = tokenizer.tokenize(sentence)
                    ner_tagged_sentence = ner_tagger.tag(tokenized_sentence)
                    serialized_sentence = serialize_ne_tagged_sentence(
                        sentence_id,
                        ner_tagged_sentence,
                        pretty=pretty_serialization
                    )
                    nes_file.write("{}\n".format(serialized_sentence))


class DependencyParseTask(luigi.Task):
    """
    Luigi task that dependency-parses sentences in a corpus.
    """
    task_config = luigi.DictParameter()
    resources = {'overwrite_resource': 1}

    def requires(self):
        return ReadCorpusTask(task_config=self.task_config)

    def output(self):
        dependency_file_path = self.task_config["dependency_file_path"]
        return luigi.LocalTarget(dependency_file_path)

    def run(self):
        # Init necessary resources
        pretty_serialization = self.task_config["pretty_serialization"]
        stanford_dependency_model_path = self.task_config["stanford_dependency_model_path"]
        stanford_corenlp_models_path = self.task_config["stanford_corenlp_models_path"]
        dependency_parser = StanfordDependencyParser(
            stanford_dependency_model_path,
            stanford_corenlp_models_path
        )

        # Main work
        with self.input().open("r") as sentences_file:
            with self.output().open("w") as dependency_file:
                for line in sentences_file:
                    sentence_id, sentence = line.split("\t")
                    parsed_sentence = dependency_parser.raw_parse(sentence)
                    serialized_tree = serialize_dependency_parse_tree(
                        sentence_id,
                        parsed_sentence,
                        pretty=pretty_serialization
                    )
                    dependency_file.write("{}\n".format(serialized_tree))


class OpenRelationExtractionTask(luigi.Task):
    """
    Luigi task that performs Open Relation extraction on a corpus.
    """
    task_config = luigi.DictParameter()
    resources = {'overwrite_resource': 1}

    def requires(self):
        return NERTask(task_config=self.task_config), DependencyParseTask(task_config=self.task_config)

    def output(self):
        relations_file_path = self.task_config["relations_file_path"]
        return luigi.LocalTarget(relations_file_path)

    def run(self):
        # TODO: Do Open Relation Extraction
        results = self.requires()
