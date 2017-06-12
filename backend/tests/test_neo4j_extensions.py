# -*- coding: utf-8 -*-
"""
Test support for the Neo4j graph database.
"""

# STD
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
            data={},
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

        self.test_selection = test_nodes = [node1, node2, node3, node4]
        self.test_result = Neo4jResult(test_nodes)

    def test_neo4j_result_init(self):
        assert self.test_result.selection == self.test_selection

    def test_neo4j_magic_methods(self):
        # Test __iter__
        for result in self.test_result:
            assert "nodes" in result
            assert "links" in result

        # Test __getitem__
        for i in range(len(self.test_selection)):
            for j in range(0, i):
                a, b = self.test_result.return_selection[i], self.test_result[i]
                assert self.test_result.return_selection[i] == self.test_result[i]
                assert self.test_result.return_selection[j:i] == self.test_result[j:i]
                assert self.test_result.return_selection[j:i:2] == self.test_result[j:i:2]

    def test_count(self):
        # TODO (Test): Test with_limit_and_skip key word argument after implementing it
        assert self.test_result.count() == len(self.test_selection)

    def test_clean_node(self):
        # TODO (Implement) [DU 07.06.17]
        pass

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
        # TODO (Implement) [DU 07.06.17]
        pass


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
