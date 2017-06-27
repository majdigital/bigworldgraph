# -*- coding: utf-8 -*-
"""
Testing functions concerning the config management of the NLP pipeline.
"""

# STD
import os
import unittest

# PROJECT
from bwg.config_management import (
    format_config_parameter, format_task_config_key, build_task_config_for_language
)


class ConfigManagementTest(unittest.TestCase):
    """
    Test configuration management of pipeline.
    """
    @staticmethod
    def test_config_parameter_formatting():
        parameter1, language1 = ("{language}_PARAMETER", "ENGLISH")
        parameter2, language2 = ("NORMAL_PARAMETER", "ENGLISH")

        assert parameter1.format(language=language1) == format_config_parameter(parameter1, language1)
        assert parameter2 == format_config_parameter(parameter2, language2)

    @staticmethod
    def test_task_config_key_formatting():
        parameter1 = "{language}_PARAMETER"
        parameter2 = "NORMAL_PARAMETER"

        assert "PARAMETER" == format_task_config_key(parameter1)
        assert parameter2 == format_task_config_key(parameter2)

    @staticmethod
    def test_building_task_config():
        dummy_pipeline_config = build_task_config_for_language(
            ["task1", "task2"], language="DEMO", config_file_path=os.environ.get(
                "DUMMY_PIPELINE_CONFIG_PATH", "./dummy_pipeline_config.py"
            )
        )
        assert dummy_pipeline_config["PARAM"] == 3.5
        assert dummy_pipeline_config["PARAM1"] == "abc"
        assert dummy_pipeline_config["PARAM2"] == 12
        assert "PARAM3" not in dummy_pipeline_config
        assert "CONFIG_DEPENDENCIES" not in dummy_pipeline_config
        assert "SUPPORTED_LANGUAGES" not in dummy_pipeline_config
        assert dummy_pipeline_config["OPTIONAL_PARAMETER"] == "I am optional"

        dummy_pipeline_config2 = build_task_config_for_language(
            ["task1", "task2"], language="DEMO", config_file_path=os.environ.get(
                "DUMMY_PIPELINE_CONFIG_PATH", "./dummy_pipeline_config.py"
            ),
            include_optionals=False
        )
        assert "OPTIONAL_PARAMETER" not in dummy_pipeline_config2


if __name__ == "__main__":
    unittest.main(verbosity=2)
