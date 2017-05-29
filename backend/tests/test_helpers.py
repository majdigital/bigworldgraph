# -*- coding: utf-8 -*-
"""
Testing module for simple helper functions.
"""

# STD
import copy
import io
import os
import random
import time
import unittest
import re

# PROJECT
from bwg.helpers import (
    filter_dict, construct_dict_from_source, get_config_from_py_file, overwrite_local_config_with_environ,
    flatten_dictlist, download_nltk_resource_if_missing, is_collection, seconds_to_hms,
    time_function, fast_copy, get_if_exists
)
from fixtures import TEST_DICT


class DictionaryHelpersTestCase(unittest.TestCase):
    """
    Test all helper functions that concern dictionaries.
    """
    test_dict = None

    def setUp(self):
        self.test_dict = TEST_DICT

    def test_filter_dict(self):
        assert filter_dict(self.test_dict, []) == {}
        assert filter_dict(self.test_dict, ["field1", "field3"]) == {"field1": True, "field3": "hello"}

    def test_construct_dict_from_source(self):
        assert construct_dict_from_source({}, self.test_dict) == {}
        assert construct_dict_from_source(
            {
                "field1": lambda x: x["field1"],
                "field2": lambda x: x["field2"],
                "field3": lambda x: x["field3"],
                "field4": lambda x: x["field4"],
            },
            self.test_dict
        ) == self.test_dict

        assert construct_dict_from_source(
            {"field2_str": lambda x: str(x["field2"])}, source=self.test_dict
        ) == {"field2_str": "33"}

        assert construct_dict_from_source(
            {"nested_field": lambda x: x["field4"]["field4_1"]["field4_1_1"]}, source=self.test_dict
        ) == {"nested_field": "nested"}

    def test_get_if_exists(self):
        # Test extreme cases
        assert get_if_exists(self.test_dict) is None
        assert get_if_exists({}) is None

        # Test normal case
        assert get_if_exists(self.test_dict, "field1")

        # Test non-existing fields
        assert get_if_exists(self.test_dict, "field5") is None
        assert get_if_exists(self.test_dict, "field5", default=1) == 1

        # Test nested fields
        assert get_if_exists(self.test_dict, "field4", "field4_1", "field4_1_1") == "nested"

    @staticmethod
    def test_flatten_dictlist():
        assert flatten_dictlist([]) == {}
        assert flatten_dictlist([{"a": 3}]) == {"a": 3}
        assert flatten_dictlist([{"a": 3}, {"a": 4}]) == {"a": 4}
        assert flatten_dictlist([{"a": 3}, {"b": 5}]) == {"a": 3, "b": 5}


class ConfigurationHelpersTestCase(unittest.TestCase):
    """
    Test all functions concerning configuration.
    """
    original_config = {
        "CONFIG_DEPENDENCIES": {
            "all": [
                "PIPELINE_DEBUG",
                "{language}_LANGUAGE_ABBREVIATION"
            ],
            "optional": [
                "OPTIONAL_PARAMETER"
            ],
            "exclude": [
                "CONFIG_DEPENDENCIES",
                "SUPPORTED_LANGUAGES",
            ],
            "task1": [
                "PARAM1"
            ],
            "task2": [
                "PARAM2",
                "{language}_PARAM"
            ],
            "task3": [
                "PARAM3"
            ]
        },
        "SUPPORTED_LANGUAGES": ["DEMO"],
        "PARAM1": "abc",
        "PARAM2": 12,
        "PARAM3": True,
        "DEMO_PARAM": 3.5,
        "REDUNDANT_PARAM": "yada yada",
        "PIPELINE_DEBUG": True,
        "DEMO_LANGUAGE_ABBREVIATION": "demo",
        "OPTIONAL_PARAMETER": "I am optional"
    }

    def test_get_config_from_py_file(self):
        assert get_config_from_py_file("./non_existing_config.py") == {}
        raw_config = get_config_from_py_file("./dummy_pipeline_config.py")
        assert raw_config == self.original_config

    @staticmethod
    def test_overwrite_local_config_with_environ():
        os.environ["DEMO_LANGUAGE_ABBREVIATION"] = "do"
        os.environ["UNIMPORTANT_PARAMETER"] = "not important"
        raw_config = get_config_from_py_file("./dummy_pipeline_config.py")
        config = overwrite_local_config_with_environ(raw_config)
        assert config["DEMO_LANGUAGE_ABBREVIATION"] == "do"
        assert "UNIMPORTANT_PARAMETER" not in config


class TimeHelpersTestCase(unittest.TestCase):
    """
    Test all functions concerning time.
    """
    @staticmethod
    def _dummy_function():
        for i in range(4):
            time.sleep(random.randint(1, 9) / 10)
        return True

    @staticmethod
    def test_seconds_to_hms():
        hours, minutes, seconds = seconds_to_hms(0)
        assert hours == minutes == seconds == 0

        hours, minutes, seconds = seconds_to_hms(61)
        assert hours == 0 and minutes == 1 and seconds == 1

        hours, minutes, seconds = seconds_to_hms(3601)
        assert hours == 1 and minutes == 0 and seconds == 1

    def test_time_function(self):
        mock_stdout1 = io.StringIO()
        mock_stdout2 = io.StringIO()
        time_string_regex = "Function .+? took \d+.\d{2} hour\(s\), \d+.\d{2} minute\(s\) and \d+.\d{2} second\(s\)" \
                            " to complete\."

        @time_function(out=mock_stdout1)
        def dummy1():
            return self._dummy_function()

        @time_function(out=mock_stdout2, return_time=True)
        def dummy2():
            return self._dummy_function()

        result1 = dummy1()
        result2 = dummy2()
        time_string1 = mock_stdout1.getvalue()
        time_string2 = mock_stdout2.getvalue()

        assert result1
        assert result2["return"]
        assert type(result2["runtime"]) == float
        assert re.search(time_string_regex, time_string1) is not None
        assert re.search(time_string_regex, time_string2) is not None


class MiscellaneousHelpersTestCase(unittest.TestCase):
    """
    Test remaining helper functions.
    """
    def test_is_collection(self):
        inputs_and_expected = [
            ("", False), ({}, True), (set(), True), (tuple(), True), (frozenset(), True), ([], True), (2, False),
            (2.2, False), (True, False)
        ]

        for input_, expected in inputs_and_expected:
            assert is_collection(input_) == expected

    @staticmethod
    def test_fast_copy():
        dict_copy1 = copy.deepcopy(TEST_DICT)
        dict_copy2 = fast_copy(TEST_DICT)
        assert TEST_DICT == dict_copy1 == dict_copy2
        assert {} == copy.deepcopy({}) == fast_copy({})


if __name__ == "__main__":
    unittest.main(verbosity=2)
