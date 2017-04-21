# -*- coding: utf-8 -*-
"""
Create support for the Neo4j graph database.
"""

# STD
import sys

# EXT
import luigi
import neomodel


class Relation(neomodel.StructuredRel):
    """
    Node model for relations in the graph.
    """
    label = neomodel.StringProperty()
    data = neomodel.JSONProperty()


class Entity(neomodel.StructuredNode):
    """
    Node model for entities in the graph.
    """
    uid = neomodel.UniqueIdProperty()
    label = neomodel.StringProperty()
    data = neomodel.JSONProperty()
    relations = neomodel.Relationship("Entity", "CONNECTED_WITH", model=Relation)


class Person(Entity):
    """
    Node model people in the graph.
    """
    pass


class Organization(Entity):
    """
    Node model for organizations in the graph.
    """
    pass


class Date(Entity):
    """
    Node model for organizations in the graph.
    """
    pass


class Location(Entity):
    """
    Node model for organization in the graph.
    """
    pass


class Miscellaneous(Entity):
    """
    Node model for remaining entities in the graph that couldn't be assigned to any other model.
    """
    pass


class PipelineRunInfo(neomodel.StructuredNode):
    """
    Define a model for pipeline run information.
    """
    uid = neomodel.UniqueIdProperty()
    run_id = neomodel.StringProperty()
    timestamp = neomodel.StringProperty()
    article_ids = neomodel.ArrayProperty()


# TODO (Refactor): Add database functions to its own wrapper class, from which the target inherits [DU 21.04.17]


class Neo4jTarget(luigi.Target):
    """
    Additional luigi target to write a tasks output into a neo4j graph database.
    """
    mode = None
    _exists = True

    def __init__(self, pipeline_run_info, user, password, host="localhost", port=7687, ne_tag_to_model={}):
        """
        Initialize a Neo4j graph database target.
        
        :param pipeline_run_info: Info about the current run of the database. Is used to determine whether this task has
         to be run.
        :type pipeline_run_info: dict
        :param user: Username to access database.
        :type user: str
        :param password: Password to access database.
        :type password: str
        :param host: Host of database.
        :type host: str
        :param port: Port of database.
        :type port: str
        :param ne_tag_to_model: Defines how entities with certain named entity tags are mapped to Neo4j node classes.
        :type ne_tag_to_model: dict
        """
        self.pipeline_run_info = pipeline_run_info
        neomodel.config.DATABASE_URL = "bolt://{user}:{password}@{host}:{port}".format(
            user=user, password=password, host=host, port=port
        )
        self.ne_tag_to_model = ne_tag_to_model
        self._delete_all_entities()
        self._delete_all_relations()

    def exists(self):
        """
        Task will be run if information about the current run is not already saved in the database (meaning that
        this run has already been performed) or the target is opened in writing mode (meaning all entries will get
        overwritten.
        
        :return: Whether the above conditions apply.
        :rtype: bool
        """
        # TODO (Bug): Only run if new hash
        return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    def _delete_all_entities():
        """
        Delete all entities in the database.
        """
        try:
            entities = Entity.nodes

            for entity in entities:
                entity.delete()
        except Entity.DoesNotExist:
            pass

    @staticmethod
    def _delete_all_relations():
        """
        Delete all relations in the database.
        """
        try:
            relation = Relation.nodes

            for relation in relation:
                relation.delete()
        except:
            pass

    def add_relation(self, relation_json, sentence, entity_properties):
        """
        Add a new relation to the graph database.
        
        :param relation_json: Relation JSON object.
        :type relation_json: dict
        :param sentence: Sentence the current relation occurs in.
        :type sentence: str
        :param entity_properties: Wikidata properties as dictionary with the entity's name as key and the properties as 
        value.
        :type entity_properties: dict
        """
        relation_meta, relation_data = relation_json["meta"], relation_json["data"]
        subj_phrase, verb, obj_phrase = relation_data["subject_phrase"], relation_data["verb"], relation_data["object_phrase"]
        subj_data = entity_properties.get(subj_phrase, {})
        obj_data = entity_properties.get(subj_phrase, {})
        subj_node = self._get_or_create_node(label=subj_phrase, data=subj_data)
        obj_node = self._get_or_create_node(label=obj_phrase, data=obj_data)
        self._add_wikidata_relations(subj_node, subj_data)
        self._add_wikidata_relations(obj_node, obj_data)

        self._get_or_create_connection(
            subj_node,
            obj_node,
            label=verb,
            data={
                "sentence": sentence,
                "relation_id": relation_meta["id"]
            }
        )

    def _add_wikidata_relations(self, node, node_data):
        """
        Add relations from Wikidata to the graph.
        
        :param node: Node of which the Wikidata relations are going to be added.
        :type node: Entity
        :param node_data: Data of the current node.
        :type node_data: dict
        """
        if "claims" in node_data:
            for claim, claim_data in node_data["claims"].items():
                target, implies_relation = claim_data["target"], claim_data["implies_relation"]

                if implies_relation and target != node_data["label"]:
                    obj_node = self._get_or_create_node(label=target, data={})
                    self._get_or_create_connection(node, obj_node, label=claim, data={})

    def _get_or_create_node(self, label, data):
        """
        Retrieve a node with a specific label from the database, or, if it doesn't exist, create it.
        
        :param label: Label of target node.
        :type label: str
        :param data: Data of target node.
        :type data: dict
        :return: Target node.
        :rtype: Entity
        """
        entity_class_string = self.ne_tag_to_model.get(data.get("type", "Entity"), "Miscellaneous")
        entity_class = getattr(sys.modules[__name__], entity_class_string)

        try:
            return entity_class.nodes.get(label=label)
        except entity_class.DoesNotExist:
            entity = entity_class(label=label, data=data)
            entity.save()
            return entity

    @staticmethod
    def _get_or_create_connection(subj_entity, obj_entity, label, data):
        """
        Retrieve a certain connection from the database, or, if it doesn't exist, create it.
        
        :param subj_entity: Start node of connection.
        :type subj_entity: Entity
        :param obj_entity: End node of connection.
        :type obj_entity: Entity
        :param label: Label of connection.
        :type label: str
        :param data: Data of connection.
        :type data: dict
        :return: Connection.
        :rtype: Relation
        """
        if obj_entity.relations.is_connected(subj_entity):
            return obj_entity.relations.search(label=label)
        else:
            relation = obj_entity.relations.connect(
                subj_entity,
                {
                    "label": label,
                    "data": data
                }
            )
            relation.save()
            subj_entity.refresh()
            obj_entity.refresh()
            return relation

    def _check_if_run_exists_and_add(self, pipeline_run_info):
        """
        Check if this run of the pipeline has already been made. If not, add it to the database.
        
        :param pipeline_run_info: Information about the current pipeline run.
        :type pipeline_run_info: dict
        """
        current_run_id = pipeline_run_info["run_id"]

        try:
            PipelineRunInfo.nodes.get(run_id=current_run_id)
        except PipelineRunInfo.DoesNotExist:
            self._exists = False
            current_run_info = PipelineRunInfo(
                run_id=pipeline_run_info["run_id"],
                timestamp=pipeline_run_info["timestamp"],
                articles_ids=pipeline_run_info["article_ids"]
            )
            current_run_info.save()
