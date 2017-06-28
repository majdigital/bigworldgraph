# -*- coding: utf-8 -*-
"""
Testing standard tasks for the NLP pipeline.
"""

# STD
import unittest
import unittest.mock as mock
import json
import copy

# PROJECT
import bwg
from bwg.standard_tasks import (
    SimpleReadingTask, NaiveOpenRelationExtractionTask,
    ParticipationExtractionTask
)
from tests.toolkit import MockInput, MockOutput
from tests.fixtures import (
    READING_TASK, NER_TASK, DEPENDENCY_TASK, POS_TAGGING_TASK, NAIVE_OPEN_RELATION_EXTRACTION_TASK,
    PARTICIPATION_EXTRACTION_TASK, DEPENDENCY_TREE
)
from bwg.pipeline_config import FRENCH_WIKIPEDIA_ARTICLE_TAG_PATTERN
from bwg.utilities import get_nes_from_sentence

# CONSTANTS
NE_TAGGED_PINEAPPLE_SENTENCE = [
    ("this", "O"), ("pineapple", "I-P"), ("is", "O"), ("part", "O"), ("of", "O"), ("a", "O"), ("sample", "I-N"),
    ("sentence", "O"), ("in", "O"), ("an", "O"), ("article", "I-N")
]
NE_DEPENDEMCY_PINEAPPLE_TREE = {
    "nodes": {
        0: {
            "address": 0,
            "word": "pineapples",
            "deps": {}
        },
        1: {
            "address": 1,
            "word": "are",
            "deps": {
                "nsubj": [0],
                "dobj": [3]
            }
        },
        2: {
            "address": 2,
            "word": "juicy",
            "deps": {}
        },
        3: {
            "address": 3,
            "word": "fruits",
            "deps": {"adj": [2]}
        }
    },
    "root": 2
}


class MockTokenizer:
    @staticmethod
    def tokenize(sentence_data):
        return sentence_data.split(" ")  # Yes, yes, very sophisticated


class MockTagger:
    def __init__(self, naive_tag_rule):
        assert callable(naive_tag_rule)
        self.naive_tag_rule = naive_tag_rule

    def tag(self, tokenized_sentence):
        return [self.naive_tag_rule(token.lower(), tokenized_sentence) for token in tokenized_sentence]


class MockParser:
    @staticmethod
    def raw_parse(sentence_data):
        tokens = sentence_data.split(" ")

        return {
            "root": {
                "address": 0
            },
            "nodes": {
                node_id: {
                    "address": node_id,
                    "word": "ROOT" if node_id == 0 else tokens[node_id - 1],
                    "rel": None if node_id == 0 else node_id - 1,
                    "deps": {
                        "rel": node_id + 1
                    }
                }
                for node_id in range(len(tokens) + 1)
            }
        }


class SimpleReadingTaskTestCase(unittest.TestCase):
    """
    Testing SimpleReadingTask.
    """
    def setUp(self):
        task_config = {
            "CORPUS_INPATH": "",
            "CORPUS_ENCODING": "",
            "SIMPLE_READING_OUTPUT_PATH": "",
            "WIKIPEDIA_ARTICLE_TAG_PATTERN": FRENCH_WIKIPEDIA_ARTICLE_TAG_PATTERN
        }

        self.task = SimpleReadingTask(task_config=task_config)

    @mock.patch('bwg.standard_tasks.SimpleReadingTask.output')
    @mock.patch('codecs.open')
    def test_task(self, open_patch, output_patch):
        open_patch.return_value = MockInput(READING_TASK["input"])
        output_patch.return_value = MockOutput()
        self.task.run()
        output_mock = output_patch()
        assert [json.loads(content, encoding="utf-8") for content in output_mock.contents] == READING_TASK["output"]

    def test_extract_article_info(self):
        article_info_line = '<doc id="12345" url="https://web.site" title="Sample article">'
        assert self.task._extract_article_info(article_info_line) == ("12345", "https://web.site", "Sample article")


class NERTaskTestCase(unittest.TestCase):
    """
    Testing NERTask.
    """
    @mock.patch('bwg.standard_tasks.NERTask.output')
    @mock.patch('bwg.standard_tasks.NERTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
            "bwg.standard_tasks.NERTask.workflow_resources", new_callable=mock.PropertyMock()
        ) as workflow_mock:

            task_config = {
                "STANFORD_MODELS_PATH": "",
                "STANFORD_NER_MODEL_PATH": "",
                "CORPUS_ENCODING": "",
                "WIKIPEDIA_READING_OUTPUT_PATH": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = MockInput(NER_TASK["input"])
            workflow_mock.__get__ = mock.Mock(
                return_value={
                    "tokenizer": MockTokenizer(),
                    "ner_tagger": MockTagger(self.naive_ner_tag)
                }
            )

            task = bwg.standard_tasks.NERTask(task_config=task_config)

            # Testing
            self._test_task(task)
            self._test_ner_tag(task)

    @staticmethod
    def naive_ner_tag(token, tokenized_sentence):
        tag_rules = {
            "sample": "I-N",
            "article": "I-N",
            "pineapple": "I-P"
        }

        if token in tag_rules:
            return token, tag_rules[token]
        return token, "O"

    @staticmethod
    def _test_task(task):
        task.run()
        output_mock = task.output()
        assert [json.loads(content, encoding="utf-8") for content in output_mock.contents] == NER_TASK["output"]

    @staticmethod
    def _test_ner_tag(task):
        sentence_data = "this pineapple is part of a sample sentence in an article"
        ner_tagged_sentence = task._ner_tag(sentence_data, **task.workflow_resources)
        assert ner_tagged_sentence == NE_TAGGED_PINEAPPLE_SENTENCE


class DependencyParseTaskTestCase(unittest.TestCase):
    """
    Testing DependencyParseTask.
    """
    @mock.patch('bwg.standard_tasks.DependencyParseTask.output')
    @mock.patch('bwg.standard_tasks.DependencyParseTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
                "bwg.standard_tasks.DependencyParseTask.workflow_resources", new_callable=mock.PropertyMock()
        ) as workflow_mock:
            task_config = {
                "STANFORD_DEPENDENCY_MODEL_PATH": "",
                "STANFORD_CORENLP_MODELS_PATH": "",
                "CORPUS_ENCODING": "",
                "DEPENDENCY_OUTPUT_PATH": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = MockInput(DEPENDENCY_TASK["input"])
            workflow_mock.__get__ = mock.Mock(
                return_value={
                    "dependency_parser": MockParser()
                }
            )

            task = bwg.standard_tasks.DependencyParseTask(task_config=task_config)

            # Testing
            self._test_task(task)
            self._test_dependency_parse(task)

    @staticmethod
    def _test_task(task):
        task.run()
        output_mock = task.output()
        assert [json.loads(content, encoding="utf-8") for content in output_mock.contents] == DEPENDENCY_TASK["output"]

    @staticmethod
    def _test_dependency_parse(task):
        sentence_data = "this pineapple is a sentence"
        dependency_parsed_sentence = task._dependency_parse(sentence_data, **task.workflow_resources)
        assert dependency_parsed_sentence == {
            "root": {"address": 0},
            "nodes": {
                0: {
                    "address": 0,
                    "word": "ROOT",
                    "rel": None,
                    "deps": {"rel": 1}
                },
                1: {
                    "address": 1,
                    "word": "this",
                    "rel": 0,
                    "deps": {"rel": 2}
                },
                2: {
                    "address": 2,
                    "word": "pineapple",
                    "rel": 1,
                    "deps": {"rel": 3}
                },
                3: {
                    "address": 3,
                    "word": "is",
                    "rel": 2,
                    "deps": {"rel": 4}
                },
                4: {
                    "address": 4,
                    "word": "a",
                    "rel": 3,
                    "deps": {"rel": 5}
                },
                5: {
                    "address": 5,
                    "word": "sentence",
                    "rel": 4,
                    "deps": {"rel": 6}
                }
            }
        }


class PoSTaggingTaskTestCase(unittest.TestCase):
    """
    Testing PoSTaggingTask.
    """
    @mock.patch('bwg.standard_tasks.PoSTaggingTask.output')
    @mock.patch('bwg.standard_tasks.PoSTaggingTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
                "bwg.standard_tasks.PoSTaggingTask.workflow_resources", new_callable=mock.PropertyMock()
        ) as workflow_mock:
            task_config = {
                "STANFORD_POSTAGGER_PATH": "",
                "STANFORD_MODELS_PATH": "",
                "STANFORD_POS_MODEL_PATH": "",
                "CORPUS_ENCODING": "",
                "POS_OUTPUT_PATH": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = MockInput(POS_TAGGING_TASK["input"])
            workflow_mock.__get__ = mock.Mock(
                return_value={
                    "tokenizer": MockTokenizer(),
                    "pos_tagger": MockTagger(self.naive_pos_tag)
                }
            )

            task = bwg.standard_tasks.PoSTaggingTask(task_config=task_config)

            # Testing
            self._test_task(task)
            self._test_pos_tag(task)

    @staticmethod
    def naive_pos_tag(token, tokenized_sentence):
        tag_rules = {
            "sample": "ADJ",
            "article": "NN",
            "pineapple": "NN",
            "first": "ADJ",
            "sentence": "NN",
            "the": "DET",
            "second": "ADJ",
            "this": "DET",
            "is": "VV",
            "a": "DET"
        }

        if token in tag_rules:
            return token, tag_rules[token]
        return token, "UKW"

    @staticmethod
    def _test_task(task):
        task.run()
        output_mock = task.output()
        assert [json.loads(content, encoding="utf-8") for content in output_mock.contents] == POS_TAGGING_TASK["output"]

    @staticmethod
    def _test_pos_tag(task):
        sentence_data = "this pineapple is a sentence"
        pos_tagged_sentence = task._pos_tag(sentence_data, **task.workflow_resources)
        assert pos_tagged_sentence == [
            ("this", "DET"), ("pineapple", "NN"), ("is", "VV"), ("a", "DET"), ("sentence", "NN")
        ]


class NaiveOpenRelationExtractionTaskTestCase(unittest.TestCase):
    """
    Testing NaiveOpenRelatioNExtractionTask.
    """
    @mock.patch('bwg.standard_tasks.NaiveOpenRelationExtractionTask.output')
    @mock.patch('bwg.standard_tasks.NaiveOpenRelationExtractionTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
            "bwg.standard_tasks.NaiveOpenRelationExtractionTask.workflow_resources", new_callable=mock.PropertyMock()
        ) as workflow_mock:
            task_config = {
                "NER_TAGSET": ["I-P", "I-N"],
                "DEFAULT_NE_TAG": "O",
                "VERB_NODE_POS_TAGS": ["VV"],
                "OMITTED_TOKENS_FOR_ALIGNMENT": [],
                "CORPUS_ENCODING": "",
                "ORE_OUTPUT_PATH": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = (
                MockInput(NAIVE_OPEN_RELATION_EXTRACTION_TASK["input"][0]),
                MockInput(NAIVE_OPEN_RELATION_EXTRACTION_TASK["input"][1]),
                MockInput(NAIVE_OPEN_RELATION_EXTRACTION_TASK["input"][2])
            )
            workflow_mock.__get__ = mock.Mock(return_value={})

            task = bwg.standard_tasks.NaiveOpenRelationExtractionTask(task_config=task_config)

            # Testing
            self._test_task(task)
            self._test_extract_relations_from_sentence(task)
            self._test_get_sentence()
            self._test_align_tagged_sentence(task)
            self._test_normalize_node_addresses()
            self._test_extract_verb_nodes(task)
            self._test_expand_node(task)
            self._test_word_is_ne_tagged(task)
            self._test_join_expanded_node()
            self._test_get_subj_and_obj()
            self._test_extract_relations(task)

    @staticmethod
    def _test_task(task):
        task.run()
        output_mock = task.output()
        assert [json.loads(content, encoding="utf-8") for content in output_mock.contents] == \
               NAIVE_OPEN_RELATION_EXTRACTION_TASK["output"]

    @staticmethod
    def _test_extract_relations_from_sentence(task):
        ne_tagged_line = [("pineapples", "I-P"), ("are", "O"), ("juicy", "I-N"), ("fruits", "I-N")]
        pos_tagged_line = [("pineapples", "NN"), ("are", "VV"), ("juicy", "ADJ"), ("fruits", "NN")]
        dependency_tree = copy.deepcopy(NE_DEPENDEMCY_PINEAPPLE_TREE)
        sentence_dates = {
            "data_ne_tagged": {"data": ne_tagged_line},
            "data_dependency_parsed": {"data": dependency_tree},
            "data_pos_tagged": {"data": pos_tagged_line}
        }

        assert task._extract_relations_from_sentence(sentence_dates) == (
            [("pineapples", "are", "juicy fruits")], "pineapples are juicy fruits"
        )

    @staticmethod
    def _test_get_sentence():
        tagged_sentence = NE_TAGGED_PINEAPPLE_SENTENCE
        assert NaiveOpenRelationExtractionTask._get_sentence(tagged_sentence) == \
               "this pineapple is part of a sample sentence in an article"

    @staticmethod
    def _test_align_tagged_sentence(task):
        assert task._align_tagged_sentence(NE_TAGGED_PINEAPPLE_SENTENCE) == NE_TAGGED_PINEAPPLE_SENTENCE

        # TODO (Bug): Find a way to do this test [DU 22.06.17]
        #new_config = {"OMITTED_TOKENS_FOR_ALIGNMENT": [token for token, _ in NE_TAGGED_PINEAPPLE_SENTENCE]}
        #with mock.patch("bwg.standard_tasks.NaiveOpenRelationExtractionTask.task_config", return_value=new_config):
        #    assert task._align_tagged_sentence(NE_TAGGED_PINEAPPLE_SENTENCE) == []

    @staticmethod
    def _test_normalize_node_addresses():
        empty_tree = {"nodes": {}, "root": {}}
        assert NaiveOpenRelationExtractionTask._normalize_node_addresses(empty_tree) == empty_tree

        normalized_tree = NaiveOpenRelationExtractionTask._normalize_node_addresses(DEPENDENCY_TREE)
        assert normalized_tree["nodes"][0]["word"] not in (None, "ROOT")
        assert normalized_tree["root"]["word"] not in (None, "ROOT")

    @staticmethod
    def _test_extract_verb_nodes(task):
        dependency_tree = NE_DEPENDEMCY_PINEAPPLE_TREE
        pos_tagged_line = [("pineapples", "NN"), ("are", "VV"), ("juicy", "ADJ"), ("fruits", "NN")]

        assert task._extract_verb_nodes({"nodes": {}}, []) == []
        assert task._extract_verb_nodes(dependency_tree, pos_tagged_line) == [dependency_tree["nodes"][1]]

    @staticmethod
    def _test_expand_node(task):
        dependecy_tree = copy.deepcopy(NE_DEPENDEMCY_PINEAPPLE_TREE)
        fruits_node, verb_node = dependecy_tree["nodes"][3], dependecy_tree["nodes"][1]
        juicy_node = dependecy_tree["nodes"][2]
        assert task._expand_node(verb_node, dependecy_tree, is_verb_node=True) == [
            (verb_node["address"], verb_node["word"])
        ]
        assert task._expand_node(fruits_node, dependecy_tree) == [
            (fruits_node["address"], fruits_node["word"]), (juicy_node["address"], juicy_node["word"])
        ]

    @staticmethod
    def _test_word_is_ne_tagged(task):
        assert task._word_is_ne_tagged(0, [("word", "I-P")])
        assert task._word_is_ne_tagged(0, [("Another word", "I-N")])
        assert not task._word_is_ne_tagged(0, [("untagged word", "O")])

    @staticmethod
    def _test_expanded_node_is_ne_tagged(task):
        ne_tagged_line = [
            ("this", "O"), ("is", "O"), ("an", "I-N"), ("expanded", "I-N"), ("node", "I-N"), ("and", "O"), ("a", "I-P"),
            ("pineapple", "I-P")
        ]
        assert task._expanded_node_is_ne_tagged([(2, "an"), (3, "expanded"), (4, "node")], ne_tagged_line)
        assert task._expanded_node_is_ne_tagged([(6, "a"), (7, "pineapple")], ne_tagged_line)
        assert not task._expanded_node_is_ne_tagged([(0, "this"), (1, "is")], ne_tagged_line)

    @staticmethod
    def _test_join_expanded_node():
        assert NaiveOpenRelationExtractionTask._join_expanded_node([(6, "a"), (7, "pineapple")]) == "a pineapple"
        assert NaiveOpenRelationExtractionTask._join_expanded_node(
            [(3, "expanded"), (2, "an"), (4, "node")]
        ) == "an expanded node"
        assert NaiveOpenRelationExtractionTask._join_expanded_node([(5, "word")]) == "word"

    @staticmethod
    def _test_get_subj_and_obj():
        dependency_tree = copy.deepcopy(NE_DEPENDEMCY_PINEAPPLE_TREE)
        verb_node = dependency_tree["nodes"][1]
        subj_node, obj_node = dependency_tree["nodes"][0], dependency_tree["nodes"][3]
        assert NaiveOpenRelationExtractionTask._get_subj_and_obj(verb_node, dependency_tree) == (subj_node, obj_node)

    @staticmethod
    def _test_extract_relations(task):
        ne_tagged_line = [("pineapples", "I-P"), ("are", "O"), ("juicy", "I-N"), ("fruits", "I-N")]
        pos_tagged_line = [("pineapples", "NN"), ("are", "VV"), ("juicy", "ADJ"), ("fruits", "NN")]
        dependency_tree = copy.deepcopy(NE_DEPENDEMCY_PINEAPPLE_TREE)

        assert task.extract_relations(ne_tagged_line, dependency_tree, pos_tagged_line) == [
            ("pineapples", "are", "juicy fruits")
        ]


class ParticipationExtractionTaskTestCase(unittest.TestCase):
    """
    Testing ParticipationExtractionTask.
    """
    participation_phrases = {
        "I-P": "is pineappled with",
        "I-N": "is related with",
        "DEFAULT": "is boringly related with"
    }

    @mock.patch('bwg.standard_tasks.ParticipationExtractionTask.output')
    @mock.patch('bwg.standard_tasks.ParticipationExtractionTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
            "bwg.standard_tasks.ParticipationExtractionTask.workflow_resources",
            new_callable=mock.PropertyMock()
        ) as workflow_mock:
            task_config = {
                "DEFAULT_NE_TAG": "O",
                "PARTICIPATION_PHRASES": self.participation_phrases,
                "PE_OUTPUT_PATH": "",
                "CORPUS_ENCODING": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = MockInput(PARTICIPATION_EXTRACTION_TASK["input"])
            workflow_mock.__get__ = mock.Mock(return_value={})

            task = bwg.standard_tasks.ParticipationExtractionTask(task_config=task_config)

            # Testing
            self._test_task(task)
            self._test_build_participation_relations()
            self._test_get_sentence()

    @staticmethod
    def _test_task(task):
        task.run()
        output_mock = task.output()
        assert [json.loads(content, encoding="utf-8") for content in output_mock.contents] == \
               PARTICIPATION_EXTRACTION_TASK["output"]

    def _test_build_participation_relations(self):
        nes = get_nes_from_sentence(NE_TAGGED_PINEAPPLE_SENTENCE, "O", True)
        assert ParticipationExtractionTask._build_participation_relations(
            nes, "The pineapple affair", self.participation_phrases
        ) == [
            ('pineapple', 'is pineappled with', 'The pineapple affair'),
            ('sample', 'is related with', 'The pineapple affair')
        ]

    @staticmethod
    def _test_get_sentence():
        tagged_sentence = NE_TAGGED_PINEAPPLE_SENTENCE
        assert ParticipationExtractionTask._get_sentence(tagged_sentence) == \
               "this pineapple is part of a sample sentence in an article"
