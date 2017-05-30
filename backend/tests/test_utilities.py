# -*- coding: utf-8 -*-
"""
Testing utilities for the NLP pipeline.
"""

# STD
import unittest

# PROJECT
from bwg.utilities import (
    serialize_article, serialize_dependency_parse_tree, serialize_relation, serialize_sentence,
    serialize_tagged_sentence, serialize_wikidata_entity, deserialize_line
)


class SerializingTestCase(unittest.TestCase):
    """
    Test all functions that serialize or deserialize JSON objects for the NLP pipeline.
    """
    def test_serialize_tagged_sentence(self):
        pass

    def test_serialize_dependency_parse_tree(self):
        pass

    def test_serialize_sentence(self):
        pass

    def test_serialize_relations(self):
        pass

    def test_serialize_wikidata_entity(self):
        pass

    def test_serialize_article(self):
        pass

    def test_jump_dump(self):
        pass


class MiscellaneousUtilitiesTestCase(unittest.TestCase):
    """
    Test remaining utilities functions.
    """
    def test_retry_with_fallback(self):
        pass

    def test_get_nes_from_sentence(self):
        pass
