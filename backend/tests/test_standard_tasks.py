# -*- coding: utf-8 -*-
"""
Testing standard tasks for the NLP pipeline.
"""

# STD
import codecs
import unittest
import unittest.mock as mock

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


class NERTaskTestCase(unittest.TestCase):
    # TODO (Implement) [DU 20.06.17]
    pass


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
