# -*- coding: utf-8 -*-
"""
Module to run the API that connects the graph database to the frontend.
"""

# STD
import json
import logging
import traceback
import os
import codecs
import time

# EXT
from eve import Eve
import flask_cors
import luigi

# PROJECT
import bwg
from bwg.config_management import get_config_from_py_file, overwrite_local_config_with_environ
from bwg.neo4j_extensions import Neo4jLayer
from bwg.french_wikipedia.french_wikipedia_pipeline import FrenchRelationsDatabaseWritingTask
from bwg.french_wikipedia.french_wikipedia_config import NEO4J_USER, NEO4J_HOST, NEO4J_PASSWORD, FRENCH_DATABASE_CATEGORIES


def set_up_api(config_path="./api_config.py", log=True, screen_output=True, load_demo_data_func=lambda paths: None):
    """
    Set up the API using the following steps:

    1. Read the configuration file.
    2. Overwrite configuration parameters if corresponding environment variables exist.
    3. Initialize the logger.
    4. Create the API.
    5. Add error handlers to the API.
    6. Add additional endpoints to the API.
    7. Connect the API to the logger.

    :return: Completely set up API.
    :rtype: eve.Eve
    """
    # Init configuration
    api_config = get_config_from_py_file(config_path)
    api_config = overwrite_local_config_with_environ(api_config)

    if log:
        # Create logging directory
        logging_file = api_config["LOGGING_PATH"]
        logging_path = "/".join(logging_file.split("/")[:-1])
        if not os.path.exists(logging_path):
            os.makedirs(logging_path)

        # Init logger
        logging.basicConfig(
            filename=api_config["LOGGING_PATH"],
            filemode="w",
            level=api_config["LOGGING_LEVEL"],
            format="%(asctime)s %(levelname)s:%(message)s",
            datefmt="%d.%m.%Y %I:%M:%S"
        )

    if api_config["LOAD_DEMO_DATA"]:
        load_demo_data_func(
            paths={
                "DEMO_RELATIONS_PATH": api_config["DEMO_RELATIONS_PATH"],
                "DEMO_PROPERTIES_PATH": api_config["DEMO_PROPERTIES_PATH"],
                "DEMO_INFO_PATH": api_config["DEMO_INFO_PATH"]
            }
        )

    # Set up API
    api = Eve(data=Neo4jLayer, settings=api_config)
    flask_cors.CORS(api)
    api = add_error_handlers(api)
    api = add_additional_endpoints(api)

    if log:
        api = add_logger_to_app(api)

        if api.config["DEBUG"] and screen_output:
            logging.getLogger().addHandler(logging.StreamHandler())

        # Add callback functions
        api.on_post_GET += log_request
        api.on_post_PUT += log_request
        api.on_post_POST += log_request
        api.on_post_DELETE += log_request

    return api


def add_error_handlers(api):
    """
    Add error handlers to the current API.

    :param api: Current api.
    :type api: eve.Eve
    :return: API with additional error handlers.
    :rtype: eve.Eve
    """
    @api.errorhandler(Exception)
    def handle_api_error(error):
        """
        Handle an error without shutting the API down.

        :param error: Error that was thrown during the execution of the API.
        :type error: Exception
        :return: Friendly error message if DEBUG is false in API config.
        :rtype: dict
        """
        if hasattr(error, "msg"):
            logging.error("The following {} occurred: {}".format(type(error).__name__, error.msg))
        else:
            logging.error("A {} occurred: {}".format(type(error).__name__, traceback.format_exc()))

        if api.config["DEBUG"]:
            raise error

        return json.dumps(
            {
                "Sorry!": "There was an error. Please check your request or consult the project's GitHub page: "
                "https://github.com/majdigital/bigworldgraph."
            }
        )

    return api


def add_additional_endpoints(api):
    """
    Add additional endpoints to the current API.

    :param api: Current api.
    :type api: eve.Eve
    :return: API with additional error handlers.
    :rtype: eve.Eve
    """
    @api.route("/version")
    def version():
        """
        Return the version and some legal info about the API.

        :return: Information about the version as serialized response.
        :type: dict
        """
        return json.dumps(
            {
                "version": bwg.__version__,
                "license": "Copyright (c) 2019 Malabaristalicious Unipessoal, Lda.\nFor more information read "
                "LICENSE.md on https://github.com/majdigital/bigworldgraph"
            }
        )

    return api


def log_request(resource, request, payload):
    """
    Log a request on an endpoint.

    :param resource: Resource being called.
    :type resource: str
    :param request: Request information.
    :type request: dict
    :param payload: Request payload.
    :type payload: dict
    """
    logging.debug("{} request detected and answered on resource {}.".format(request.method, resource))


def add_logger_to_app(app):
    """
    Add logger to the current app.

    :param app: Current app.
    :type app: eve.Eve
    :return: App with logger.
    :rtype: eve.Eve
    """
    handler = logging.FileHandler(app.config["LOGGING_PATH"])
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(filename)s:%(lineno)d] -- ip: %(clientip)s, '
            'url: %(url)s, method:%(method)s'
        )
    )
    app.logger.setLevel(app.config["LOGGING_LEVEL"])
    app.logger.addHandler(handler)
    return app


def load_french_demo_data(paths):
    class FrenchDemoRelationsDatabaseWritingTask(FrenchRelationsDatabaseWritingTask):
        def requires(self):
            pass

        def input(self):
            return self.task_config["RELATIONS_PATH"], self.task_config["PROPERTIES_PATH"]

        def run(self):
            with codecs.open(self.input()[0], "r", "utf-8") as mr_file, \
                 codecs.open(self.input()[1], "r", "utf-8") as pc_file:
                entity_properties = self._read_properties_file(pc_file.readlines())
                with self.output() as database:
                    for mr_line in mr_file:
                        self.process_article(mr_line, database, entity_properties)

    assert "DEMO_RELATIONS_PATH" in paths
    assert "DEMO_PROPERTIES_PATH" in paths

    task_config = {
        "NEO4J_USER": NEO4J_USER,
        "NEO4J_PASSWORD": NEO4J_PASSWORD,
        "NEO4J_HOST": NEO4J_HOST,
        "DATABASE_CATEGORIES": FRENCH_DATABASE_CATEGORIES,
        "RELATIONS_PATH": paths["DEMO_RELATIONS_PATH"],
        "PROPERTIES_PATH": paths["DEMO_PROPERTIES_PATH"],
        "CORPUS_ENCODING": "utf-8"
    }
    task_config = overwrite_local_config_with_environ(task_config)

    logging.info("Adding sample data to the database.")
    luigi.build(
        [FrenchDemoRelationsDatabaseWritingTask(task_config=task_config)],
        local_scheduler=True, workers=1, log_level="INFO"
    )


if __name__ == "__main__":
    api_config_path = os.environ.get("API_CONFIG_PATH", os.path.dirname(__file__) + "/api_config.py")

    # TODO (Improvement): Find better solution for this [DU 07.08.17]
    time.sleep(20)  # Give neo4j container time to start up when using docker

    api = set_up_api(api_config_path, load_demo_data_func=load_french_demo_data)
    flask_cors.CORS(api)
    logging.info("API is being run now!")
    logging.debug(
        "API is going to run with the following settings:\n\t{}".format("\n\t".join(
            ["{}: {}".format(key, value) for key, value in api.config.items()]
        ))
    )
    api.run(use_reloader=False, host=api.config["API_HOST"])
