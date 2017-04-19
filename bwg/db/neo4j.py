# -*- coding: utf-8 -*-
"""
Create support for the Neo4j graph database.
"""

# EXT
import luigi
import neomodel


class Entity(neomodel.StructuredNode):
    # TODO (Implement) [DU 19.04.17]
    pass


class Neo4jTarget(luigi.Target):
    """
    Additional luigi target to write a tasks output into a neo4j graph database.
    """
    mode = None

    def __init__(self, user, password, host="localhost", port=7687):
        neomodel.config.DATABASE_URL = "bolt://{user}:{password}@{host}:{port}".format(
            user=user, password=password, host=host, port=port
        )

    def exists(self):
        # TODO (Implement) [DU 19.04.17]
        # Find way to not overwrite data each time
        return False

    def open(self, mode):
        assert mode in ("w", "a")
        self.mode = mode

        # Overwrite database
        if mode == "w":
            self._delete_all_entries()

        return self

    @staticmethod
    def _delete_all_entries():
        entities = Entity.nodes.get()

        for entity in entities:
            entity.delete()
