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
    READING_TASK, NER_TASK
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
        return [self.naive_tag_rule(token, tokenized_sentence) for token in tokenized_sentence]


class SimpleReadingTaskTestCase(unittest.TestCase):
    """
    Testing the SimpleReadingTask.
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
    Testing the NERTask.
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
    # TODO (Implement) [DU 20.06.17]
    pass


class PoSTaggingTaskTestCase(unittest.TestCase):
    # TODO (Implement) [DU 20.06.17]
    pass


class NaiveOpenRelationExtractionTestCase(unittest.TestCase):
    # TODO (Implement) [DU 20.06.17]
    pass


class ParticipationExtractionTaskTestCase(unittest.TestCase):
    # TODO (Implement) [DU 20.06.17]
    pass
