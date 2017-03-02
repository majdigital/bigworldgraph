# -*- coding: utf-8 -*-
"""
Defining standard tasks for the NLP pipeline.
"""

# STD
import codecs
import os
import uuid

# EXT
import luigi
from nltk.tokenize.stanford import StanfordTokenizer
from nltk.tag.stanford import StanfordNERTagger
from nltk.parse.stanford import StanfordDependencyParser

# PROJECT
from bwg.nlp.utilities import (
    serialize_dependency_parse_tree,
    serialize_ne_tagged_sentence,
    deserialize_line,
    deserialize_dependency_tree,
    get_serialized_dependency_tree_connections,
)


class ReadCorpusTask(luigi.Task):
    """
    Luigi task that reads a corpus.
    """
    task_config = luigi.DictParameter()

    def output(self):
        sentences_file_path = self.task_config["SENTENCES_FILE_PATH"]
        return luigi.LocalTarget(sentences_file_path)

    def run(self):
        # Init necessary resources
        corpus_file_path = self.task_config["CORPUS_FILE_PATH"]

        # Main work
        with codecs.open(corpus_file_path, "rb", "utf-8") as corpus_file, self.output().open("w") as sentences_file:
            for line in corpus_file.readlines():
                sentence_id = uuid.uuid4()
                sentences_file.write("{}\t{}\n".format(sentence_id, line.strip()))


class NERTask(luigi.Task):
    """
    Luigi task that performs Named Entity Recognition on a corpus.
    """
    task_config = luigi.DictParameter()

    def requires(self):
        return ReadCorpusTask(task_config=self.task_config)

    def output(self):
        nes_file_path = self.task_config["NES_FILE_PATH"]
        return luigi.LocalTarget(nes_file_path)

    def run(self):
        # Init necessary resources
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]
        stanford_models_path = self.task_config["STANFORD_MODELS_PATH"]
        stanford_ner_model_path = self.task_config["STANFORD_NER_MODEL_PATH"]
        tokenizer = StanfordTokenizer(stanford_models_path, encoding='utf-8')
        ner_tagger = StanfordNERTagger(stanford_ner_model_path, stanford_models_path, encoding='utf-8')

        # Main work
        with self.input().open("r") as sentences_file, self.output().open("w") as nes_file:
            for line in sentences_file:
                sentence_id, sentence = line.split("\t")
                tokenized_sentence = tokenizer.tokenize(sentence)
                ner_tagged_sentence = ner_tagger.tag(tokenized_sentence)
                serialized_sentence = serialize_ne_tagged_sentence(
                    sentence_id, ner_tagged_sentence, pretty=pretty_serialization
                )
                nes_file.write("{}\n".format(serialized_sentence))


class DependencyParseTask(luigi.Task):
    """
    Luigi task that dependency-parses sentences in a corpus.
    """
    task_config = luigi.DictParameter()

    def requires(self):
        return ReadCorpusTask(task_config=self.task_config)

    def output(self):
        dependency_file_path = self.task_config["DEPENDENCY_FILE_PATH"]
        return luigi.LocalTarget(dependency_file_path)

    def run(self):
        # Init necessary resources
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]
        stanford_dependency_model_path = self.task_config["STANFORD_DEPENDENCY_MODEL_PATH"]
        stanford_corenlp_models_path = self.task_config["STANFORD_CORENLP_MODELS_PATH"]
        dependency_parser = StanfordDependencyParser(stanford_dependency_model_path, stanford_corenlp_models_path)

        # Main work
        with self.input().open("r") as sentences_file, self.output().open("w") as dependency_file:
            for line in sentences_file:
                sentence_id, sentence = line.split("\t")
                parsed_sentence = dependency_parser.raw_parse(sentence)
                serialized_tree = serialize_dependency_parse_tree(
                    sentence_id, parsed_sentence, pretty=pretty_serialization
                )
                dependency_file.write("{}\n".format(serialized_tree))


class NaiveOpenRelationExtractionTask(luigi.Task):
    """
    Luigi task that performs Open Relation extraction on a corpus.
    """
    task_config = luigi.DictParameter()

    def requires(self):
        return NERTask(task_config=self.task_config), DependencyParseTask(task_config=self.task_config)

    def output(self):
        relations_file_path = self.task_config["RELATIONS_FILE_PATH"]
        return luigi.LocalTarget(relations_file_path)

    def run(self):
        # TODO: Do Open Relation Extraction

        with self.input()[0].open("r") as nes_file, self.input()[1].open("r") as dependency_file:
            with self.output().open("w") as relations_file:
                for nes_line, dependency_line in zip(nes_file, dependency_file):
                    sentence_id_1, ne_tagged_line = deserialize_line(nes_line)
                    sentence_id_2, dependency_tree = deserialize_dependency_tree(dependency_line)
                    assert sentence_id_1 == sentence_id_2

                    #get_serialized_dependency_tree_connections(dependency_tree)

                    self.extract_relations(dependency_tree, ne_tagged_line)

    def _extract_moderating_nodes(self, dependency_tree):
        """
        Extract those moderating (verb) nodes with a direct subject (nsubj) and object (dobj).
        """
        moderating_node_ctags = self.task_config["MODERATING_NODE_CTAGS"]
        moderating_nodes = []

        for address, node in dependency_tree["nodes"].items():
            if node["ctag"] in moderating_node_ctags:
                if "nsubj" in node["deps"] and "dobj" in node["deps"]:
                    moderating_nodes.append(node)

        return moderating_nodes

    def _check_moderating_nodes_children_importance(self, moderating_nodes, ner_tagged_line):
        pass

    def _expand_node(self, node, dependency_tree):
        expanded_node = [(node["address"], node["word"])]

        for dependency in node["deps"]:
            if dependency == "rel":
                continue

            for address in node["deps"][dependency]:
                expanded_node.extend(self._expand_node(dependency_tree["nodes"][address], dependency_tree))

        return expanded_node

    def _word_is_ne_tagged(self, word_index, ne_tagged_line):
        word, ne_tag = ne_tagged_line[word_index]
        return ne_tag in self.task_config["NER_TAGSET"]

    def _expanded_node_is_ne_tagged(self, expanded_node, ne_tagged_line):
        return any(
            [
                self._word_is_ne_tagged(address-1, ne_tagged_line)
                for address, word in expanded_node
            ]
        )

    @staticmethod
    def _join_expanded_node(expanded_node):
        sorted_expanded_node = sorted(expanded_node, key=lambda x: x[0])
        return " ".join([word for address, word in sorted_expanded_node])

    def extract_relations(self, dependency_tree, ne_tagged_line):
        moderating_nodes = self._extract_moderating_nodes(dependency_tree)
        extracted_relations = []

        for moderating_node in moderating_nodes:
            subj_node_index = moderating_node["deps"]["nsubj"][0]
            obj_node_index = moderating_node["deps"]["dobj"][0]

            expanded_subj_node = self._expand_node(dependency_tree["nodes"][subj_node_index], dependency_tree)
            expanded_obj_node = self._expand_node(dependency_tree["nodes"][obj_node_index], dependency_tree)

            # subj_phrase = self._join_expanded_node(expanded_subj_node)
            # obj_phrase = self._join_expanded_node(expanded_obj_node)

            # TODO: Use extended corpus? (1.)
            # TODO: Extend definition of moderating nodes? (2.)

            if self._expanded_node_is_ne_tagged(expanded_subj_node, ne_tagged_line) or\
                self._expanded_node_is_ne_tagged(expanded_obj_node, ne_tagged_line):
                    pass
