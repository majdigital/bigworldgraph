# -*- coding: utf-8 -*-
"""
Defining standard tasks for the NLP pipeline.
"""

# STD
import uuid
import collections

# EXT
import luigi
import luigi.format
from nltk.tokenize.stanford import StanfordTokenizer
from nltk.tag.stanford import StanfordNERTagger, StanfordPOSTagger
from nltk.parse.stanford import StanfordDependencyParser

# PROJECT
from bwg.nlp.utilities import (
    serialize_dependency_parse_tree,
    serialize_tagged_sentence,
    serialize_relation,
    deserialize_line,
    deserialize_dependency_tree,
    TaskWorkflowMixin
)


class IDTaggingTask(luigi.Task, TaskWorkflowMixin):
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


class NERTask(luigi.Task, TaskWorkflowMixin):
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
        # Init necessary resources
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]
        stanford_models_path = self.task_config["STANFORD_MODELS_PATH"]
        stanford_ner_model_path = self.task_config["STANFORD_NER_MODEL_PATH"]
        tokenizer = StanfordTokenizer(stanford_models_path)
        ner_tagger = StanfordNERTagger(stanford_ner_model_path, stanford_models_path)
        workflow_kwargs = {
            "tokenizer": tokenizer,
            "ner_tagger": ner_tagger
        }

        # Main work
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_line(
                    line, **workflow_kwargs, new_state="ne_tagged", serializing_function=serialize_tagged_sentence,
                    output_file=output_file, pretty=pretty_serialization
                )

    @staticmethod
    def task_workflow(sentence, **workflow_kwargs):
        meta, data = sentence["meta"], sentence["data"]
        tokenizer = workflow_kwargs["tokenizer"]
        ner_tagger = workflow_kwargs["ner_tagger"]

        tokenized_sentence = tokenizer.tokenize(data)
        ner_tagged_sentence = ner_tagger.tag(tokenized_sentence)
        serializing_arguments = {
            "sentence_id": meta["id"],
            "tagged_sentence": ner_tagged_sentence
        }

        return serializing_arguments


class DependencyParseTask(luigi.Task, TaskWorkflowMixin):
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
        workflow_kwargs = {
            "dependency_parser": dependency_parser
        }

        # Main work
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_line(
                    line, **workflow_kwargs, new_state="dependency_task",
                    serializing_function=serialize_dependency_parse_tree, output_file=output_file,
                    pretty=pretty_serialization
                )

    def task_workflow(self, sentence, **workflow_kwargs):
        meta, data = sentence["meta"], sentence["data"]
        dependency_parser = workflow_kwargs["dependency_parser"]

        parsed_sentence = dependency_parser.raw_parse(sentence)

        serializing_arguments = {
            "sentence_id": meta["id"],
            "parse_trees": parsed_sentence
        }

        return serializing_arguments


class PoSTaggingTask(luigi.Task, TaskWorkflowMixin):
    """
    Luigi task that PoS tags a sentence in a corpus.
    """
    task_config = luigi.DictParameter()

    def requires(self):
        return IDTaggingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["POS_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    def run(self):
        # Init necessary resources
        corpus_encoding = self.task_config["CORPUS_ENCODING"]
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]
        stanford_postagger_path = self.task_config["STANFORD_POSTAGGER_PATH"]
        stanford_models_path = self.task_config["STANFORD_MODELS_PATH"]
        stanford_pos_model_path = self.task_config["STANFORD_POS_MODEL_PATH"]
        tokenizer = StanfordTokenizer(stanford_models_path)
        pos_tagger = StanfordPOSTagger(
            stanford_pos_model_path, path_to_jar=stanford_postagger_path, encoding=corpus_encoding
        )
        workflow_kwargs = {
            "tokenizer": tokenizer,
            "pos_tagger": pos_tagger
        }

        # Main work
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_line(
                    line, **workflow_kwargs, new_state="pos_tagged", serializing_function=serialize_tagged_sentence,
                    output_file=output_file, pretty=pretty_serialization
                )

    @staticmethod
    def task_workflow(sentence, **workflow_kwargs):
        meta, data = sentence["meta"], sentence["data"]
        tokenizer = workflow_kwargs["tokenizer"]
        pos_tagger = workflow_kwargs["pos_tagger"]

        tokenized_sentence = tokenizer.tokenize(data)
        pos_tagged_sentence = pos_tagger.tag(tokenized_sentence)

        serializing_arguments = {
            "sentence_id": meta["id"],
            "tagged_sentence": pos_tagged_sentence
        }

        return serializing_arguments


class NaiveOpenRelationExtractionTask(luigi.Task, TaskWorkflowMixin):
    """
    Luigi task that performs Open Relation extraction on a corpus.
    """
    task_config = luigi.DictParameter()

    def requires(self):
        return NERTask(task_config=self.task_config),\
               DependencyParseTask(task_config=self.task_config),\
               PoSTaggingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["ORE_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    def run(self):
        # pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]
        relations_sum = 0
        number_of_lines = 0

        with self.input()[0].open("r") as nes_input_file,\
             self.input()[1].open("r") as dependency_input_file,\
             self.input()[2].open("r") as pos_input_file:
            with self.output().open("w") as output_file:
                for nes_line, dependency_line, pos_line in zip(nes_input_file, dependency_input_file, pos_input_file):
                    number_of_lines += 1
                    sentence_id_1, ne_tagged_line = deserialize_line(nes_line)
                    sentence_id_2, dependency_tree = deserialize_dependency_tree(dependency_line)
                    sentence_id_3, pos_tagged_line = deserialize_line(pos_line)
                    assert sentence_id_1 == sentence_id_2 == sentence_id_3

                    # Info for summary
                    relations = self.extract_relations(dependency_tree, ne_tagged_line, pos_tagged_line)
                    relations_sum += len(relations)

                    for subj_phrase, verb, obj_phrase in relations:
                        serialized_relation = serialize_relation(
                            sentence_id_1, subj_phrase, verb, obj_phrase,
                            self._get_sentence(ne_tagged_line),
                            pretty=True
                        )
                        output_file.write("{}\n".format(serialized_relation))

        print("{} relations were extracted from {} sentences.".format(relations_sum, number_of_lines))

    @staticmethod
    def _get_sentence(ne_tagged_line):
        """
        Get the original (not de-tokenized) sentence from a line tagged with NE tags.
        """
        return " ".join([word for word, tag in ne_tagged_line])

    def _align_tagged_sentence(self, ne_tagged_sentence):
        """
        Align a NE tagged sentence with a dependency parse by omitting pre-defined punctuation marks.
        """
        omitted_tokens = self.task_config["OMITTED_TOKENS_FOR_ALIGNMENT"]

        return [
            (word, tag)
            for word, tag in ne_tagged_sentence
            if word not in omitted_tokens
        ]

    @staticmethod
    def _normalize_node_addresses(dependency_tree):
        """
        Normalize the node addresses in a dependency tree.
        Because of the parsing, they will often contain gaps in their numbering, which makes it harder to align them
        with the words of a NE tagged sentence.
        """
        # Delete graph's root node without word
        if dependency_tree["nodes"][0]["word"] is None:
            del dependency_tree["nodes"][0]

        normalized_dependency_tree = {"root": dependency_tree["root"], "nodes": {}}
        sorted_nodes = collections.OrderedDict(sorted(dependency_tree["nodes"].items()))
        normalizations = {
            address: normalized_address
            for address, normalized_address in zip(sorted_nodes, range(len(dependency_tree["nodes"])))
        }

        # Normalize addresses
        for (address, node) in sorted_nodes.items():
            # Adjust nodes address attribute, dependencies
            node["address"] = normalizations[address]

            for dependency in node["deps"]:
                if dependency == "rel":
                    continue

                node["deps"][dependency] = [normalizations[addr] for addr in node["deps"][dependency]]

            normalized_dependency_tree["nodes"][normalizations[address]] = node

        return normalized_dependency_tree

    def _extract_verb_nodes(self, dependency_tree, pos_tagged_line):
        """
        Extract those moderating (verb) nodes with a direct subject (nsubj) and object (dobj).
        """
        verb_node_pos_tags = self.task_config["VERB_NODE_POS_TAGS"]
        verb_nodes = []

        for address, node in dependency_tree["nodes"].items():
            if pos_tagged_line[address][1] in verb_node_pos_tags:
                if "nsubj" in node["deps"] and "dobj" in node["deps"]:
                    verb_nodes.append(node)

        return verb_nodes

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
                expanded_node.extend(self._expand_node(dependency_tree["nodes"][address], dependency_tree, is_verb_node))

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
    def _get_subj_and_obj(verb_node, dependency_tree):
        """
        Get the adjacent subject and object node from a verb node.
        """
        subj_node_index = verb_node["deps"]["nsubj"][0]
        subj_node = dependency_tree["nodes"][subj_node_index]
        obj_node_index = verb_node["deps"]["dobj"][0]
        obj_node = dependency_tree["nodes"][obj_node_index]

        return subj_node, obj_node

    def extract_relations(self, dependency_tree, ne_tagged_line, pos_tagged_line):
        """
        Extract relations involving Named Entities from a sentence, using a dependency graph and named entity tags.
        """
        # Normalize resources
        aligned_ne_tagged_line = self._align_tagged_sentence(ne_tagged_line)
        aligned_pos_tagged_line = self._align_tagged_sentence(pos_tagged_line)
        normalized_dependency_tree = self._normalize_node_addresses(dependency_tree)

        verb_nodes = self._extract_verb_nodes(normalized_dependency_tree, aligned_pos_tagged_line)
        extracted_relations = []

        for verb_node in verb_nodes:
            subj_node, obj_node = self._get_subj_and_obj(verb_node, normalized_dependency_tree)

            expanded_subj_node = self._expand_node(subj_node, normalized_dependency_tree)
            expanded_obj_node = self._expand_node(obj_node, normalized_dependency_tree)

            # TODO (FEATURE): Extend definition of verb nodes? (Allow more patterns)

            if self._expanded_node_is_ne_tagged(expanded_subj_node, aligned_ne_tagged_line) or \
               self._expanded_node_is_ne_tagged(expanded_obj_node, aligned_ne_tagged_line):
                    subj_phrase = self._join_expanded_node(expanded_subj_node)
                    obj_phrase = self._join_expanded_node(expanded_obj_node)
                    extracted_relations.append((subj_phrase, verb_node["word"], obj_phrase))

        return extracted_relations
