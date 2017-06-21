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
from bwg.standard_tasks import (
    SimpleReadingTask, NERTask, DependencyParseTask, PoSTaggingTask, NaiveOpenRelationExtractionTask,
    ParticipationExtractionTask
)
from .toolkit import MockInput, MockOutput, mock_class_method
from .fixtures import READING_TASK
from bwg.pipeline_config import FRENCH_WIKIPEDIA_ARTICLE_TAG_PATTERN


class SimpleReadingTaskTestCase(unittest.TestCase):

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
    def setUp(self):
        task_config = {

        }


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
