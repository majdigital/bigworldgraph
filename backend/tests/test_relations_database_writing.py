# -*- coding: utf-8 -*-
"""
Testing standard tasks for the NLP pipeline.
"""

# Avoid Pywikibot exception
import os

import bwg.tasks.relation_merging

os.environ["PYWIKIBOT2_DIR"] = "../bwg/user-config.py"
os.environ["PYWIKIBOT2_NO_USER_CONFIG"] = "1"

# STD
import unittest
import unittest.mock as mock

# PROJECT
import bwg
from tests.toolkit import MockInput, MockOutput
from tests.fixtures import (
    RELATIONS_DATABASE_WRITING_TASK
)


class RelationsDatabaseWritingTaskTestCase(unittest.TestCase):
    """
    Test RelationsDatabaseWritingTask.
    """
    @mock.patch('bwg.tasks.relations_database_writing.RelationsDatabaseWritingTask.output')
    @mock.patch('bwg.tasks.relations_database_writing.RelationsDatabaseWritingTask.input')
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

        task = bwg.tasks.relations_database_writing.RelationsDatabaseWritingTask(task_config=task_config)

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
