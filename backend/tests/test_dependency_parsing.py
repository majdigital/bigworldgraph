# STD
import json
import unittest
from unittest import mock as mock

# PROJECT
import bwg
from tests.fixtures import DEPENDENCY_TASK
from tests.mock_nlp import MockParser
from tests.toolkit import MockOutput, MockInput


class DependencyParseTaskTestCase(unittest.TestCase):
    """
    Testing DependencyParseTask.
    """
    @mock.patch('bwg.tasks.dependency_parsing.DependencyParseTask.output')
    @mock.patch('bwg.tasks.dependency_parsing.DependencyParseTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
                "bwg.tasks.dependency_parsing.DependencyParseTask.workflow_resources", new_callable=mock.PropertyMock()
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

            task = bwg.tasks.dependency_parsing.DependencyParseTask(task_config=task_config)

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