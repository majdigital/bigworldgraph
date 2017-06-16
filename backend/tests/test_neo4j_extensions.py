# -*- coding: utf-8 -*-
"""
Test support for the Neo4j graph database.
"""

# STD
import copy
import unittest
import random

# EXT
import neomodel

# PROJECT
from bwg.neo4j_extensions import (
    EveCompatibilityMixin, Relation, Entity, PipelineRunInfo, Neo4jResult, Neo4jDatabase, Neo4jLayer, Neo4jTarget
)
from bwg.api_config import (
    NEO4J_HOST, NEO4J_PASSWORD, NEO4J_PORT, NEO4J_USER, NODE_TYPES, RELATION_TYPES, NODE_BASE_CLASSES
)
from bwg.helpers import overwrite_local_config_with_environ


class DummyParsedRequest:
    legit_parameters = {
        "aggregation", "embedded", "if_match", "if_modified_since", "if_none_match", "max_results", "page",
        "projection", "show_deleted", "sort", "where"
    }

    def __init__(self, **kwargs):
        self.args = kwargs.get("args", {})

        for param in self.legit_parameters:
            if param in kwargs:
                setattr(self, param, kwargs[param])
            else:
                setattr(self, param, None)


class Neo4jTestMixin:
    """
    Create some testing nodes for different Neo4j-related tests.
    """
    @property
    def created_test_nodes(self):
        node1 = Entity(
            uid="1",
            label="node1",
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
            }
        )
        node2 = Entity(uid="2", label="node2", data={})
        node3 = Entity(uid="3", label="node3", data={})
        node4 = Entity(uid="4", label="node4", data={})

        nodes = [node1, node2, node3, node4]
        for node in nodes:
            node.save()

        return [copy.deepcopy(node) for node in [node1, node2, node3, node4]]

    def create_nodes(self):
        for node in self.created_test_nodes:
            node.save()

    def create_and_connect_nodes(self):
        connections = [(1, 2), (1, 3), (3, 2)]
        self.create_nodes()

        for start, end in connections:
            start_node = Entity.nodes.get(uid=start)
            end_node = Entity.nodes.get(uid=end)
            relation = end_node.relations.connect(start_node)
            relation.save()

    @staticmethod
    def reset_database():
        neomodel.util.clear_neo4j_database(neomodel.db)


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


class Neo4jResultTestCase(unittest.TestCase, Neo4jTestMixin):
    """
    Testing the Neo4jResult class.
    """
    test_result = None

    def setUp(self):
        self._test_selection = self.created_test_nodes

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

        # Test __len__
        assert len(self.test_selection) == len(self.test_result)

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
        # Test no request parameters
        no_request_result = Neo4jResult(self.test_selection, parsed_request=DummyParsedRequest())
        assert self.test_result.return_selection == no_request_result.return_selection

        # Test max_results parameter
        max_results_result = Neo4jResult(self.test_selection, parsed_request=DummyParsedRequest(max_results=2))
        assert self.test_result.return_selection[:2] == max_results_result.return_selection

        # Test remaining parameters
        # TODO (Testing): Test other query parameters when they are implemented


class Neo4jDatabaseTestCase(unittest.TestCase, Neo4jTestMixin):
    """
    Testing the Neo4jDatabase class.
    """
    def setUp(self):
        self.neo4j_database = Neo4jDatabase(user=NEO4J_USER, password=NEO4J_PASSWORD, host=NEO4J_HOST, port=NEO4J_PORT)
        self.reset_database()

    def tearDown(self):
        self.reset_database()

    def test_init(self):
        assert neomodel.config.DATABASE_URL == "bolt://{user}:{password}@{host}:{port}".format(
            user=NEO4J_USER, password=NEO4J_PASSWORD, host=NEO4J_HOST, port=NEO4J_PORT
        )

    def test_get_node_class(self):
        # Default
        class1 = self.neo4j_database.get_node_class("SpecificEntity")
        assert class1.__name__ == "SpecificEntity"
        assert issubclass(class1, neomodel.StructuredNode) and issubclass(class1, EveCompatibilityMixin)

        # Custom base classes
        class2 = self.neo4j_database.get_node_class("NewEntity", base_classes=(neomodel.StructuredNode, ))
        assert class2.__name__ == "NewEntity"
        assert issubclass(class2, neomodel.StructuredNode) and not issubclass(class2, EveCompatibilityMixin)

    def test_find_nodes(self):
        # Non-existing node
        assert self.neo4j_database.find_nodes(Entity, DummyParsedRequest()) == []

        for node in self.created_test_nodes:
            node.save()

        # All nodes
        assert len(self.neo4j_database.find_nodes(Entity, DummyParsedRequest())) == 4

        # Single node with constraint
        assert len(self.neo4j_database.find_nodes(Entity, req=DummyParsedRequest(), uid="1")) == 1

        self.reset_database()

    def test_friends_of_friends(self):
        self.reset_database()

        assert len(self.neo4j_database.find_friends_of_friends(Entity, "uid", "1")) == 0

        self.create_and_connect_nodes()

        friends_of_friends = self.neo4j_database.find_friends_of_friends(Entity, "uid", "1")
        assert len(friends_of_friends) == 3
        assert len(set([node.uid for node in friends_of_friends]) - {"1", "2", "3"}) == 0

        self.reset_database()

    def test_get_or_create_node(self):
        test_nodes = self.created_test_nodes
        self.reset_database()

        first_node = test_nodes[0]
        new_node = self.neo4j_database.get_or_create_node(label=first_node.label, data=first_node.data)
        same_node = self.neo4j_database.get_or_create_node(label=first_node.label, data=first_node.data)
        assert new_node.id == same_node.id
        assert new_node.weight == 1
        assert same_node.weight == 2
        assert new_node.label == same_node.label == first_node.label
        assert new_node.data == same_node.data == first_node.data

    def test_or_create_connection(self):
        test_nodes = self.created_test_nodes

        first_node, second_node = test_nodes[0], test_nodes[1]
        new_connection = self.neo4j_database.get_or_create_connection(
            first_node, second_node, "new_connection", {"param": "test"}
        )
        same_connection = self.neo4j_database.get_or_create_connection(
            first_node, second_node, "new_connection", {"param": "test"}
        )
        assert new_connection.id == same_connection.id
        assert new_connection.weight == 1
        assert same_connection.weight == 2
        assert new_connection.label == same_connection.label
        assert new_connection.data == same_connection.data


class Neo4jLayerTestCase(unittest.TestCase, Neo4jTestMixin):
    """
    Testing the Neo4jLayer class.
    """
    def setUp(self):
        class MockApp:
            def __init__(self, **config):
                self.config = config
                self.config["DOMAIN"] = {
                    "entities": {
                        "item_title": "Entity"
                    }
                }

        config = {
            "NEO4J_USER": NEO4J_USER,
            "NEO4J_HOST": NEO4J_HOST,
            "NEO4J_PORT": NEO4J_PORT,
            "NEO4J_PASSWORD": NEO4J_PASSWORD,
            "NODE_TYPES": NODE_TYPES,
            "NODE_BASE_CLASSES": NODE_BASE_CLASSES,
            "RELATION_TYPES": RELATION_TYPES
        }
        config = overwrite_local_config_with_environ(config)
        mock_app = MockApp(**config)
        self.neo4j_layer = Neo4jLayer(app=mock_app)
        self.url = neomodel.config.DATABASE_URL
        neomodel.util.clear_neo4j_database(neomodel.db)

        for node in self.created_test_nodes:
            node.save()

    def tearDown(self):
        neomodel.util.clear_neo4j_database(neomodel.db)

    @neomodel.util.ensure_connection
    def test_init_app(self):
        assert len(self.neo4j_layer.node_types) > 0
        assert len(self.neo4j_layer.relation_types) > 0
        assert len(self.neo4j_layer.node_base_classes) > 0
        assert len(self.neo4j_layer.node_base_classes_names) > 0

        assert all(
            [
                issubclass(node_base_class, neomodel.StructuredNode) and
                issubclass(node_base_class, EveCompatibilityMixin)
                for node_base_class in self.neo4j_layer.node_base_classes
            ]
        )
        assert all([isinstance(node_type, str) for node_type in self.neo4j_layer.node_types])
        assert all([isinstance(relation_type, str) for relation_type in self.neo4j_layer.relation_types])

    def test_find(self):
        # All nodes
        search_result1 = self.neo4j_layer.find("entities", DummyParsedRequest(), None)
        assert len(search_result1) == 4
        assert len(set([node["uid"] for node in search_result1.return_selection]) - {"1", "2", "3", "4"}) == 0

        # Friends and friends of friends
        search_result2 = self.neo4j_layer.find("entities", DummyParsedRequest(args={"uid": 1}), None)
        assert len(set([node["uid"] for node in search_result2.return_selection]) - {"1", "2", "3"}) == 0

        # Non-existing nodes
        search_result3 = self.neo4j_layer.find("entities", DummyParsedRequest(args={"uid": 100}), None)
        assert len(search_result3) == 0

    def test_aggregate(self):
        # TODO (Test): Implement when Neo4jLayer.aggregate() is implemented [DU 14.06.17]
        pass

    def test_find_one(self):
        search_result = self.neo4j_layer.find_one("entities", DummyParsedRequest())
        assert len(search_result) == 1
        assert search_result[0]["uid"] == "1"

    def test_find_one_raw(self):
        # TODO (Test): Implement when Neo4jLayer.find_one_raw() is implemented [DU 14.06.17]
        return True

    def test_find_list_of_ids(self):
        search_result1 = self.neo4j_layer.find_list_of_ids("entities", set(range(0, 10000)))
        assert len(search_result1) == 4

        node_ids = [node["id"] for node in search_result1.return_selection]
        test_id = random.choice(node_ids)
        search_result2 = self.neo4j_layer.find_list_of_ids("entities", [test_id])
        assert len(search_result2) == 1
        assert search_result2.return_selection[0]["id"] == test_id

    def test_insert(self):
        # TODO (Test): Implement when Neo4jLayer.insert() is implemented [DU 14.06.17]
        return True

    def test_update(self):
        # TODO (Test): Implement when Neo4jLayer.update() is implemented [DU 14.06.17]
        return True

    def test_replace(self):
        # TODO (Test): Implement when Neo4jLayer.replace() is implemented [DU 14.06.17]
        return True

    def test_remove(self):
        # TODO (Test): Implement when Neo4jLayer.find_one_raw() is implemented [DU 14.06.17]
        return True

    def test_combine_queries(self):
        with self.assertRaises(NotImplementedError):
            self.neo4j_layer.combine_queries("", "")

    def test_get_value_from_query(self):
        with self.assertRaises(NotImplementedError):
            self.neo4j_layer.get_value_from_query("", "")

    def test_query_contains_field(self):
        with self.assertRaises(NotImplementedError):
            self.neo4j_layer.query_contains_field("", "")

    def test_is_empty(self):
        neomodel.util.clear_neo4j_database(neomodel.db)
        assert self.neo4j_layer.is_empty("entities")


class Neo4jTargetTestCase(unittest.TestCase):
    """
    Testing the Neo4jTarget class.
    """
    # TODO (Implement) [DU 07.06.17]
    pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
