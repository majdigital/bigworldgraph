# -*- coding: utf-8 -*-
"""
Module to run the API that connects the graph database to the frontend
"""

# EXT
from eve import Eve
from eve_neo4j import Neo4j as Eve_neo4j
import flask_restful

# PROJECT
import bwg
from bwg.misc.helpers import get_config_from_py_file


def setup_api(config_path):
    config = get_config_from_py_file(config_path)
    api = Eve(config=config, data=Eve_neo4j)
    api.add_resource(Version, "/version")
    api.run()


class Version(flask_restful.Resource):
    def get(self):
        return {"version": bwg.__version__}


if __name__ == "__main__":
    setup_api(config_path="../../api_config.py")

