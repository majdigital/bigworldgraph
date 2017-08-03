# -*- coding: utf-8 -*-
"""
Defining standard tasks for the NLP pipeline.
"""

# STD
import collections

# EXT
import luigi
import luigi.format

# PROJECT
from bwg.decorators import time_function
from bwg.mixins import ArticleProcessingMixin
from bwg.serializing import (
    serialize_relation
)
from bwg.tasks.dependency_parsing import DependencyParseTask
from bwg.tasks.ner import NERTask
from bwg.tasks.pos_tagging import PoSTaggingTask


class NaiveOpenRelationExtractionTask(luigi.Task, ArticleProcessingMixin):
    """
    Luigi task that performs Open Relation extraction on a corpus.
    """
    def requires(self):
        return NERTask(task_config=self.task_config), \
               DependencyParseTask(task_config=self.task_config), \
               PoSTaggingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["ORE_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input()[0].open("r") as nes_input_file, self.input()[1].open("r") as dependency_input_file,\
         self.input()[2].open("r") as pos_input_file, self.output().open("w") as output_file:
            for nes_line, dependency_line, pos_line in zip(nes_input_file, dependency_input_file, pos_input_file):
                self.process_articles(
                    (nes_line, dependency_line, pos_line), new_state="extracted_relations",
                    serializing_function=serialize_relation, output_file=output_file
                )

    def task_workflow(self, article, **workflow_resources):
        article_meta, article_data = article["meta"], article["data"]

        for sentence_id, sentence_json in article_data.items():
            sentence_dates = sentence_json["data"]
            relations, sentence = self._extract_relations_from_sentence(sentence_dates, **workflow_resources)

            serializing_arguments = {
                "sentence_id": sentence_id,
                "sentence": sentence,
                "relations": relations,
                "infix": "ORE"
            }

            yield serializing_arguments

    def _extract_relations_from_sentence(self, sentence_dates, **workflow_resources):
        """
        Extract all relation from a sentence.

        :param sentence_dates: Sentence's NE, PoS and dependency data.
        :type sentence_dates: dict
        :param workflow_resources: Additional resources for this step.
        :type workflow_resources: dict
        :return: All relationships and the raw sentence.
        :rtype: tuple
        """
        enriched_sentences = [sentence_date["data"] for sentence_date in sentence_dates.values()]
        relations = self.extract_relations(*enriched_sentences)
        sentence = self._get_sentence(enriched_sentences[0])

        return relations, sentence

    @staticmethod
    def _get_sentence(ne_tagged_line):
        """
        Get the original (not de-tokenized) sentence from a line tagged with NE tags.

        :param ne_tagged_line: Sentence with Named Entity tags.
        :type ne_tagged_line: list
        :return: Raw sentence.
        :rtype: str
        """
        return " ".join([word for word, tag in ne_tagged_line])

    def _align_tagged_sentence(self, ne_tagged_sentence):
        """
        Align a NE tagged sentence with a dependency parse by omitting pre-defined punctuation marks.

        :param ne_tagged_sentence: Sentence with Named Entity tags to be aligned.
        :type ne_tagged_sentence: list
        :return: Aligned sentence.
        :rtype: list
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

        :param dependency_tree: Dependency tree to be normalized.
        :type dependency_tree: dict
        :return: Normalized tree.
        :rtype: dict
        """
        # Delete graph's root node without word
        if "0" in dependency_tree["nodes"]:
            if dependency_tree["nodes"]["0"]["word"] in (None, "ROOT"):
                del dependency_tree["nodes"]["0"]
        elif 0 in dependency_tree["nodes"]:
            if dependency_tree["nodes"][0]["word"] in (None, "ROOT"):
                del dependency_tree["nodes"][0]
        else:
            # Empty tree
            return dependency_tree

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

        :param dependency_tree: Dependency parse tree.
        :type dependency_tree: dict
        :param pos_tagged_line: Same sentence as dependency parse tree but with PoS tags.
        :type pos_tagged_line: list
        :return: List of all verb nodes in this dependency parse tree.
        :rtype: list
        """
        verb_node_pos_tags = self.task_config["VERB_NODE_POS_TAGS"]
        verb_nodes = []

        if len(pos_tagged_line) == 0 or len(dependency_tree["nodes"]) == 1:
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

        :param node: Node to be expanded.
        :type node: dict
        :param dependency_tree: Dependency parse tree.
        :type dependency_tree: dict
        :param is_verb_node: Flag to indicate whether the current node is a verb node (the node shouldn't be expanded
        to its subject and object):
        :type is_verb_node: bool
        :return: Expanded node.
        :rtype: dict
        """
        expanded_node = [(node["address"], node["word"])]

        for dependency in node["deps"]:
            if dependency == "rel":
                continue

            # Ignore noun and object phrases
            if is_verb_node and dependency in ("nsubj", "dobj"):
                continue

            for address in node["deps"][dependency]:
                expanded_node.extend(self._expand_node(dependency_tree["nodes"][address], dependency_tree, is_verb_node))

        return expanded_node

    def _word_is_ne_tagged(self, word_index, ne_tagged_line):
        """
        Check if a word is Named Entity tagged.

        :param word_index: Index of word in current sentence.
        :type word_index: int
        :param ne_tagged_line: Current NE tagged sentence.
        :type ne_tagged_line: list
        :return: Result of check.
        :rtype: bool
        """
        word, ne_tag = ne_tagged_line[word_index]
        return ne_tag in self.task_config["NER_TAGSET"]

    def _expanded_node_is_ne_tagged(self, expanded_node, ne_tagged_line):
        """
        Check if a word within an expanded node was assigned a Named Entity tag.

        :param expanded_node: Expanded node to be checked.
        :type expanded_node: dict
        :param ne_tagged_line: Current NE tagged sentence.
        :type ne_tagged_line: list
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

        :param expanded_node: Expanded node to be joined.
        :type expanded_node: list
        :return: Joined node.
        :rtype: str
        """
        sorted_expanded_node = sorted(expanded_node, key=lambda x: x[0])
        return " ".join([word for address, word in sorted_expanded_node])

    @staticmethod
    def _get_subj_and_obj(verb_node, dependency_tree):
        """
        Get the adjacent subject and object node from a verb node.

        :param verb_node: Verb node subject and object should be found for.
        :type verb_node: dict
        :param dependency_tree: Dependency parse tree.
        :type dependency_tree: dict
        :return: Subject and object node.
        :rtype: tuple
        """
        subj_node_index = verb_node["deps"]["nsubj"][0]
        subj_node = dependency_tree["nodes"][subj_node_index]
        obj_node_index = verb_node["deps"]["dobj"][0]
        obj_node = dependency_tree["nodes"][obj_node_index]

        return subj_node, obj_node

    def extract_relations(self, ne_tagged_line, dependency_tree, pos_tagged_line):
        """
        Extract relations involving Named Entities from a sentence, using a dependency graph and named entity tags.

        :param ne_tagged_line: Current NE tagged sentence.
        :type ne_tagged_line: list
        :param dependency_tree: Dependency parse tree.
        :type dependency_tree: dict
        :param pos_tagged_line: Same sentence as dependency parse tree but with PoS tags.
        :type pos_tagged_line: list
        :return: List of extracted relations.
        :rtype: list
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

            # TODO (FEATURE): Extend definition of verb nodes? (Allow more patterns) [DU 18.04.17]
            # At the moment, the simple extraction heuristic ist just the following:
            # 1.) Find all verb nodes in a dependency tree
            # 2.) Find subject and object of that verb
            # 3.) Check if they are tagged with a Named Entity Tag
            # 4.) If one of them is tagged, extract the hold phrase as a relation triplet
            #
            # Possible improvements
            # - Use Machine Learning to learn patterns from pre-annotated corpus
            # - Alternatively, come up with more sophisticated rules manually
            # - Only extract relevant relationships
            # - Only extract the relevant parts of a relationship

            if self._expanded_node_is_ne_tagged(expanded_subj_node, aligned_ne_tagged_line) or \
               self._expanded_node_is_ne_tagged(expanded_obj_node, aligned_ne_tagged_line):
                    subj_phrase = self._join_expanded_node(expanded_subj_node)
                    obj_phrase = self._join_expanded_node(expanded_obj_node)
                    extracted_relations.append((subj_phrase, verb_node["word"], obj_phrase))

        return extracted_relations


