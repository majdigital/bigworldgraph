# -*- coding: utf-8 -*-
"""
Create support for the Neo4j graph database.
"""

# EXT
import luigi
import neo4j.v1 as neo4j


class Neo4jSession:
    """
    Context manager to handle connections to a Neo4j graph database.
    """
    def __init__(self, uri, user, password):
        self.driver = neo4j.GraphDatabase.driver(uri, auth=neo4j.basic_auth(user, password))
        self.session = self.driver.session()

    def __enter__(self):
        self.session = self.driver.session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


class Neo4jTarget(luigi.target):
    """
    Additional luigi target to write a tasks output into a neo4j graph database.
    """
    mode = None

    def __init__(self, uri, user, password, schemata):
        self.uri = uri
        self.user = user
        self.password = password
        self.schemata = schemata

    def exists(self):
        # TODO (Implement) [DU 19.04.17]
        return

    def open(self, mode):
        assert mode in ("w", "a")
        self.mode = mode
        return self

    def add_entry(self, schema_name, entry_data):
        assert type(entry_data) == dict

        try:
            schema = self.schemata[schema_name]
        except KeyError:
            raise KeyError("No schema named '{}' found.".format(schema_name))

        with Neo4jSession as session:
            session.run("CREATE {}".format(schema), entry_data)
