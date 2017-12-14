# STD
import unittest
from unittest import mock as mock

# PROJECT
import bwg
from tests.fixtures import PIPELINE_RUN_INFO_GENERATION_TASK
from tests.toolkit import MockOutput, MockInput


class PipelineRunInfoGenerationTaskTestCase(unittest.TestCase):
    """
    Test PipelineRunInfoGenerationTask.
    """
    @mock.patch('bwg.tasks.pipeline_run_info_generation.PipelineRunInfoGenerationTask.output')
    @mock.patch('bwg.tasks.pipeline_run_info_generation.PipelineRunInfoGenerationTask.input')
    def test_task_functions(self, input_patch, output_patch):
            task_config = {
                "CORPUS_ENCODING": "",
                "PIPELINE_RUN_INFO_OUTPUT_PATH": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = MockInput(PIPELINE_RUN_INFO_GENERATION_TASK["input"])

            task = bwg.tasks.relation_merging.RelationMergingTask(task_config=task_config)

            # Testing
            self._test_generate_run_information(task)
            self._test_generate_run_hash()
            self._test_generate_timestamp()

    @staticmethod
    def _test_generate_run_information(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_generate_run_hash():
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_generate_timestamp():
        # TODO (Implement) [DU 28.07.17]
        pass