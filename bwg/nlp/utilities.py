# -*- coding: utf-8 -*-
"""
Utilities for the NLP pipeline.
"""

# STD
from collections import defaultdict
import json

# PROJECT
from bwg.misc.helpers import filter_dict
from pipeline_config import DEPENDENCY_TREE_KEEP_FIELDS


def serialize_ne_tagged_sentence(sentence_id, tagged_sentence, pretty=False):
    """
    Serialize a sentence tagged with Nnmed entitiy tags s.t. it can be passed between Luigi tasks.
    """
    options = {}

    if pretty:
        options.update({"indent": 4, "sort_keys": True})

    return json.dumps(
        {
            "sentence_id": sentence_id,
            "data": tagged_sentence
        },
        **options
    )


def serialize_dependency_parse_tree(sentence_id, parse_trees, pretty=False):
    """
    Serialize a dependency parse tree for a sentence.
    """
    options = {}
    parse_tree = vars([tree for tree in parse_trees][0])
    simplified_tree = {
        "root": parse_tree["root"]["address"],
        "nodes": {
            number: filter_dict(node, DEPENDENCY_TREE_KEEP_FIELDS)
            for number, node in parse_tree["nodes"].items()
        }
    }

    if pretty:
        options.update({"indent": 4, "sort_keys": True})

    return json.dumps(
        {
            "sentence_id": sentence_id,
            "data": simplified_tree
        },
        **options
    )


def deserialize_line(line):
    """
    Transform a line in a file that was created as a result from a Luigi task into a sentence id and sentence data.
    """
    json_object = json.loads(line)
    return json_object["sentence_id"], json_object["data"]


def get_serialized_dependency_tree_connections(serialized_dependency_tree):
    """
    Extract the connection from a dependency parse tree.
    """
    connections = defaultdict(set)

    nodes = serialized_dependency_tree["nodes"]
    for number, node in nodes.items():
        if number == 0:
            continue

        if node["head"] is not None:
            connections[number].add(node["head"])

        for dependency, target_nodes in node["deps"].items():
            if dependency == "rel":
                continue

            for target_node in target_nodes:
                connections[number].add(target_node)

    return connections


