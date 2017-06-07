# -*- coding: utf-8 -*-
"""
Test support for the Neo4j graph database.
"""

# STD
import unittest

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
