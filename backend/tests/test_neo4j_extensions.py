# -*- coding: utf-8 -*-
"""
Test support for the Neo4j graph database.
"""

# STD
import copy
import unittest
import unittest.mock as mock

# EXT
import neomodel

# PROJECT
from bwg.neo4j_extensions import (
    EveCompatibilityMixin, Relation, Entity, PipelineRunInfo, Neo4jResult, Neo4jDatabase, Neo4jLayer, Neo4jTarget
)


class EveCompatibilityMixinTestCase(unittest.TestCase):
    """
    Testing the EveCompatibilityMixin class.
    """
    @staticmethod
    def test_eve_compatibility_mixin():
        class TestClass(EveCompatibilityMixin):
            def __init__(self):
                self.param = 3

        test_object = TestClass()

        # Test __contains__
        assert "param" in test_object

        # Test __getitem__
        assert test_object["param"] == 3
        test_object["param"] = 4

        # Test __setitem__
        assert test_object["param"] == 4


class StucturedNodesTestCase(unittest.TestCase):
    """
    Testing StructuredNode classes.
    """
    @staticmethod
    def test_structured_nodes():
        test_data = [
            (
                Relation,
                {
                    "label": "relation_label",
                    "data": {
                        "param": 33
                    }
                },
                (neomodel.StructuredRel, EveCompatibilityMixin)
            ),
            (
                Entity,
                {
                    "uid": "1234",
                    "category": "entity",
                    "label": "entity_label",
                    "data": {
                        "param": "test"
                    },
                    "relations": []
                },
                (neomodel.StructuredNode, EveCompatibilityMixin)
            ),
            (
                PipelineRunInfo,
                {
                    "uid": "4321",
                    "run_id": "1234abcd",
                    "timestamp": "1980.01.01 00:00:01",
                    "article_ids": ["ab12", "cd34"]
                },
                (neomodel.StructuredNode, )
            )
        ]

        for node_class, node_init_kwargs, super_classes in test_data:
            node = node_class(**node_init_kwargs)
            assert all([isinstance(node, super_class) for super_class in super_classes])
            for key, value in node_init_kwargs.items():
                assert getattr(node, key) == value


class Neo4jResultTestCase(unittest.TestCase):
    """
    Testing the Neo4jResult class.
    """
    test_result = None

    def setUp(self):
        class RelationList(list):
            def __init__(self, *args, uid=None, relationships={}):
                self.uid = uid
                self.relationships = relationships
                super().__init__(*args)

            def relationship(self, other_node):
                return self.relationships[(self.uid, other_node.uid)]

        self.relationships = relationships = {
            ("1", "2"): {
                "id": "R1",
                "label": "relation12",
                "data": {},
                "source": Entity(uid="1"),
                "target": Entity(uid="2")
            },
            ("1", "3"): {
                "id": "R2",
                "label": "relation13",
                "data": {},
                "source": Entity(uid="1"),
                "target": Entity(uid="3")
            },
            ("3", "2"): {
                "id": "R3",
                "label": "relation32",
                "data": {},
                "source": Entity(uid="3"),
                "target": Entity(uid="2")
            }
        }

        node1 = Entity(
            uid="1",
            data={
                'category': "entity",
                'ambiguous': False,
                'senses': [
                    {
                        'aliases': ["Entity"],
                        'description': 'test entity',
                        'label': 'Test Entity',
                        'claims': {
                            'claim1': {
                                'target': 'claim_attribute',
                                'implies_relation': False,
                                'entity_class': None,
                                'target_data': {
                                    'ambiguous': False,
                                    'senses': []
                                }
                            }
                        },
                        'type': 'I-PER',
                        'wikidata_last_modified': '2017-02-26T18:25:53Z',
                        'wikidata_id': 'Q12345678'
                    }
                ]
            },
            relations=RelationList((Entity(uid="2"), Entity(uid="2")), uid="1", relationships=relationships)
        )
        node2 = Entity(
            uid="2",
            data={},
            relations=RelationList(uid="2", relationships=relationships)
        )
        node3 = Entity(
            uid="3",
            data={},
            relations=RelationList((Entity(uid="2"), ), uid="3", relationships=relationships)
        )
        node4 = Entity(
            uid="4",
            data={},
            relations=RelationList(uid="4", relationships=relationships)
        )

        self._test_selection = [node1, node2, node3, node4]

    @property
    def test_selection(self):
        return [copy.deepcopy(node) for node in self._test_selection]

    @property
    def test_result(self):
        return Neo4jResult(self.test_selection)

    def test_neo4j_result_init(self):
        assert [node.uid for node in self.test_result.selection] == \
               [node.uid for node in self.test_selection]

    def test_neo4j_magic_methods(self):
        # Test __iter__
        for result in self.test_result:
            assert "nodes" in result
            assert "links" in result

        # Test __getitem__
        for i in range(len(self.test_selection)):
            for j in range(0, i):
                assert self.test_result.return_selection[i]["uid"] == self.test_result[i]["uid"]

                # Only compare uids because nodes come out of Neo4jResult cleaned
                assert [el["uid"] for el in self.test_result.return_selection[j:i]] == \
                       [el["uid"] for el in self.test_result[j:i]]
                assert [el["uid"] for el in self.test_result.return_selection[j:i:2]] == \
                       [el["uid"] for el in self.test_result[j:i:2]]

    def test_count(self):
        # TODO (Test): Test with_limit_and_skip key word argument after implementing it [DU 09.06.17]
        assert self.test_result.count() == len(self.test_selection)

    def test_clean_node(self):
        target_node = None
        original_node = self.test_selection[0]
        cleaning_test_result = Neo4jResult(self.test_selection[:2])

        for result in cleaning_test_result:
            nodes = result["nodes"]
            target_node = nodes[0]
            break

        # Superficial test, see test_clean_unserializables for a more in-depth test
        assert not hasattr(target_node, "DoesNotExist")

        # Test relation filtering
        assert "R2" not in cleaning_test_result.relation_ids
        assert "R3" not in cleaning_test_result.relation_ids

        # Test cleaning of Wikidata claims
        target_first_sense = target_node["data"]["senses"][0]
        original_first_sense = original_node["data"]["senses"][0]
        # Make sure these values stayed the same
        assert target_first_sense["aliases"] == original_first_sense["aliases"]
        assert target_first_sense["label"] == original_first_sense["label"]
        assert target_first_sense["type"] == original_first_sense["type"]
        assert target_first_sense["wikidata_id"] == original_first_sense["wikidata_id"]
        assert target_first_sense["wikidata_last_modified"] == original_first_sense["wikidata_last_modified"]
        assert all(
            [
                dirty_claim == clean_claim and dirty_claim_data["target"] == clean_claim_target
                for (dirty_claim, dirty_claim_data), (clean_claim, clean_claim_target)
                in zip(original_first_sense["claims"].items(), target_first_sense["claims"].items())
            ]
        )

    def test_clean_unserializables(self):
        clean_dict = {
            "param1": 1,
            "param2": 2.22,
            "param3": True,
            "param4": None,
            "param5": [1, 2, 3, 4, 5],
            "param6": {n: n**2 for n in range(1, 5)}
        }

        # "Pollute" dict with unserializable types
        dirty_dict = dict(clean_dict)
        dirty_dict.update(
            {
                "param7": lambda x: x**2,
                "param8": type("Test Class", tuple(), {})
            }
        )

        cleaned_dict = self.test_result.clean_unserializables(dirty_dict)
        assert cleaned_dict == clean_dict

    @staticmethod
    def test_is_json_serializable():
        assert Neo4jResult.is_json_serializable("test string")
        assert Neo4jResult.is_json_serializable(None)
        assert Neo4jResult.is_json_serializable(1234)
        assert Neo4jResult.is_json_serializable(True)
        assert Neo4jResult.is_json_serializable(22.2)
        assert Neo4jResult.is_json_serializable([1, 2, 3, 4, 5])
        assert Neo4jResult.is_json_serializable({n: n**2 for n in range(1, 5)})
        assert not Neo4jResult.is_json_serializable(lambda x: x**2)
        assert not Neo4jResult.is_json_serializable(type("Test Class", tuple(), {}))

    def test_apply_request_parameters(self):
        class DummyParsedRequest:
            legit_parameters = {
                "aggregation", "embedded", "if_match", "if_modified_since", "if_none_match", "max_results", "page",
                "projection", "show_deleted", "sort", "where"
            }

            def __init__(self, **kwargs):
                for param in self.legit_parameters:
                    if param in kwargs:
                        setattr(self, param, kwargs[param])
                    else:
                        setattr(self, param, None)

        # Test no request parameters
        no_request_result = Neo4jResult(self.test_selection, parsed_request=DummyParsedRequest())
        assert self.test_result.return_selection == no_request_result.return_selection

        # Test max_results parameter
        max_results_result = Neo4jResult(self.test_selection, parsed_request=DummyParsedRequest(max_results=2))
        assert self.test_result.return_selection[:2] == max_results_result.return_selection

        # Test remaining parameters
        # TODO (Testing): Test other query parameters when they are implemented


class Neo4jDatabaseTestCase(unittest.TestCase):
    """
    Testing the Neo4jDatabase class.
    """
    # TODO (Implement) [DU 07.06.17]
    pass


class Neo4jLayerTestCase(unittest.TestCase):
    """
    Testing the Neo4jLayer class.
    """
    # TODO (Implement) [DU 07.06.17]
    pass


class Neo4jTargetTestCase(unittest.TestCase):
    """
    Testing the Neo4jTarget class.
    """
    # TODO (Implement) [DU 07.06.17]
    pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
