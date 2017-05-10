# -*- coding: utf-8 -*-
"""
Module to run the API that connects the graph database to the frontend
"""

# STD
import json

# EXT
from eve import Eve
import flask_cors

# PROJECT
import bwg
from bwg.helpers import get_config_from_py_file, overwrite_local_config_with_environ
from bwg.neo4j_extensions import Neo4jLayer


api_config = get_config_from_py_file("settings.py")
api_config = overwrite_local_config_with_environ(api_config)
api = Eve(data=Neo4jLayer, settings=api_config)
flask_cors.CORS(api)


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
