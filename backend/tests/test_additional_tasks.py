# -*- coding: utf-8 -*-
"""
Testing standard tasks for the NLP pipeline.
"""

# Avoid Pywikibot exception
import os
os.environ["PYWIKIBOT2_DIR"] = "../bwg/user-config.py"
os.environ["PYWIKIBOT2_NO_USER_CONFIG"] = "1"

# STD
import unittest
import unittest.mock as mock
import json
import copy

# PROJECT
import bwg
from bwg.additional_tasks import (
   RelationMergingTask, PipelineRunInfoGenerationTask, RelationsDatabaseWritingTask
)
from tests.toolkit import MockInput, MockOutput
from tests.fixtures import (
    RELATION_MERGING_TASK, RELATIONS_DATABASE_WRITING_TASK, PIPELINE_RUN_INFO_GENERATION_TASK
)


class RelationMergingTaskTestCase(unittest.TestCase):
    """
    Test RelationMergingTask.
    """
    @mock.patch('bwg.additional_tasks.RelationMergingTask.output')
    @mock.patch('bwg.additional_tasks.RelationMergingTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
                "bwg.additional_tasks.RelationMergingTask.workflow_resources", new_callable=mock.PropertyMock()
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

            task = bwg.additional_tasks.RelationMergingTask(task_config=task_config)

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


class PipelineRunInfoGenerationTaskTestCase(unittest.TestCase):
    """
    Test PipelineRunInfoGenerationTask.
    """
    @mock.patch('bwg.additional_tasks.PipelineRunInfoGenerationTask.output')
    @mock.patch('bwg.additional_tasks.PipelineRunInfoGenerationTask.input')
    def test_task_functions(self, input_patch, output_patch):
            task_config = {
                "CORPUS_ENCODING": "",
                "PIPELINE_RUN_INFO_OUTPUT_PATH": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = MockInput(PIPELINE_RUN_INFO_GENERATION_TASK["input"])

            task = bwg.additional_tasks.RelationMergingTask(task_config=task_config)

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


class RelationsDatabaseWritingTaskTestCase(unittest.TestCase):
    """
    Test RelationsDatabaseWritingTask.
    """
    @mock.patch('bwg.additional_tasks.RelationsDatabaseWritingTask.output')
    @mock.patch('bwg.additional_tasks.RelationsDatabaseWritingTask.input')
    def test_task_functions(self, input_patch, output_patch):
        task_config = {
            "NEO4J_USER": "",
            "NEO4J_PASSWORD": "",
            "NEO4J_HOST": "",
            "DATABASE_CATEGORIES": {},
            "CORPUS_ENCODING": ""
        }

        output_patch.return_value = MockOutput()
        input_patch.return_value = MockInput(RELATIONS_DATABASE_WRITING_TASK["input"])

        task = bwg.additional_tasks.RelationsDatabaseWritingTask(task_config=task_config)

        # Testing
        self._test_process_article(task)
        self._test_read_properties_file(task)
        self._test_extract_properties(task)
        self._test_add_entity_data_to_properties_dict(task)
        self._test_convert_entity_sense(task)
        self._test_rename_field()
        self._test_read_pipeline_run_info(task)
        self._test_is_relevant(task)
        self._test_is_relevant_node(task)
        self._test_categorize_node(task)

    @staticmethod
    def _test_process_article(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_read_properties_file(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_extract_properties(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_add_entity_data_to_properties_dict(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_convert_entity_sense(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_rename_field():
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_read_pipeline_run_info(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_is_relevant(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_is_relevant_node(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def _test_categorize_node(task):
        # TODO (Implement) [DU 28.07.17]s
        pass
