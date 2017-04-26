# -*- coding: utf-8 -*-
"""
Create support for the Neo4j graph database.
"""

# EXT
from eve.io.base import DataLayer
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


def create_entity_class(class_name):
    return type(class_name, (Entity, ), {})


class PipelineRunInfo(neomodel.StructuredNode):
    """
    Define a model for pipeline run information.
    """
    uid = neomodel.UniqueIdProperty()
    run_id = neomodel.StringProperty()
    timestamp = neomodel.StringProperty()
    article_ids = neomodel.ArrayProperty()


class NEO4jDatabase:
    def __init__(self, user, password, host, port):
        neomodel.config.DATABASE_URL = "bolt://{user}:{password}@{host}:{port}".format(
            user=user, password=password, host=host, port=port
        )


class Neo4jLayer(DataLayer, NEO4jDatabase):
    """
    This a simple re-implementation for a Neo4j data layer, because flask_neo4j doesn't seem to be maintained anymore, 
    leading eve_neo4j to break.
    
    Docstring are mostly just copied from eve.io.DataLayer.
    """
    def init_app(self, app):
        NEO4jDatabase.__init__(
            user=app.config["NEO4J_USER"], password=app.config["NEO4J_PASSWORD"],
            host=app.config["NEO4J_HOST"], port=app.config["NEO4J_PORT"]
        )

    def find(self, resource, req, sub_resource_lookup):
        """
        Retrieves a set of documents (rows), matching the current request.
        Consumed when a request hits a collection/document endpoint
        (`/people/`).

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve both
                         the db collection/table and base query (filter), if
                         any.
        :param req: an instance of ``eve.utils.ParsedRequest``. This contains
                    all the constraints that must be fulfilled in order to
                    satisfy the original request (where and sort parts, paging,
                    etc). Be warned that `where` and `sort` expresions will
                    need proper parsing, according to the syntax that you want
                    to support with your driver. For example ``eve.io.Mongo``
                    supports both Python and Mongo-like query syntaxes.
        :param sub_resource_lookup: sub-resource lookup from the endpoint url.
        """
        # TODO (Implement) [DU 26.04.17]
        pass

    def aggregate(self, resource, pipeline, options):
        """ 
        Perform an aggregation on the resource datasource and returns
        the result. Only implement this if the underlying db engine supports
        aggregation operations.

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the db collection/table consumed by the resource.
        :param pipeline: aggregation pipeline to be executed.
        :param options: aggregation options to be considered.
        """
        # TODO (Implement) [DU 26.04.17]
        pass

    def find_one(self, resource, req, **lookup):
        """ 
        Retrieves a single document/record. Consumed when a request hits an
        item endpoint (`/people/id/`).

        :param resource: resource being accessed. You should then use the
                         ``datasource`` helper function to retrieve both the
                         db collection/table and base query (filter), if any.
        :param req: an instance of ``eve.utils.ParsedRequest``. This contains
                    all the constraints that must be fulfilled in order to
                    satisfy the original request (where and sort parts, paging,
                    etc). As we are going to only look for one document here,
                    the only req attribute that you want to process here is
                    ``req.projection``.

        :param **lookup: the lookup fields. This will most likely be a record
                         id or, if alternate lookup is supported by the API,
                         the corresponding query.
        """
        # TODO (Implement) [DU 26.04.17]
        pass

    def find_one_raw(self, resource, _id):
        """ 
        Retrieves a single, raw document. No projections or datasource
        filters are being applied here. Just looking up the document by unique
        id.

        :param resource: resource name.
        :param _id: unique id.
        """
        # TODO (Implement) [DU 26.04.17]
        pass

    def find_list_of_ids(self, resource, ids, client_projection=None):
        """
        Retrieves a list of documents based on a list of primary keys
        The primary key is the field defined in `ID_FIELD`.
        This is a separate function to allow us to use per-database
        optimizations for this type of query.

        :param resource: resource name.
        :param ids: a list of ids corresponding to the documents
        to retrieve
        :param client_projection: a specific projection to use
        :return: a list of documents matching the ids in `ids` from the
        collection specified in `resource` 
        """
        # TODO (Implement) [DU 26.04.17]
        pass

    def insert(self, resource, doc_or_docs):
        """
        Inserts a document into a resource collection/table.

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve both
                         the actual datasource name.
        :param doc_or_docs: json document or list of json documents to be added
                            to the database.
        """
        # TODO (Implement) [DU 26.04.17]
        pass

    def update(self, resource, id_, updates, original):
        """
        Updates a collection/table document/row.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param id_: the unique id of the document.
        :param updates: json updates to be performed on the database document
                        (or row).
        :param original: definition of the json document that should be
        updated.
        :raise OriginalChangedError: raised if the database layer notices a
        change from the supplied `original` parameter.
        """
        # TODO (Implement) [DU 26.04.17]
        pass

    def replace(self, resource, id_, document, original):
        """
        Replaces a collection/table document/row.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param id_: the unique id of the document.
        :param document: the new json document
        :param original: definition of the json document that should be
        updated.
        :raise OriginalChangedError: raised if the database layer notices a
        change from the supplied `original` parameter.
        """
        # TODO (Implement) [DU 26.04.17]
        pass

    def remove(self, resource, lookup={}):
        """
        Removes a document/row or an entire set of documents/rows from a
        database collection/table.

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param lookup: a dict with the query that documents must match in order
                       to qualify for deletion. For single document deletes,
                       this is usually the unique id of the document to be
                       removed.
        """
        # TODO (Implement) [DU 26.04.17]
        pass

    def combine_queries(self, query_a, query_b):
        """
        Takes two db queries and applies db-specific syntax to produce
        the intersection.
        """
        # TODO (Implement) [DU 26.04.17]
        pass

    def get_value_from_query(self, query, field_name):
        """
        Parses the given potentially-complex query and returns the value
        being assigned to the field given in `field_name`.

        This mainly exists to deal with more complicated compound queries 
        """
        # TODO (Implement) [DU 26.04.17]
        pass

    def query_contains_field(self, query, field_name):
        """
        For the specified field name, does the query contain it?
        Used know whether we need to parse a compound query.
        """
        # TODO (Implement) [DU 26.04.17]
        pass

    def is_empty(self, resource):
        """
        Returns True if the collection is empty; False otherwise. While
        a user could rely on self.find() method to achieve the same result,
        this method can probably take advantage of specific datastore features
        to provide better perfomance.

        Don't forget, a 'resource' could have a pre-defined filter. If that is
        the case, it will have to be taken into consideration when performing
        the is_empty() check (see eve.io.mongo.mongo.py implementation).

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        """
        # TODO (Implement) [DU 26.04.17]
        pass


class Neo4jTarget(luigi.Target, NEO4jDatabase):
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
        NEO4jDatabase.__init__(user=user, password=password, host=host, port=port)
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
        try:
            return Entity.nodes.get(label=label)
        except Entity.DoesNotExist:
            entity_class_string = self.ne_tag_to_model.get(data.get("type", "Entity"), "Miscellaneous")
            entity_class = create_entity_class(entity_class_string)
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
