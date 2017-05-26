# -*- coding: utf-8 -*-
"""
Testing module for simple helper functions.
"""

# STD
import unittest

# PROJECT
from bwg.helpers import (
    filter_dict, construct_dict_from_source, get_config_from_py_file, overwrite_local_config_with_environ,
    flatten_dictlist, download_nltk_resource_if_missing, is_collection, seconds_to_hms,
    time_function, fast_copy, get_if_exists
)


class DictionaryHelpersTestCase(unittest.TestCase):
    """
    Test all helper functions that concern dictionaries.
    """
    test_dict = None

    def setUp(self):
        self.test_dict = {
            "field1": True,
            "field2": 33,
            "field3": "hello",
            "field4": {
                "field4_1": {
                    "field4_1_1": "nested"
                },
                "field4_2": False
            }
        }

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
    Test loading a .py config file.
    """
    pass


class TimeHelpersTestCase(unittest.TestCase):
    # TODO (Implement) [DU 26.05.17]
    pass


class MiscellaneousHelpersTestCase(unittest.TestCase):
    # TODO (Implement) [DU 26.05.17]
    pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
