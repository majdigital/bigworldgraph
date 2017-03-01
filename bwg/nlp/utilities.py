# -*- coding: utf-8 -*-
"""
Utilities for the NLP pipeline.
"""

# STD
import json

# PROJECT
from bwg.misc.helpers import filter_dict


# CONST
DEPENDENCY_TREE_KEEP_FIELDS = {
    "address", "ctag", "deps", "word", "head", "rel"
}


def serialize_ne_tagged_sentence(sentence_id, tagged_sentence, pretty=False):
    """
    Serialize a sentence tagged with Nnmed entitiy tags s.t. it can be passed between Luigi tasks.
    """
    if pretty:
        return json.dumps({sentence_id: tagged_sentence}, indent=4, sort_keys=True)
    return json.dumps({sentence_id: tagged_sentence})


def serialize_dependency_parse_tree(sentence_id, parse_trees, pretty=False):
    parse_tree = vars([tree for tree in parse_trees][0])
    simplified_tree = {
        "root": parse_tree["root"]["address"],
        "nodes": [
            filter_dict(node, DEPENDENCY_TREE_KEEP_FIELDS)
            for number, node in parse_tree["nodes"].items()
        ]
    }

    if pretty:
        return json.dumps({sentence_id: simplified_tree}, indent=4, sort_keys=True)
    return json.dumps({sentence_id: simplified_tree})
