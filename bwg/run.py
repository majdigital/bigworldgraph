# -*- coding: utf-8 -*-
"""
Module to run the API that connects the graph database to the frontend
"""

# STD
import json
import logging
import traceback

# EXT
from eve import Eve

# PROJECT
import bwg
from bwg.helpers import get_config_from_py_file, overwrite_local_config_with_environ
from bwg.neo4j_extensions import Neo4jLayer

# Init configuration
api_config = get_config_from_py_file("settings.py")
api_config = overwrite_local_config_with_environ(api_config)

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

if api.config["DEBUG"]:
    logging.getLogger().addHandler(logging.StreamHandler())


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
            "license": "Copyright (c) 2017 Malabaristalicious Unipessoal, Lda.\nFor more information read LICENSE.md "
            "on https://github.com/majdigital/bigworldgraph"
        }
    )


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


# Add callback functions
api.on_post_GET += log_request
api.on_post_PUT += log_request
api.on_post_POST += log_request
api.on_post_DELETE += log_request


def add_logger_to_app(app_):
    """
    Add logger to the current app.
    
    :param app_: Current app.
    :type app_: Eve.eve
    :return: App with logger.
    :rtype: Eve.eve
    """
    handler = logging.FileHandler(app_.config["LOGGING_PATH"])
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(filename)s:%(lineno)d] -- ip: %(clientip)s, '
            'url: %(url)s, method:%(method)s'
        )
    )
    app_.logger.setLevel(app_.config["LOGGING_LEVEL"])
    app_.logger.addHandler(handler)
    return app_


if __name__ == "__main__":
    logging.info("API is being run now!")
    logging.debug(
        "API is going to run with the following settings:\n\t{}".format("\n\t".join(
            ["{}: {}".format(key, value) for key, value in api.config.items()]
        ))
    )
    api = add_logger_to_app(api)
    api.run(use_reloader=False)
