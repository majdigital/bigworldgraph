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
            self.test_get_relations_from_sentence_json()
            self.test_is_relevant_article(task)
            self.test_is_relevant_sentence(task)

    @staticmethod
    def test_get_relations_from_sentence_json():
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_is_relevant_article(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_is_relevant_sentence(task):
        # TODO (Implement) [DU 28.07.17]
        pass


class PipelineRunInfoGenerationTaskTestCase(unittest.TestCase):
    """
    Test PipelineRunInfoGenerationTask.
    """
    @mock.patch('bwg.additional_tasks.PipelineRunInfoGenerationTask.output')
    @mock.patch('bwg.additional_tasks.PipelineRunInfoGenerationTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
                "bwg.additional_tasks.PipelineRunInfoGenerationTask.workflow_resources",
                new_callable=mock.PropertyMock()
        ) as workflow_mock:
            task_config = {
                "CORPUS_ENCODING": "",
                "PIPELINE_RUN_INFO_OUTPUT_PATH": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = MockInput(PIPELINE_RUN_INFO_GENERATION_TASK["input"])
            workflow_mock.__get__ = mock.Mock(return_value={})

            task = bwg.additional_tasks.RelationMergingTask(task_config=task_config)

            # Testing
            self.test_generate_run_information(task)
            self.test_generate_run_hash()
            self.test_generate_timestamp()

    @staticmethod
    def test_generate_run_information(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_generate_run_hash():
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_generate_timestamp():
        # TODO (Implement) [DU 28.07.17]
        pass


class RelationsDatabaseWritingTaskTestCase(unittest.TestCase):
    """
    Test RelationsDatabaseWritingTask.
    """
    @mock.patch('bwg.additional_tasks.RelationsDatabaseWritingTask.output')
    @mock.patch('bwg.additional_tasks.RelationsDatabaseWritingTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
                "bwg.additional_tasks.RelationsDatabaseWritingTask.workflow_resources",
                new_callable=mock.PropertyMock()
        ) as workflow_mock:
            task_config = {
                "NEO4J_USER": "",
                "NEO4J_PASSWORD": "",
                "NEO4J_HOST": "",
                "DATABASE_CATEGORIES": {},
                "CORPUS_ENCODING": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = MockInput(RELATIONS_DATABASE_WRITING_TASK["input"])
            workflow_mock.__get__ = mock.Mock(return_value={})

            task = bwg.additional_tasks.RelationsDatabaseWritingTask(task_config=task_config)

            # Testing
            self.test_process_article(task)
            self.test_read_properties_file(task)
            self.test_extract_properties(task)
            self.test_add_entity_data_to_properties_dict(task)
            self.test_convert_entity_sense(task)
            self.test_rename_field()
            self.test_read_pipeline_run_info(task)
            self.test_is_relevant(task)
            self.test_is_relevant_node(task)
            self.test_categorize_node(task)

    @staticmethod
    def test_process_article(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_read_properties_file(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_extract_properties(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_add_entity_data_to_properties_dict(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_convert_entity_sense(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_rename_field():
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_read_pipeline_run_info(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_is_relevant(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_is_relevant_node(task):
        # TODO (Implement) [DU 28.07.17]
        pass

    @staticmethod
    def test_categorize_node(task):
        # TODO (Implement) [DU 28.07.17]s
        pass
