# -*- coding: utf-8 -*-
"""
Create support for the Neo4j graph database.
"""

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


class PipelineRunInfo(neomodel.StructuredNode):
    """
    Define a model for pipeline run information.
    """
    uid = neomodel.UniqueIdProperty()
    run_id = neomodel.StringProperty()
    timestamp = neomodel.StringProperty()
    article_ids = neomodel.ArrayProperty()


class Neo4jTarget(luigi.Target):
    """
    Additional luigi target to write a tasks output into a neo4j graph database.
    """
    mode = None
    _exists = True

    def __init__(self, pipeline_run_info, user, password, host="localhost", port=7687):
        self.pipeline_run_info = pipeline_run_info
        neomodel.config.DATABASE_URL = "bolt://{user}:{password}@{host}:{port}".format(
            user=user, password=password, host=host, port=port
        )
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
        try:
            relation = Relation.nodes

            for relation in relation:
                relation.delete()
        except:
            pass

    def add_relation(self, relation_json, sentence):
        """
        Add a new relation to the graph database.
        
        :param relation_json: Relation JSON object.
        :type relation_json: dict
        :param sentence: Sentence the current relation occurs in.
        :type sentence: str
        """
        # TODO (Bug): Check if relations are already in database and retrieve them if so [DU 19.04.17]
        # TODO (Improve): Add Wikidata properties to entites [DU 19.04.17]
        relation_meta, relation_data = relation_json["meta"], relation_json["data"]
        subj_phrase, verb, obj_phrase = relation_data["subject_phrase"], relation_data["verb"], relation_data["object_phrase"]
        subj_entity = self._get_or_create_node(label=subj_phrase, data={"phrase": subj_phrase})
        obj_entity = self._get_or_create_node(label=obj_phrase, data={"phrase": obj_phrase})
        relation = self._get_or_create_connection(
            subj_entity,
            obj_entity,
            label=verb,
            data={
                "phrase": verb,
                "sentence": sentence,
                "relation_id": relation_meta["id"]
            }
        )

    @staticmethod
    def _get_or_create_node(label, data):
        try:
            return Entity.nodes.get(label=label)
        except Entity.DoesNotExist:
            entity = Entity(label=label, data=data)
            entity.save()
            return entity

    @staticmethod
    def _get_or_create_connection(subj_entity, obj_entity, label, data):
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
