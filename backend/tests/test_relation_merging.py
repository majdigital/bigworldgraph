# STD
import unittest
from unittest import mock as mock

# PROJECT
import bwg
from tests.fixtures import RELATION_MERGING_TASK
from tests.toolkit import MockOutput, MockInput


class RelationMergingTaskTestCase(unittest.TestCase):
    """
    Test RelationMergingTask.
    """
    @mock.patch('bwg.tasks.relation_merging.RelationMergingTask.output')
    @mock.patch('bwg.tasks.relation_merging.RelationMergingTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
            "bwg.tasks.relation_merging.RelationMergingTask.workflow_resources", new_callable=mock.PropertyMock()
        ) as workflow_mock:
            task_config = {
                "CORPUS_ENCODING": "",
                "RELATION_MERGING_OUTPUT_PATH": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = (
                MockInput(RELATION_MERGING_TASK["input"][0]),
                MockInput(RELATION_MERGING_TASK["input"][0])
            )
            workflow_mock.__get__ = mock.Mock(return_value={})

            task = bwg.tasks.relation_merging.RelationMergingTask(task_config=task_config)

            # Testing
            self._test_get_relations_from_sentence_json()
            self._test_is_relevant_article(task)
            self._test_is_relevant_sentence(task)

    @staticmethod
    def _test_get_relations_from_sentence_json():
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_is_relevant_article(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_is_relevant_sentence(task):
        # TODO (Implement) [DU 28.07.17]
        pass