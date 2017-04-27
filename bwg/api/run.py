# -*- coding: utf-8 -*-
"""
Module to run the API that connects the graph database to the frontend
"""

# STD
import json

# EXT
from eve import Eve

# PROJECT
import bwg
from bwg.db.neo4j import Neo4jLayer

# TODO (Implement): Implement post-event-hook to make data more readable for frontend [DU 26.04.17]


api = Eve(data=Neo4jLayer)


@api.route("/version")
def version():
    return json.dumps(
        {
            "version": bwg.__version__,
            "license": "Copyright (c) 2017 Malabaristalicious Unipessoal, Lda.\nFor more information read LICENSE.md "
            "on https://github.com/majdigital/bigworldgraph"
        }
    )


if __name__ == "__main__":
    api.run()
