# -*- coding: utf-8 -*-
"""
Create support for the Neo4j graph database.
"""

# STD
import json
import sys
import os

# EXT
from eve.io.base import DataLayer
from eve.exceptions import ConfigException
from eve.utils import ParsedRequest
import luigi
import neomodel
import neo4j

# PROJECT
from bwg.helpers import get_if_exists
from bwg.decorators import retry_on_condition


class EveCompatibilityMixin:
    """
    Extend ``neomodel`` classes to make them compatible with Eve API functions.
    """
    def __contains__(self, item):
        return item in vars(self)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class Relation(neomodel.StructuredRel, EveCompatibilityMixin):
    """
    Node model for relations in the graph.
    """
    label = neomodel.StringProperty()   # Text that should be displayed about this edge
    data = neomodel.JSONProperty()  # Dictionary with more detailed data about this relation
    weight = neomodel.IntegerProperty(default=1)


class Entity(neomodel.StructuredNode, EveCompatibilityMixin):
    """
    Node model for entities in the graph.
    """
    uid = neomodel.UniqueIdProperty()  # Unique ID for this database entry
    category = neomodel.StringProperty()   # Category of this entity (Person, Organization...)
    label = neomodel.StringProperty()  # Text that should be displayed about this node
    data = neomodel.JSONProperty()  # Dictionary with more detailed data about this entity
    relations = neomodel.Relationship("Entity", "CONNECTED_WITH", model=Relation)
    weight = neomodel.IntegerProperty(default=1)


class PipelineRunInfo(neomodel.StructuredNode):
    """
    Define a model for pipeline run information.
    """
    uid = neomodel.UniqueIdProperty()  # Unique ID for this database entry
    run_id = neomodel.StringProperty()  # ID for this pipeline run, created with sentence IDs involved in this run
    timestamp = neomodel.StringProperty()  # Timestamp for the current pipeline run
    article_ids = neomodel.ArrayProperty()  # List of sentence IDs involved in this pipeline run


class Neo4jResult:
    """
    Object the result of a data layer query gets wrapped in.
    """
    def __init__(self, selection, **kwargs):
        """
        Constructor.
        
        :param selection: Current database selection.
        :type selection: list
        :param kwargs: Additional key word arguments.
        :type kwargs: dict
        """
        self.relations = []
        self.relation_ids = set()
        self.node_ids = set()
        self.parsed_request = kwargs.get("parsed_request", None)
        self._return_selection = self.selection = selection

        for node in selection:
            self.node_ids.add(node.uid)

    def __iter__(self):
        yield {
            "nodes": self.return_selection,
            "links": self.relations
        }

    def __getitem__(self, *args):
        if type(args[0]) in (int, slice):
            return self.return_selection[args[0]]
        return KeyError

    def __len__(self):
        return self.count()

    @property
    def return_selection(self):
        return_selection = self._return_selection
        return_selection = self._apply_request_parameters(return_selection)
        return_selection = self._clean_selection(return_selection)

        return return_selection

    def count(self, with_limit_and_skip=False, **kwargs):
        # TODO (Implement): Implement this in a clean way with all the features [DU 27.04.17]
        return len(self.selection)

    def _clean_selection(self, selection):
        """
        Clean all elements of this selection of fields which values are not serializable.
        """
        return [self._clean_node(node) for node in selection]

    def _clean_node(self, node):
        """
        Clean the node of data that is unserializable and transform it into a structure that is easy to be visualized 
        later. 
        
        :param node: Node to be cleaned.
        :type node: dict
        :return: Cleaned node.
        :rtype: dict
        """
        for target_node in node.relations:
            relation = node.relations.relationship(target_node)
            relation = self.clean_unserializables(relation)
            relation["source"] = node.uid
            relation["target"] = target_node.uid

            if relation["id"] not in self.relation_ids and \
               node.uid in self.node_ids and target_node.uid in self.node_ids:
                self.relations.append(relation)
                self.relation_ids.add(relation["id"])

        # Clean non-serializable-fields
        node = self.clean_unserializables(node)

        # Clean claims
        for sense in get_if_exists(node, "data", "senses", default=[]):
            if "claims" in sense:
                sense["claims"] = {
                    claim: claim_data["target"]
                    for claim, claim_data in sense["claims"].items()
                }

        if "relations" in node:
            del node["relations"]
        return node

    def clean_unserializables(self, dictionary):
        """
        Remove unserializable fields from a dictionary.
        
        :param dictionary: Dictionary to be cleaned from unserializable fields.
        :type dictionary: dict
        :return: Cleaned dictionary.
        :rtype: dict
        """
        return {
            key: value
            for key, value in (dictionary.items() if type(dictionary) == dict else vars(dictionary).items())
            if self.is_json_serializable(value) and not key.startswith("_")
        }

    @staticmethod
    def is_json_serializable(value):
        """
        Test whether a value is JSON serializable.
        
        :param value: Value to be tested.
        :type value: any
        :return: Result of check.
        :rtype: bool
        """
        try:
            json.dumps(value)
            return True
        except (TypeError, OverflowError):
            return False

    def _apply_request_parameters(self, selection):
        """
        Apply additional request parameters to the current selection.
        """
        if self.parsed_request is not None:
            aggregation = getattr(self.parsed_request, "aggregation")
            embedded = getattr(self.parsed_request, "embedded")
            if_match = getattr(self.parsed_request, "if_match")
            if_modified_since = getattr(self.parsed_request, "if_modified_since")
            if_none_match = getattr(self.parsed_request, "if_none_match")
            max_results = getattr(self.parsed_request, "max_results")
            page = getattr(self.parsed_request, "page")
            projection = getattr(self.parsed_request, "projection")
            show_deleted = getattr(self.parsed_request, "show_deleted")
            sort = getattr(self.parsed_request, "sort")
            where = getattr(self.parsed_request, "where")

            if aggregation is not None:
                # TODO (Implement) [DU 28.04.17]
                raise NotImplementedError

            if embedded is not None:
                # TODO (Implement) [DU 28.04.17]
                raise NotImplementedError

            if if_match is not None:
                # TODO (Implement) [DU 28.04.17]
                raise NotImplementedError

            if if_modified_since is not None:
                # TODO (Implement) [DU 28.04.17]
                raise NotImplementedError

            if if_none_match is not None:
                # TODO (Implement) [DU 28.04.17]
                raise NotImplementedError

            if page is not None:
                # TODO (Implement) [DU 28.04.17]
                pass

            if projection is not None:
                # TODO (Implement) [DU 28.04.17]
                raise NotImplementedError

            if show_deleted is not None:
                # TODO (Implement) [DU 28.04.17]
                pass

            if sort is not None:
                # TODO (Implement) [DU 28.04.17]
                raise NotImplementedError

            if where is not None:
                # TODO (Implement) [DU 28.04.17]
                raise NotImplementedError

            if max_results is not None:
                selection = selection[:max_results]

        return selection


class Neo4jDatabase:
    """
    Wrapper for a ``Neo4j`` Graph database, providing an easy way to connect to a database, querying nodes and relations as 
    well as creating new Node and Relation classes on the fly.
    """
    # During deployment with docker, the Python container needs to wait for the Neo4j container to start up
    @retry_on_condition(
        exception_class=neo4j.bolt.connection.ServiceUnavailable,
        condition=lambda: os.environ.get("ENV", None) == "testing",
        max_retries=25
    )
    def __init__(self, user, password, host, port):
        neomodel.config.DATABASE_URL = "bolt://{user}:{password}@{host}:{port}".format(
            user=user, password=password, host=host, port=port
        )

    @staticmethod
    def get_node_class(class_name, base_classes=(neomodel.StructuredNode, EveCompatibilityMixin)):
        """
        Get the corresponding node class to a class name. If it isn't found in the current module, create it on the fly.
        
        :param class_name: Name of class that is looked for.
        :type class_name: str
        :param base_classes: Classes the class should inherit from in case it's created from scratch.
        :type base_classes: tuple
        :return: Node class.
        :rtype: neomodel.StructuredNode
        """
        node_class = getattr(sys.modules[__name__], class_name, None)

        if node_class is None:
            return type(class_name, base_classes, {})
        return node_class

    def find_nodes(self, node_class, req, **constraints):
        """
        Find nodes of a certain class given optional constraints.
        
        :param node_class: Class of nodes that is of interest.
        :type node_class: neomodel.StructuredNode
        :param constraints: Search constraints.
        :type constraints: dict
        :return: List of nodes matching the criteria.
        :rtype: list
        """
        try:
            if req.args not in ({}, None):
                if "pretty" not in req.args:
                    identifier = list(req.args.keys())[0]
                    return self.find_friends_of_friends(node_class, identifier, req.args[identifier])

            return [node_class.nodes.get(**constraints)] if constraints != {} else node_class.nodes.all()
        except node_class.DoesNotExist:
            return []

    @staticmethod
    def find_friends_of_friends(node_class, identifier, identifier_value):
        """
        Find friends and friends of friends of a specific node.
        
        :param node_class: Class of target node.
        :type node_class: neomodel.StructuredNode 
        :param identifier: Field that should be used to identify the target node.
        :type identifier: str
        :param identifier_value: Value that should be used to identify the target node.
        :type identifier_value: str
        :return: list of friends and friends of friends.
        :rtype: list
        """
        results, meta = neomodel.db.cypher_query(
            'MATCH (n)-[r]-(m), (m)-[r2]-(o) WHERE n.{identifier} = "{identifier_value}" RETURN n, o, m'.format(
                identifier=identifier, identifier_value=identifier_value
            )
        )

        unique_node_identifiers = set()
        unique_nodes = []

        for result in results:
            for row in result:
                node = node_class.inflate(row)

                if identifier not in vars(node):
                    continue

                current_identifier = getattr(node, identifier)
                if current_identifier not in unique_node_identifiers:
                    unique_nodes.append(node)
                    unique_node_identifiers.add(current_identifier)

        return unique_nodes

    @staticmethod
    def get_or_create_node(label, data, node_category=Entity):
        """
        Retrieve a node with a specific label from the database, or, if it doesn't exist, create it.

        :param label: Label of target node.
        :type label: str
        :param data: Data of target node.
        :type data: dict
        :param node_category: Entity class of node if given. Otherwise it will be determined by the categorization
        function.
        :type node_category: Entity
        :return: Target node.
        :rtype: Entity
        """
        try:
            entity = Entity.nodes.get(label=label)
            entity.weight += 1
            entity.save()
            return entity
        except Entity.DoesNotExist:
            entity = node_category(category=node_category.__name__, label=label, data=data)
            entity.save()
            return entity

    @staticmethod
    def get_or_create_connection(subj_entity, obj_entity, label, data):
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
            connection = obj_entity.relations.relationship(subj_entity)
            connection.weight += 1
            connection.save()
            return connection
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


class Neo4jLayer(DataLayer, Neo4jDatabase):
    """
    This a simple re-implementation for a ``Neo4j`` data layer, because flask_neo4j doesn't seem to be maintained anymore, 
    leading eve_neo4j to break.
    
    Docstring are mostly just copied from eve.io.DataLayer.
    """
    node_base_classes = None  # List of base classes for nodes
    node_base_classes_names = None  # List of names of node base classes
    node_types = None  # List of base types for nodes
    relation_types = None  # List of base types for relations
    relation_base_classes = None  # List of base classes for relations
    relation_base_classes_names = None  # List of names of relation base classes

    def init_app(self, app):
        self.app = app

        self._init_db(app)

        # Determine base types for nodes and vertices
        self.node_types = app.config["NODE_TYPES"]
        self.relation_types = app.config["RELATION_TYPES"]
        self.node_base_classes = tuple([
            self.get_node_class(base_class_name)
            for base_class_name in app.config.get("NODE_BASE_CLASSES", [])
        ]) if app.config.get("NODE_BASE_CLASSES", []) != [] else (neomodel.StructuredNode, EveCompatibilityMixin)
        self.node_base_classes_names = [
            node_base_class.__name__ for node_base_class in self.node_base_classes
        ]

    # During deployment with docker, the Python container needs to wait for the Neo4j container to start up
    @retry_on_condition(
        exception_class=neo4j.bolt.connection.ServiceUnavailable,
        condition=lambda: os.environ.get("ENV", None) == "testing",
        max_retries=25
    )
    def _init_db(self, app):
        Neo4jDatabase.__init__(
            self, user=app.config["NEO4J_USER"], password=app.config["NEO4J_PASSWORD"],
            host=app.config["NEO4J_HOST"], port=app.config["NEO4J_PORT"]
        )

    def find(self, resource, req, sub_resource_lookup):
        """
        Retrieves a set of documents (rows), matching the current request.
        Consumed when a request hits a collection/document endpoint
        (`/people/`).

        :param resource: resource being accessed. You should then use the ``datasource`` helper function to retrieve 
            both the db collection/table and base query (filter), if any.
        :param req: an instance of ``eve.utils.ParsedRequest``. This contains all the constraints that must be fulfilled
            in order to satisfy the original request (where and sort parts, paging, etc). Be warned that `where` and 
            `sort` expressions will need proper parsing, according to the syntax that you want to support with your 
            driver. For example ``eve.io.Mongo`` supports both Python and Mongo-like query syntaxes.
        :param sub_resource_lookup: sub-resource lookup from the endpoint url.
        """
        item_title = self.app.config["DOMAIN"][resource]["item_title"].capitalize()

        if item_title in self.node_base_classes_names:
            node_class = self.get_node_class(item_title)
            results = self.find_nodes(node_class, req)
        elif resource in self.node_types:
            node_class = self.get_node_class(class_name=item_title, base_classes=self.node_base_classes)
            results = self.find_nodes(node_class, req)
        else:
            raise ConfigException("Resource {} wasn't found in neither node or relation types.".format(resource))

        return Neo4jResult(results, parsed_request=req)

    def aggregate(self, resource, pipeline, options):
        """ 
        Perform an aggregation on the resource datasource and returns
        the result. Only implement this if the underlying db engine supports
        aggregation operations.

        :param resource: resource being accessed. You should then use the ``datasource`` helper function to retrieve 
            the db collection/table consumed by the resource.
        :param pipeline: aggregation pipeline to be executed.
        :param options: aggregation options to be considered.
        """
        # TODO (Implement) [DU 26.04.17]
        raise NotImplementedError

    def find_one(self, resource, req, **lookup):
        """ 
        Retrieves a single document/record. Consumed when a request hits an
        item endpoint (`/people/id/`).

        :param resource: resource being accessed. You should then use the ``datasource`` helper function to retrieve  
            both the db collection/table and base query (filter), if any.
        :param req: an instance of ``eve.utils.ParsedRequest``. This contains all the constraints that must be fulfilled
            in order to satisfy the original request (where and sort parts, paging, etc). As we are going to only look for 
            one document here, the only req attribute that you want to process here is``req.projection``.

        :param **lookup: the lookup fields. This will most likely be a record id or, if alternate lookup is supported by
        the API, the corresponding query.
        """
        item_title = self.app.config["DOMAIN"][resource]["item_title"].capitalize()

        if item_title in self.node_base_classes_names:
            node_class = self.get_node_class(item_title)
            results = self.find_nodes(node_class, req)
        elif resource in self.node_types:
            node_class = self.get_node_class(class_name=item_title, base_classes=self.node_base_classes)
            results = self.find_nodes(node_class, req)
        else:
            raise ConfigException("Resource {} wasn't found in neither node or relation types.".format(resource))

        return Neo4jResult([results[0]], parsed_request=req)

    def find_one_raw(self, resource, _id):
        """ 
        Retrieves a single, raw document. No projections or datasource filters are being applied here. Just looking up 
        the document by unique id.

        :param resource: resource name.
        :param _id: unique id.
        """
        # TODO (Implement) [DU 26.04.17]
        raise NotImplementedError

    def find_list_of_ids(self, resource, ids, client_projection=None):
        """
        Retrieves a list of documents based on a list of primary keys. The primary key is the field defined in 
        `ID_FIELD`. This is a separate function to allow us to use per-database optimizations for this type of query.

        :param resource: resource name.
        :param ids: a list of ids corresponding to the documents to retrieve
        :param client_projection: a specific projection to use
        :return: a list of documents matching the ids in `ids` from the collection specified in `resource` 
        """
        item_title = self.app.config["DOMAIN"][resource]["item_title"].capitalize()

        if item_title in self.node_base_classes_names:
            node_class = self.get_node_class(item_title)
            results = self.find_nodes(node_class, req=ParsedRequest())
        elif resource in self.node_types:
            node_class = self.get_node_class(class_name=item_title, base_classes=self.node_base_classes)
            results = self.find_nodes(node_class)
        else:
            raise ConfigException("Resource {} wasn't found in neither node or relation types.".format(resource))

        return Neo4jResult([result for result in results if result["id"] in ids])

    def insert(self, resource, doc_or_docs):
        """
        Inserts a document into a resource collection/table.

        :param resource: resource being accessed. You should then use the ``datasource`` helper function to retrieve 
            both the actual datasource name.
        :param doc_or_docs: json document or list of json documents to be added to the database.
        """
        # TODO (Implement) [DU 26.04.17]
        raise NotImplementedError

    def update(self, resource, id_, updates, original):
        """
        Updates a collection/table document/row.
        
        :param resource: resource being accessed. You should then use the ``datasource`` helper function to retrieve
            the actual datasource name.
        :param id_: the unique id of the document.
        :param updates: json updates to be performed on the database document (or row).
        :param original: definition of the json document that should be
            updated.
        :raise OriginalChangedError: raised if the database layer notices a change from the supplied `original` 
            parameter.
        """
        # TODO (Implement) [DU 26.04.17]
        raise NotImplementedError

    def replace(self, resource, id_, document, original):
        """
        Replaces a collection/table document/row.
        
        :param resource: resource being accessed. You should then use the ``datasource`` helper function to retrieve
            the actual datasource name.
        :param id_: the unique id of the document.
        :param document: the new json document
        :param original: definition of the json document that should be updated.
        :raise OriginalChangedError: raised if the database layer notices a change from the supplied `original` 
            parameter.
        """
        # TODO (Implement) [DU 26.04.17]
        raise NotImplementedError

    def remove(self, resource, lookup={}):
        """
        Removes a document/row or an entire set of documents/rows from a
        database collection/table.

        :param resource: resource being accessed. You should then use the ``datasource`` helper function to retrieve the
            actual datasource name.
        :param lookup: a dict with the query that documents must match in order to qualify for deletion. For single 
            document deletes, this is usually the unique id of the document to be removed.
        """
        # TODO (Implement) [DU 26.04.17]
        raise NotImplementedError

    def combine_queries(self, query_a, query_b):
        """
        Takes two db queries and applies db-specific syntax to produce
        the intersection.
        """
        raise NotImplementedError

    def get_value_from_query(self, query, field_name):
        """
        Parses the given potentially-complex query and returns the value
        being assigned to the field given in `field_name`.

        This mainly exists to deal with more complicated compound queries
        """
        raise NotImplementedError

    def query_contains_field(self, query, field_name):
        """
        For the specified field name, does the query contain it?
        Used know whether we need to parse a compound query.
        """
        raise NotImplementedError

    def is_empty(self, resource):
        """
        Returns True if the collection is empty; False otherwise. While
        a user could rely on self.find() method to achieve the same result,
        this method can probably take advantage of specific datastore features
        to provide better perfomance.

        Don't forget, a 'resource' could have a pre-defined filter. If that is
        the case, it will have to be taken into consideration when performing
        the is_empty() check (see eve.io.mongo.mongo.py implementation).

        :param resource: resource being accessed. You should then use the ``datasource`` helper function to retrieve the
            actual datasource name.
        """
        resource_collection = self.find(resource, ParsedRequest(), None)
        return resource_collection.count() == 0


class Neo4jTarget(luigi.Target, Neo4jDatabase):
    """
    Additional luigi target to write a tasks output into a neo4j graph database.
    """
    _exists = True

    def __init__(self, pipeline_run_info, user, password, host="localhost", port=7687, categories={"Entity": 0},
                 node_relevance_function=lambda label, node_data: True,
                 categorization_function=lambda label, node_data: "Entity"):
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
        :param categories: Categories of nodes in the database with their level of detail as int.
        :type categories: dict
        :param node_relevance_function: Function where the user can define a relevance function for new nodes in the
        database. It takes the future nodes data. By default, all nodes are relevant. Connections will only be added if
        both nodes involved are relevant.
        :type node_relevance_function: func
        :param categorization_function: Function that assigns nodes to a specific category.
        :type categorization_function: func
        """
        self.categories = categories
        self.pipeline_run_info = pipeline_run_info

        self._init_db(user, password, host, port)
        self.node_relevance_function = node_relevance_function
        self._categorize_node = categorization_function

    # During deployment with docker, the Python container needs to wait for the Neo4j container to start up
    @retry_on_condition(
        exception_class=neo4j.bolt.connection.ServiceUnavailable,
        condition=lambda: os.environ.get("ENV", None) == "testing",
        max_retries=25
    )
    def _init_db(self, user, password, host, port):
        """
        Initialize the database.

        :param user: Username to access database.
        :type user: str
        :param password: Password to access database.
        :type password: str
        :param host: Host of database.
        :type host: str
        :param port: Port of database.
        :type port: str
        """
        Neo4jDatabase.__init__(self, user=user, password=password, host=host, port=port)

    def exists(self):
        """
        Task will be run if information about the current run is not already saved in the database (meaning that
        this run has already been performed) or the target is opened in writing mode (meaning all entries will get
        overwritten.
        
        :return: Whether the above conditions apply.
        :rtype: bool
        """
        # TODO (Bug): Only run if new hash [DU 26.08.17]
        # At the moment, this task is run every time the pipeline is run
        return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def categorize_node(self, label, data, entity_class="Entity"):
        implied_entity_class_string = entity_class
        categorized_entity_class_string = self._categorize_node(label, data)

        # Define which class should be preferred in different cases by comparing the priorities of the classes
        if self.categories[implied_entity_class_string] > self.categories[categorized_entity_class_string]:
            entity_class = self.get_node_class(implied_entity_class_string, (Entity,))
            entity_class_string = implied_entity_class_string
        else:
            entity_class = self.get_node_class(categorized_entity_class_string, (Entity,))
            entity_class_string = categorized_entity_class_string

        return entity_class, entity_class_string

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
        subj_phrase, verb, obj_phrase = relation_data["subject_phrase"], relation_data["verb"], \
                                        relation_data["object_phrase"]
        subj_data = entity_properties.get(subj_phrase, {})
        obj_data = entity_properties.get(obj_phrase, {})
        subj_node_is_relevant = self.node_relevance_function(subj_phrase, subj_data)
        obj_node_is_relevant = self.node_relevance_function(obj_phrase, obj_data)

        if subj_node_is_relevant:
            subj_label = subj_data["senses"][0].get("label", "No label available")  # Get label if available
            node_category, _ = self.categorize_node(subj_label, subj_data)
            subj_node = self.get_or_create_node(label=subj_phrase, data=subj_data, node_category=node_category)
            self._add_wikidata_relations(subj_node, subj_data)

        if obj_node_is_relevant:
            obj_label = obj_data["senses"][0].get("label", "No label available")  # Get label if available
            node_category, _ = self.categorize_node(obj_label, obj_data)
            obj_node = self.get_or_create_node(label=obj_phrase, data=obj_data, node_category=node_category)
            self._add_wikidata_relations(obj_node, obj_data)

        if subj_node_is_relevant and obj_node_is_relevant:
            self.get_or_create_connection(
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
        # Pick first sense; if faulty, correct manually later
        sense_dates = node_data.get("senses", [])
        sense_data = {} if len(sense_dates) == 0 else sense_dates[0]
        if "claims" in sense_data:
            for claim, claim_data in sense_data["claims"].items():
                target, implies_relation, node_category, target_data = claim_data["target"], claim_data["implies_relation"], \
                                                         claim_data["entity_class"], claim_data["target_data"]
                if implies_relation and target != sense_data["label"]:
                    entity_class = self.get_node_class(node_category, base_classes=(Entity, ))
                    obj_node = self.get_or_create_node(label=target, data=target_data, node_category=entity_class)
                    self.get_or_create_connection(node, obj_node, label=claim, data={})

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
