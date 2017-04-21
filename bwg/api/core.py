# -*- coding: utf-8 -*-
"""
Module to run the API that connects the graph database to the frontend
"""

# EXT
from eve import Eve

# PROJECT
from bwg.misc.helpers import get_config_from_py_file


def setup_api(config_path):
    config = get_config_from_py_file(config_path)
    api = Eve(config=config)
    api.run()


if __name__ == "__main__":
    setup_api(config_path="../../api_config.py")
