# -*- coding: utf-8 -*-
"""
Testing utilities for the NLP pipeline.
"""

# STD
import json
import unittest

# PROJECT
from bwg.pipeline_config import DEPENDENCY_TREE_KEEP_FIELDS
from bwg.helpers import filter_dict
from bwg.utilities import (
    serialize_article, serialize_dependency_parse_tree, serialize_relation, serialize_sentence,
    serialize_tagged_sentence, serialize_wikidata_entity, deserialize_line, just_dump, retry_with_fallback,
    get_nes_from_sentence
)
from fixtures import RAW_SENTENCE, TAGGED_SENTENCE, SENTENCES, DEPENDENCY_TREE, RELATIONS, WIKIDATA_ENTITIES


class SerializingTestCase(unittest.TestCase):
    """
    Test all functions that serialize or deserialize JSON objects for the NLP pipeline.
    """
    @staticmethod
    def _test_serializing_function(raw_input, serializing_function):
        assert type(serializing_function("1234", raw_input)) == str
        assert type(serializing_function("1234", raw_input, pretty=True)) == str
        assert type(serializing_function("1234", raw_input, dump=False)) == dict
        assert type(serializing_function("1234", raw_input, pretty=True, dump=False)) == dict

        serialized_json_object = serializing_function("1234", raw_input, state="new_state", dump=False)
        assert "meta" in serialized_json_object["1234"] and "data" in serialized_json_object["1234"]
        assert serialized_json_object["1234"]["meta"]["state"] == "new_state"
        return serialized_json_object

    def test_serialize_tagged_sentence(self):
        serialized_json_object = self._test_serializing_function(TAGGED_SENTENCE, serialize_tagged_sentence)
        assert serialized_json_object["1234"]["data"] == TAGGED_SENTENCE

    def test_serialize_dependency_parse_tree(self):
        serialized_json_object = self._test_serializing_function(DEPENDENCY_TREE, serialize_dependency_parse_tree)

        simplified_tree = {
            "root": DEPENDENCY_TREE["root"]["address"],
            "nodes": {
                int(number): filter_dict(node, DEPENDENCY_TREE_KEEP_FIELDS)
                for number, node in DEPENDENCY_TREE["nodes"].items()
            }
        }
        assert serialized_json_object["1234"]["data"] == simplified_tree

    def test_serialize_sentence(self):
        serialized_json_object = self._test_serializing_function(RAW_SENTENCE, serialize_sentence)
        assert serialized_json_object["1234"]["data"] == RAW_SENTENCE

    @staticmethod
    def test_serialize_relations():
        assert type(serialize_relation("1234", "this is a sentence", RELATIONS)) == str
        assert type(serialize_relation("1234", "this is a sentence", RELATIONS, pretty=True)) == str
        assert type(serialize_relation("1234", "this is a sentence", RELATIONS, dump=False)) == dict
        assert type(serialize_relation("1234", "this is a sentence", RELATIONS, pretty=True, dump=False)) == dict

        serialized_json_object = serialize_relation(
            "1234", "this is a sentence", RELATIONS, state="new_state", dump=False
        )
        assert "meta" in serialized_json_object["1234"] and "data" in serialized_json_object["1234"]
        assert serialized_json_object["1234"]["meta"]["state"] == "new_state"

        relation = serialized_json_object["1234"]["data"]["relations"]["1234/00001"]["data"]
        assert relation["subject_phrase"] == RELATIONS[0][0]
        assert relation["verb"] == RELATIONS[0][1]
        assert relation["object_phrase"] == RELATIONS[0][2]

    def test_serialize_wikidata_entity(self):
        serialized_json_object = self._test_serializing_function(WIKIDATA_ENTITIES, serialize_wikidata_entity)
        entity_sense_ids = set([entity["id"] for entity in WIKIDATA_ENTITIES[0]])
        serialized_entity_ids = set()

        entities = serialized_json_object["1234"]["data"]["entities"]
        for entity, entity_json in entities.items():
            entity_data = entity_json["data"]
            for sense in entity_data:
                serialized_entity_ids.add(sense["id"])

        # Check if all senses are present
        assert len(entity_sense_ids.union(serialized_entity_ids)) == len(entity_sense_ids)

    @staticmethod
    def test_serialize_article():
        test_article_id = "1234"
        test_article_url = "www.testurl.com/1234"
        test_article_title = "test article"

        assert type(serialize_article(
            test_article_id, test_article_url, test_article_title, SENTENCES, state="new_state"
        )) == str
        assert type(serialize_article(
            test_article_id, test_article_url, test_article_title, SENTENCES, state="new_state", pretty=True
        )) == str
        assert type(serialize_article(
            test_article_id, test_article_url, test_article_title, SENTENCES, state="new_state", pretty=True,
            from_scratch=False
        )) == str

        assert type(serialize_article(
            test_article_id, test_article_url, test_article_title, SENTENCES, state="new_state", dump=False
        )) == dict
        assert type(serialize_article(
            test_article_id, test_article_url, test_article_title, SENTENCES, state="new_state", pretty=True, dump=False
        )) == dict
        assert type(serialize_article(
            test_article_id, test_article_url, test_article_title, SENTENCES, state="new_state", pretty=True,
            from_scratch=False, dump=False
        )) == dict

        serialized_article = serialize_article(
            test_article_id, test_article_url, test_article_title, SENTENCES, state="new_state", dump=False,
            from_scratch=False
        )
        assert serialized_article["meta"]["state"] == "new_state"
        assert serialized_article["meta"]["id"] == test_article_id
        assert serialized_article["meta"]["title"] == test_article_title
        assert serialized_article["meta"]["url"] == test_article_url

    @staticmethod
    def test_just_dump():
        json_object = {"sentence": RAW_SENTENCE}
        assert type(just_dump(json_object)) == str
        assert type(just_dump(json_object, pretty=True)) == str
        assert json_object == json.loads(just_dump(json_object))
        assert json_object == json.loads(just_dump(json_object, pretty=True))
        assert json_object == deserialize_line(just_dump(json_object))


class MiscellaneousUtilitiesTestCase(unittest.TestCase):
    """
    Test remaining utilities functions.
    """
    @staticmethod
    def test_retry_with_fallback():
        @retry_with_fallback(KeyError, important_kwarg="retry_value")
        def dummy_function(*args, important_kwarg=None):
            if important_kwarg == "fail":
                raise KeyError
            assert important_kwarg == "retry_value"

        dummy_function(important_kwarg="fail")

    @staticmethod
    def test_get_nes_from_sentence():
        test_tagged_sentence = [
            ("a", "I-PERS"), ("b", "I-PERS"), ("c", "I-ORG"), ("d", "O")
        ]
        nes1 = get_nes_from_sentence(test_tagged_sentence, 'O')
        nes2 = get_nes_from_sentence(test_tagged_sentence, 'O', include_tag=True)

        assert "a b" in nes1
        assert "c" in nes1
        assert [entity for entity, tag in nes2] == nes1
        assert [tag for entity, tag in nes2] == ["I-PERS", "I-ORG"]


if __name__ == "__main__":
    unittest.main(verbosity=2)
