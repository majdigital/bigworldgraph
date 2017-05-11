# -*- coding: utf-8 -*-
"""
Defining standard tasks for the NLP pipeline.
"""

# STD
import codecs
import collections
import re

# EXT
import luigi
import luigi.format
from nltk.parse.stanford import StanfordDependencyParser
from nltk.tag.stanford import StanfordNERTagger, StanfordPOSTagger
from nltk.tokenize.stanford import StanfordTokenizer

# PROJECT
from bwg.helpers import time_function
from bwg.mixins import ArticleProcessingMixin
from bwg.utilities import (
    serialize_dependency_parse_tree,
    serialize_tagged_sentence,
    serialize_relation,
    get_nes_from_sentence,
    serialize_article
)
from bwg.wikipedia_tasks import WikipediaReadingTask


class SimpleReadingTask(luigi.Task):
    """
    A luigi task that reads an extracted Wikipedia corpus (see README).
    """
    task_config = luigi.DictParameter()

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["SIMPLE_READING_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        corpus_inpath = self.task_config["CORPUS_INPATH"]
        corpus_encoding = self.task_config["CORPUS_ENCODING"]

        # Init "parsing" variables
        current_title = ""
        current_id = ""
        current_url = ""
        current_sentences = []
        skip_line = False
        comment = False

        with codecs.open(corpus_inpath, "r", corpus_encoding) as input_file, self.output().open("w") as output_file:
            for line in input_file.readlines():
                line = line.strip()

                # Skip lines that should be ignored (article headers withing the article, xml comments, etc.)
                if skip_line:
                    if not comment or "-->" in line:
                        comment = False
                        skip_line = False
                    continue

                # Skip line if line is the title (title is already given in the <doc> tag)
                if line == current_title:
                    continue

                # Identify xml/html comments
                if "<!--" in line:
                    if "-->" not in line:
                        skip_line = True
                        comment = True
                    continue

                # Identify beginning of new article
                if re.match(self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"], line):
                    current_id, current_url, current_title = self._extract_article_info(line)

                # Identify end of article
                elif line.strip() == "</doc>":
                    self._output_article(
                        current_id, current_url, current_title, current_sentences, output_file, state="parsed"
                    )
                    current_title, current_id, current_url, current_sentences = self._reset_vars()

                # Just add a new line to ongoing article
                else:
                    if not line.strip():
                        continue

                    # Apply additional formatting to line if an appropriate function is given
                    line = re.sub("</?.+?>", "", line)  # Remove other xml markup
                    current_sentences.append(line)

    def _output_article(self, id_, url, title, sentences, output_file, **additional):
        """
        Write read article to file.

        :param id_: Article ID.
        :type id_: int
        :param url: URL of current article.
        :type url: str
        :param title: Title of current article.
        :type title: str
        :param sentences: Article sentences. 
        :type sentences: list
        :param output_file: Output file the article is written to.
        :type output_file: _io.TextWrapper
        :param additional: Additional parameters for serialization.
        :type additional: dict
        """
        article_json = serialize_article(
            id_, url, title, sentences, **additional
        )
        output_file.write("{}\n".format(article_json))

    @staticmethod
    def _reset_vars():
        """
        Reset temporary variables used while reading the input corpus.

        :return: Reset variables.
        :rtype: tuple
        """
        return "", "", "", []

    def _extract_article_info(self, line):
        """
        Extract important information from the opening article XML tag.

        :param line: Line with article information.
        :type line: str
        :return: Information about article.
        :rtype: tuple
        """
        article_tag_pattern = self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"]
        groups = re.match(article_tag_pattern, line).groups()
        return groups


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

    @time_function(is_classmethod=True)
    def run(self):
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_articles(
                    line, new_state="ne_tagged", serializing_function=serialize_tagged_sentence, output_file=output_file
                )

    @property
    def workflow_resources(self):
        stanford_models_path = self.task_config["STANFORD_MODELS_PATH"]
        stanford_ner_model_path = self.task_config["STANFORD_NER_MODEL_PATH"]
        corpus_encoding = self.task_config["CORPUS_ENCODING"]

        tokenizer = StanfordTokenizer(stanford_models_path, encoding=corpus_encoding)
        ner_tagger = StanfordNERTagger(stanford_ner_model_path, stanford_models_path, encoding=corpus_encoding)

        workflow_resources = {
            "tokenizer": tokenizer,
            "ner_tagger": ner_tagger
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

        :param sentence_data: Data of the sentence that is going to be named entity tagged.
        :type sentence_data: dict
        :param workflow_resources: Additional resources for this step.
        :type workflow_resources: dict
        :return: Processed sentence.
        :rtype: dict
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

    @time_function(is_classmethod=True)
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
        stanford_dependency_model_path = self.task_config["STANFORD_DEPENDENCY_MODEL_PATH"]
        stanford_corenlp_models_path = self.task_config["STANFORD_CORENLP_MODELS_PATH"]

        dependency_parser = StanfordDependencyParser(
            stanford_dependency_model_path, stanford_corenlp_models_path, encoding=corpus_encoding
        )

        workflow_resources = {
            "dependency_parser": dependency_parser
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

        :param sentence_data: Data of the sentence that is going to be dependency parsed.
        :type sentence_data: dict
        :param workflow_resources: Additional resources for this step.
        :type workflow_resources: dict
        :return: Processed sentence.
        :rtype: dict
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

    @time_function(is_classmethod=True)
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
        stanford_postagger_path = self.task_config["STANFORD_POSTAGGER_PATH"]
        stanford_models_path = self.task_config["STANFORD_MODELS_PATH"]
        stanford_pos_model_path = self.task_config["STANFORD_POS_MODEL_PATH"]

        tokenizer = StanfordTokenizer(stanford_models_path, encoding=corpus_encoding)
        pos_tagger = StanfordPOSTagger(
            stanford_pos_model_path, path_to_jar=stanford_postagger_path, encoding=corpus_encoding
        )

        workflow_resources = {
            "tokenizer": tokenizer,
            "pos_tagger": pos_tagger
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

        Tag a single sentence with Part-of-Speech tags using a Stanford CoreNLP server.

        :param sentence_data: Data of the sentence that is going to be pos tagged.
        :type sentence_data: dict
        :param workflow_resources: Additional resources for this step.
        :type workflow_resources: dict
        :return: Processed sentence.
        :rtype: dict
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
        :type ne_tagged_line: str
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
            if is_verb_node and dependency in ("nsub", "dobj"):
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
        :type expanded_node: dict
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

            if self._expanded_node_is_ne_tagged(expanded_subj_node, aligned_ne_tagged_line) or \
               self._expanded_node_is_ne_tagged(expanded_obj_node, aligned_ne_tagged_line):
                    subj_phrase = self._join_expanded_node(expanded_subj_node)
                    obj_phrase = self._join_expanded_node(expanded_obj_node)
                    extracted_relations.append((subj_phrase, verb_node["word"], obj_phrase))

        return extracted_relations


class ParticipationExtractionTask(luigi.Task, ArticleProcessingMixin):
    """
    Luigi task that extracts all Named Entity participating in an issue or topic.
    """
    def requires(self):
        return NERTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["PE_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input().open("r") as nes_input_file, self.output().open("w") as output_file:
            for nes_line in nes_input_file:
                self.process_articles(
                    nes_line, new_state="extracted_participations",
                    serializing_function=serialize_relation, output_file=output_file
                )

    def task_workflow(self, article, **workflow_resources):
        article_meta, article_data = article["meta"], article["data"]
        article_title = article_meta["title"]
        participation_phrases = self.task_config["PARTICIPATION_PHRASES"]
        default_ne_tag = self.task_config["DEFAULT_NE_TAG"]

        for sentence_id, sentence_json in article_data.items():
            nes = get_nes_from_sentence(sentence_json["data"], default_ne_tag, True)
            relations = self._build_participation_relations(nes, article_title, participation_phrases)
            sentence = self._get_sentence(sentence_json["data"])

            serializing_arguments = {
                "sentence_id": sentence_id,
                "sentence": sentence,
                "relations": relations,
                "infix": "PE"
            }

            yield serializing_arguments

    @staticmethod
    def _build_participation_relations(nes, title, participation_phrases):
        """
        Build participation relations based on the Named entities in a sentence, the current articles titles and a
        dictionary of specific phrases for each Named entity tag.

        :param nes: List of named entities in the current sentence.
        :type nes: list
        :param title: Title of current article.
        :type title: str
        :param participation_phrases: Dictionary of participation phrases for different Named Entity tags.
        :type participation_phrases: dict
        :return: List of participation relations.
        :rtype: list
        """
        return [
            (ne, participation_phrases.get(tag, participation_phrases["DEFAULT"]), title) for ne, tag in nes
        ]

    @staticmethod
    def _get_sentence(sentence_data):
        """
        Get the original (not de-tokenized) sentence from a line tagged with NE tags.

        :param sentence_data: Sentence with Named Entity tags.
        :type sentence_data: list
        :return: Raw sentence.
        :rtype: str
        """
        return " ".join([word for word, ne_tag in sentence_data])
