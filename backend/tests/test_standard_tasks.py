# -*- coding: utf-8 -*-
"""
Testing standard tasks for the NLP pipeline.
"""

# STD
import codecs
import unittest
import unittest.mock as mock
import json

# PROJECT
import bwg
from bwg.standard_tasks import (
    SimpleReadingTask, NERTask, DependencyParseTask, PoSTaggingTask, NaiveOpenRelationExtractionTask,
    ParticipationExtractionTask
)
from .toolkit import MockInput, MockOutput, mock_class_method
from .fixtures import (
    READING_TASK, NER_TASK, DEPENDENCY_TASK, POS_TAGGING_TASK
)
from bwg.pipeline_config import FRENCH_WIKIPEDIA_ARTICLE_TAG_PATTERN


class MockTokenizer:
    @staticmethod
    def tokenize(sentence_data):
        return sentence_data.split(" ")


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
        assert ner_tagged_sentence == [
            ("this", "O"), ("pineapple", "I-P"), ("is", "O"), ("part", "O"), ("of", "O"), ("a", "O"), ("sample", "I-N"),
            ("sentence", "O"), ("in", "O"), ("an", "O"), ("article", "I-N")
        ]


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
    # TODO (Implement) [DU 20.06.17]
    pass


class ParticipationExtractionTaskTestCase(unittest.TestCase):
    """
    Testing ParticipationExtractionTask.
    """
    # TODO (Implement) [DU 20.06.17]
    pass
