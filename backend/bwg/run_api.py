# -*- coding: utf-8 -*-
"""
Module to run the API that connects the graph database to the frontend.
"""

# STD
import json
import logging
import traceback
import os

# EXT
from eve import Eve
import flask_cors

# PROJECT
import bwg
from bwg.helpers import get_config_from_py_file, overwrite_local_config_with_environ
from bwg.neo4j_extensions import Neo4jLayer


def set_up_api():
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
    api_config = get_config_from_py_file("./api_config.py")
    api_config = overwrite_local_config_with_environ(api_config)

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

    # Set up API
    api = Eve(data=Neo4jLayer, settings=api_config)
    api = add_error_handlers(api)
    api = add_additional_endpoints(api)
    api = add_logger_to_app(api)

    if api.config["DEBUG"]:
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
            logging.error("A {} occured: {}".format(type(error).__name__, traceback.format_exc()))

        if api.config["DEBUG"]:
            raise error

        return json.dumps(
            {
                "Sorry!": "There was an error. Please check your request or consult the projects GitHub page: "
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
                "license": "Copyright (c) 2017 Malabaristalicious Unipessoal, Lda.\nFor more information read "
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


if __name__ == "__main__":
    api = set_up_api()
    flask_cors.CORS(api)
    logging.info("API is being run now!")
    logging.debug(
        "API is going to run with the following settings:\n\t{}".format("\n\t".join(
            ["{}: {}".format(key, value) for key, value in api.config.items()]
        ))
    )
    api.run(use_reloader=False, host=api.config["API_HOST"])
