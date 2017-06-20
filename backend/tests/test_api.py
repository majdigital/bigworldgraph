# -*- coding: utf-8 -*-
"""
Testing functions API endpoints and API related functionalities.
"""

# STD
import json
import unittest
import codecs
import datetime
import os

# EXT
import neomodel

# PROJECT
import bwg
from bwg.api_config import (
    DOMAIN, NEO4J_HOST, NEO4J_PASSWORD, NEO4J_PORT, NEO4J_USER
)
from bwg.run_api import set_up_api
from bwg.neo4j_extensions import Neo4jDatabase
from .test_neo4j_extensions import Neo4jTestMixin
from .toolkit import make_api_request


class APIEndpointTestCase(unittest.TestCase, Neo4jTestMixin):
    """
    Testing API endpoints and defined method on these same endpoints.
    """
    def setUp(self):
        os.environ["DEBUG"] = str(False)
        self.neo4j_database = Neo4jDatabase(user=NEO4J_USER, password=NEO4J_PASSWORD, host=NEO4J_HOST, port=NEO4J_PORT)
        neomodel.util.logger.setLevel("WARNING")
        self.reset_database()
        self.create_and_connect_nodes()
        self.api = set_up_api(config_path="../bwg/api_config.py", log=False, screen_output=False)
        self.api = self.api.test_client()

    def tearDown(self):
        del self.api
        self.reset_database()

    def test_endpoints_get(self):
        for endpoint, endpoint_data in DOMAIN.items():
            if "GET" in endpoint_data["resource_methods"]:
                response = make_api_request(self.api, "GET", "/" + endpoint)
                assert response._status_code == 200

                content = json.loads(response.data, encoding="utf-8")
                assert "nodes" in content["_items"][0]
                assert "links" in content["_items"][0]

                # Do further testing of necessary
                if hasattr(self, "test_endpoints_get_" + endpoint):
                    getattr(self, "_test_endpoints_get_" + endpoint)()

    def _test_endpoints_get_entities(self):
        response = make_api_request(self.api, "GET", "/entities")
        assert response._status_code == 200

        content = json.loads(response.data, encoding="utf-8")
        nodes, links = content["_items"][0]["nodes"], content["_items"][0]["links"]
        assert len(nodes) == 4
        assert len(links) == 3

    def test_endpoints_delete(self):
        # TODO (Implement): Implement this as soon as DELETE is supported [DU 20.07.17]
        pass

    def test_endpoints_put(self):
        # TODO (Implement): Implement this as soon as PUT is supported [DU 20.07.17]
        pass

    def test_endpoints_post(self):
        # TODO (Implement): Implement this as soon as POST is supported [DU 20.07.17]
        pass

    def test_version_endpoints(self):
        response = make_api_request(self.api, "GET", "/version")
        assert response._status_code == 200
        content = json.loads(response.data, encoding="utf-8")
        assert content["version"] == bwg.__version__
        current_year = datetime.datetime.now().year
        assert str(current_year) in content["license"]


class APIAdditionalFunctionsTestCase(unittest.TestCase):
    """
    Testing additional API functions.
    """
    def setUp(self):
        self.logging_path = "./test.log"
        neomodel.util.logger.setLevel("WARNING")

        os.environ["LOGGING_PATH"] = self.logging_path
        os.environ["DEBUG"] = str(True)

        self.api = set_up_api(config_path="../bwg/api_config.py", log=True, screen_output=False)
        self.api = self.api.test_client()

    def tearDown(self):
        os.remove(self.logging_path)

    def test_logging(self):
        make_api_request(self.api, "GET", "/entities")

        assert os.path.isfile(self.logging_path)
        with codecs.open(self.logging_path, "r", "utf-8") as log_file:
            log_lines = log_file.readlines()
            assert any([
                "GET request detected and answered on resource entities." in line
                for line in log_lines
            ])
