# -*- coding: utf-8 -*-
"""
Defining standard tasks for the NLP pipeline.
"""

# STD
import codecs
import uuid
import collections

# EXT
import luigi
import luigi.format
from nltk.tokenize.stanford import StanfordTokenizer
from nltk.tag.stanford import StanfordNERTagger
from nltk.parse.stanford import StanfordDependencyParser

# PROJECT
from bwg.nlp.utilities import (
    serialize_dependency_parse_tree,
    serialize_ne_tagged_sentence,
    serialize_relation,
    deserialize_line,
    deserialize_dependency_tree
)


class IDTaggingTask(luigi.Task):
    """
    Luigi task that reads a corpus and assigns each sentence an ID.
    """
    task_config = luigi.DictParameter()

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["ID_TAGGING_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    def run(self):
        # Main work
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file.readlines():
                sentence_id = uuid.uuid4()
                output_file.write("{}\t{}\n".format(sentence_id, line.strip()))


class NERTask(luigi.Task):
    """
    Luigi task that performs Named Entity Recognition on a corpus.
    """
    task_config = luigi.DictParameter()

    def requires(self):
        return IDTaggingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["NES_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    def run(self):
        # TODO (BUG): Words with special characters get split?
        # Init necessary resources
        corpus_encoding = self.task_config["CORPUS_ENCODING"]
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]
        stanford_models_path = self.task_config["STANFORD_MODELS_PATH"]
        stanford_ner_model_path = self.task_config["STANFORD_NER_MODEL_PATH"]
        tokenizer = StanfordTokenizer(stanford_models_path)
        ner_tagger = StanfordNERTagger(stanford_ner_model_path, stanford_models_path)

        # Main work
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                sentence_id, sentence = line.split("\t")
                tokenized_sentence = tokenizer.tokenize(sentence)
                ner_tagged_sentence = ner_tagger.tag(tokenized_sentence)
                serialized_sentence = serialize_ne_tagged_sentence(
                    sentence_id, ner_tagged_sentence, pretty=pretty_serialization
                )
                output_file.write("{}\n".format(serialized_sentence))


class DependencyParseTask(luigi.Task):
    """
    Luigi task that dependency-parses sentences in a corpus.
    """
    task_config = luigi.DictParameter()

    def requires(self):
        return IDTaggingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["DEPENDENCY_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    def run(self):
        # Init necessary resources
        corpus_encoding = self.task_config["CORPUS_ENCODING"]
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]
        stanford_dependency_model_path = self.task_config["STANFORD_DEPENDENCY_MODEL_PATH"]
        stanford_corenlp_models_path = self.task_config["STANFORD_CORENLP_MODELS_PATH"]
        dependency_parser = StanfordDependencyParser(
            stanford_dependency_model_path, stanford_corenlp_models_path, encoding=corpus_encoding
        )

        # Main work
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                sentence_id, sentence = line.split("\t")
                parsed_sentence = dependency_parser.raw_parse(sentence)
                serialized_tree = serialize_dependency_parse_tree(
                    sentence_id, parsed_sentence, pretty=pretty_serialization
                )
                output_file.write("{}\n".format(serialized_tree))


class NaiveOpenRelationExtractionTask(luigi.Task):
    """
    Luigi task that performs Open Relation extraction on a corpus.
    """
    task_config = luigi.DictParameter()

    def requires(self):
        return NERTask(task_config=self.task_config), DependencyParseTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["ORE_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    def run(self):
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]

        with self.input()[0].open("r") as nes_input_file, self.input()[1].open("r") as dependency_input_file:
            with self.output().open("w") as output_file:
                for nes_line, dependency_line in zip(nes_input_file, dependency_input_file):
                    sentence_id_1, ne_tagged_line = deserialize_line(nes_line)
                    sentence_id_2, dependency_tree = deserialize_dependency_tree(dependency_line)
                    assert sentence_id_1 == sentence_id_2

                    relations = self.extract_relations(dependency_tree, ne_tagged_line)
                    for subj_phrase, verb, obj_phrase in relations:
                        # TODO (BUG): No pretty-printing?
                        serialized_relation = serialize_relation(
                            sentence_id_1, subj_phrase, verb, obj_phrase,
                            self._get_sentence(ne_tagged_line),
                            pretty=True
                        )
                        output_file.write("{}\n".format(serialized_relation))

    @staticmethod
    def _get_sentence(ne_tagged_line):
        return " ".join([word for word, tag in ne_tagged_line])

    def _align_ne_tagged_sentence(self, ne_tagged_sentence):
        omitted_tokens = self.task_config["OMITTED_TOKENS_FOR_ALIGNMENT"]

        return [
            (word, tag)
            for word, tag in ne_tagged_sentence
            if word not in omitted_tokens
        ]

    @staticmethod
    def _normalize_node_addresses(dependency_tree):
        # TODO (Bug): Also normalize references
        # Delete graph's root node without word
        if dependency_tree["nodes"][0]["word"] is None:
            del dependency_tree["nodes"][0]

        normalized_dependency_tree = {"root": dependency_tree["root"], "nodes": {}}
        sorted_nodes = collections.OrderedDict(sorted(dependency_tree["nodes"].items()))
        normalizations = {
            address: normalized_address
            for address, normalized_address in zip(sorted_nodes, range(len(dependency_tree["nodes"])))
        }

        for (address, node) in sorted_nodes.items():
            # Adjust nodes address attribute, dependencies
            node["address"] = normalizations[address]

            for dependency in node["deps"]:
                if dependency == "rel":
                    continue

                node["deps"][dependency] = [normalizations[addr] for addr in node["deps"][dependency]]

            normalized_dependency_tree["nodes"][normalizations[address]] = node

        return normalized_dependency_tree

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

    def _expand_node(self, node, dependency_tree, is_verb_node=False):
        """
        Expand a node from a dependency graph s.t. it includes the address and the word of all nodes that are dependent
        from it.
        """
        expanded_node = [(node["address"], node["word"])]

        for dependency in node["deps"]:
            if dependency == "rel":
                continue

            # Ignore noun and object phrases
            if is_verb_node and dependency in ("nsub", "dobj"):
                continue

            for address in node["deps"][dependency]:
                expanded_node.extend(self._expand_node(dependency_tree["nodes"][address], dependency_tree))

        return expanded_node

    def _word_is_ne_tagged(self, word_index, ne_tagged_line):
        """
        Check if a word is Named Entity tagged.
        """
        word, ne_tag = ne_tagged_line[word_index]
        return ne_tag in self.task_config["NER_TAGSET"]

    def _expanded_node_is_ne_tagged(self, expanded_node, ne_tagged_line):
        """
        Check if a word within an expanded node was assigned a Named Entity tag.
        """
        return any(
            [
                self._word_is_ne_tagged(address, ne_tagged_line)
                for address, word in expanded_node
            ]
        )

    @staticmethod
    def _join_expanded_node(expanded_node):
        """
        Join all the words from an extended word into a phrase.
        """
        sorted_expanded_node = sorted(expanded_node, key=lambda x: x[0])
        return " ".join([word for address, word in sorted_expanded_node])

    @staticmethod
    def _get_subj_and_obj(moderating_node, dependency_tree):
        subj_node_index = moderating_node["deps"]["nsubj"][0]
        subj_node = dependency_tree["nodes"][subj_node_index]
        obj_node_index = moderating_node["deps"]["dobj"][0]
        obj_node = dependency_tree["nodes"][obj_node_index]

        return subj_node, obj_node

    def extract_relations(self, dependency_tree, ne_tagged_line):
        """
        Extract relations involving Named Entities from a sentence, using a dependency graph and named entity tags.
        """
        aligned_ne_tagged_line = self._align_ne_tagged_sentence(ne_tagged_line)
        normalized_dependency_tree = self._normalize_node_addresses(dependency_tree)
        moderating_nodes = self._extract_moderating_nodes(normalized_dependency_tree)
        extracted_relations = []

        for moderating_node in moderating_nodes:
            subj_node, obj_node = self._get_subj_and_obj(moderating_node, normalized_dependency_tree)

            expanded_subj_node = self._expand_node(subj_node, normalized_dependency_tree)
            expanded_obj_node = self._expand_node(obj_node, normalized_dependency_tree)

            # TODO (FEATURE): Use extended corpus? (1.)
            # TODO (FEATURE): Extend definition of moderating nodes? (Allow more patterns) (2.)

            if self._expanded_node_is_ne_tagged(expanded_subj_node, aligned_ne_tagged_line) or\
                self._expanded_node_is_ne_tagged(expanded_obj_node, aligned_ne_tagged_line):
                    subj_phrase = self._join_expanded_node(expanded_subj_node)
                    obj_phrase = self._join_expanded_node(expanded_obj_node)

                    # TODO (BUG) Verb node is not expanded correctly
                    expanded_verb_node = self._expand_node(
                        moderating_node, normalized_dependency_tree, is_verb_node=True
                    )
                    verb_phrase = self._join_expanded_node(expanded_verb_node)

                    extracted_relations.append((subj_phrase, verb_phrase, obj_phrase))

        return extracted_relations
