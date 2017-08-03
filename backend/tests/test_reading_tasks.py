# STD
import json
import unittest
from unittest import mock as mock

# PROJECT
from bwg.french_wikipedia.french_wikipedia_config import FRENCH_WIKIPEDIA_ARTICLE_TAG_PATTERN
from bwg.tasks.reading_tasks import SimpleReadingTask
from tests.fixtures import READING_TASK
from tests.toolkit import MockInput, MockOutput


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

    @mock.patch('bwg.tasks.reading_tasks.SimpleReadingTask.output')
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