# -*- coding: utf-8 -*-
"""
Defining standard tasks for the NLP pipeline.
"""

# STD
import collections

# EXT
import luigi
import luigi.format
from nltk.tokenize.stanford import StanfordTokenizer
from nltk.tag.stanford import StanfordNERTagger, StanfordPOSTagger
from nltk.parse.stanford import StanfordDependencyParser

# PROJECT
from bwg.misc.helpers import time_function
from bwg.nlp.utilities import (
    serialize_dependency_parse_tree,
    serialize_tagged_sentence,
    serialize_relation
)
from bwg.nlp.mixins import ArticleProcessingMixin
from bwg.nlp.wikipedia_tasks import WikipediaReadingTask


class NERTask(luigi.Task, ArticleProcessingMixin):
    """
    Luigi task that performs Named Entity Recognition on a corpus.
    """
    def requires(self):
        return WikipediaReadingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["NES_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True, give_report=True)
    def run(self):
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_articles(
                    line, new_state="ne_tagged", serializing_function=serialize_tagged_sentence, output_file=output_file
                )

    @property
    def workflow_resources(self):
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]
        stanford_models_path = self.task_config["STANFORD_MODELS_PATH"]
        stanford_ner_model_path = self.task_config["STANFORD_NER_MODEL_PATH"]
        corpus_encoding = self.task_config["CORPUS_ENCODING"]

        tokenizer = StanfordTokenizer(stanford_models_path, encoding=corpus_encoding)
        ner_tagger = StanfordNERTagger(stanford_ner_model_path, stanford_models_path, encoding=corpus_encoding)

        workflow_resources = {
            "tokenizer": tokenizer,
            "ner_tagger": ner_tagger,
            "pretty": pretty_serialization
        }

        return workflow_resources

    def task_workflow(self, article, **workflow_resources):
        article_data = article["data"]

        for sentence_id, sentence_json in article_data.items():
            sentence_data = sentence_json["data"]
            ner_tagged_sentence = self._ner_tag(sentence_data, **workflow_resources)

            serializing_arguments = {
                "sentence_id": sentence_id,
                "tagged_sentence": ner_tagged_sentence
            }

            yield serializing_arguments

    def _ner_tag(self, sentence_data, **workflow_resources):
        """
        Tag a single sentence with named entities.
        """
        tokenizer = workflow_resources["tokenizer"]
        ner_tagger = workflow_resources["ner_tagger"]

        tokenized_sentence = tokenizer.tokenize(sentence_data)
        ner_tagged_sentence = ner_tagger.tag(tokenized_sentence)

        return ner_tagged_sentence


class DependencyParseTask(luigi.Task, ArticleProcessingMixin):
    """
    Luigi task that dependency-parses sentences in a corpus.
    """
    def requires(self):
        return WikipediaReadingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["DEPENDENCY_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True, give_report=True)
    def run(self):
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_articles(
                    line, new_state="dependency_parsed",
                    serializing_function=serialize_dependency_parse_tree, output_file=output_file,
                )

    @property
    def workflow_resources(self):
        corpus_encoding = self.task_config["CORPUS_ENCODING"]
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]
        stanford_dependency_model_path = self.task_config["STANFORD_DEPENDENCY_MODEL_PATH"]
        stanford_corenlp_models_path = self.task_config["STANFORD_CORENLP_MODELS_PATH"]

        dependency_parser = StanfordDependencyParser(
            stanford_dependency_model_path, stanford_corenlp_models_path, encoding=corpus_encoding
        )

        workflow_resources = {
            "dependency_parser": dependency_parser,
            "pretty": pretty_serialization
        }

        return workflow_resources

    def task_workflow(self, article, **workflow_resources):
        article_data = article["data"]

        for sentence_id, sentence_json in article_data.items():
            sentence_data = sentence_json["data"]
            parsed_sentence = self._dependency_parse(sentence_data, **workflow_resources)

            serializing_arguments = {
                "sentence_id": sentence_id,
                "parse_trees": parsed_sentence
            }

            yield serializing_arguments

    def _dependency_parse(self, sentence_data, **workflow_resources):
        """
        Dependency parse a sentence.
        """
        dependency_parser = workflow_resources["dependency_parser"]

        parsed_sentence = dependency_parser.raw_parse(sentence_data)

        return parsed_sentence


class PoSTaggingTask(luigi.Task, ArticleProcessingMixin):
    """
    Luigi task that PoS tags a sentence in a corpus.
    """
    def requires(self):
        return WikipediaReadingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["POS_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True, give_report=True)
    def run(self):

        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_articles(
                    line, new_state="pos_tagged", serializing_function=serialize_tagged_sentence,
                    output_file=output_file
                )

    @property
    def workflow_resources(self):
        corpus_encoding = self.task_config["CORPUS_ENCODING"]
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]
        stanford_postagger_path = self.task_config["STANFORD_POSTAGGER_PATH"]
        stanford_models_path = self.task_config["STANFORD_MODELS_PATH"]
        stanford_pos_model_path = self.task_config["STANFORD_POS_MODEL_PATH"]

        tokenizer = StanfordTokenizer(stanford_models_path, encoding=corpus_encoding)
        pos_tagger = StanfordPOSTagger(
            stanford_pos_model_path, path_to_jar=stanford_postagger_path, encoding=corpus_encoding
        )

        workflow_resources = {
            "tokenizer": tokenizer,
            "pos_tagger": pos_tagger,
            "pretty": pretty_serialization
        }

        return workflow_resources

    def task_workflow(self, article, **workflow_resources):
        article_data = article["data"]

        for sentence_id, sentence_json in article_data.items():
            sentence_data = sentence_json["data"]
            pos_tagged_sentence = self._pos_tag(sentence_data, **workflow_resources)

            serializing_arguments = {
                "sentence_id": sentence_id,
                "tagged_sentence": pos_tagged_sentence
            }

            yield serializing_arguments

    def _pos_tag(self, sentence_data, **workflow_resources):
        """
        Tag a single sentence with Part-of-Speech tags.
        """
        tokenizer = workflow_resources["tokenizer"]
        pos_tagger = workflow_resources["pos_tagger"]

        tokenized_sentence = tokenizer.tokenize(sentence_data)
        pos_tagged_sentence = pos_tagger.tag(tokenized_sentence)

        return pos_tagged_sentence


class NaiveOpenRelationExtractionTask(luigi.Task, ArticleProcessingMixin):
    """
    Luigi task that performs Open Relation extraction on a corpus.
    """
    def requires(self):
        return NERTask(task_config=self.task_config),\
               DependencyParseTask(task_config=self.task_config),\
               PoSTaggingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["ORE_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True, give_report=True)
    def run(self):
        with self.input()[0].open("r") as nes_input_file, self.input()[1].open("r") as dependency_input_file,\
         self.input()[2].open("r") as pos_input_file, self.output().open("w") as output_file:
            for nes_line, dependency_line, pos_line in zip(nes_input_file, dependency_input_file, pos_input_file):
                self.process_articles(
                    (nes_line, dependency_line, pos_line), new_state="extracted_relations",
                    serializing_function=serialize_relation, output_file=output_file, pretty=True
                )

    @property
    def workflow_resources(self):
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]

        workflow_resources = {
            "pretty": pretty_serialization
        }

        return workflow_resources

    def task_workflow(self, article, **workflow_resources):
        article_meta, article_data = article["meta"], article["data"]

        for sentence_id, sentence_json in article_data.items():
            sentence_dates = sentence_json["data"]
            relations, sentence = self._extract_relations_from_sentence(sentence_dates, **workflow_resources)

            serializing_arguments = {
                "sentence_id": sentence_id,
                "sentence": sentence,
                "relations": relations
            }

            yield serializing_arguments

    def _extract_relations_from_sentence(self, sentence_dates, **workflow_resources):
        enriched_sentences = [sentence_date["data"] for sentence_date in sentence_dates.values()]
        relations = self.extract_relations(*enriched_sentences)
        sentence = self._get_sentence(enriched_sentences[0])

        return relations, sentence

    def _is_relevant_article(self, article):
        """
        Override ArticleProcessingMixin's relevance criterion.
        """
        return len(article["data"]) > 0

    def _is_relevant_sentence(self, sentence):
        """
        Override ArticleProcessingMixin's relevance criterion.
        """
        # Separate sentence from sentence ID
        sentence = list(sentence.values())[0]
        return len(sentence["data"]["relations"]) > 0

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
        if dependency_tree["nodes"]["0"]["word"] is None:
            del dependency_tree["nodes"]["0"]

        dependency_tree["nodes"] = {int(address): node for address, node in dependency_tree["nodes"].items()}
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

        if len(pos_tagged_line) == 0 and len(dependency_tree["nodes"]) == 1:
            return verb_nodes

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

    def extract_relations(self, ne_tagged_line, dependency_tree, pos_tagged_line):
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
