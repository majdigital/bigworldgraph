# -*- coding: utf-8 -*-
"""
Utilities for the NLP pipeline.
"""

# STD
from collections import defaultdict
import pkgutil
import json
import luigi
import inspect
import sys

# PROJECT
from bwg.misc.helpers import filter_dict
from pipeline_config import DEPENDENCY_TREE_KEEP_FIELDS


class TaskRequirementsFromConfigMixin(object):
    task_config = luigi.DictParameter()

    def requires(self):
        required_tasks = self.task_config["PIPELINE_DEPENDENCIES"]
        requirements = [
            self._get_task_cls_from_str(required_task)(task_config=self.task_config)
            for required_task in required_tasks
        ]
        if len(requirements) == 1:
            return requirements[0]
        return requirements

    def _get_task_cls_from_str(self, cls_str):
        """
        Turn a string of a Luigi Task class into an actual type.
        """
        package_name = ".".join(__name__.split(".")[:-1])
        module_classes = self._load_task_classes(package_name)

        try:
            return module_classes[cls_str]
        except:
            raise KeyError(
                "No task class called '{}' found in any module of package {}.".format(cls_str, package_name)
            )

    @staticmethod
    def _load_task_classes(package):
        """
        Load all the classes in all the modules of a package.
        """
        module_names = []
        classes = {}

        for importer, module_name, ispkg in pkgutil.iter_modules("../"):
            module_names.append(package + "." + module_name)

        for module_name in module_names:
            __import__(module_name)
            classes.update(
                {
                    module_class_name: module_class
                    for module_class_name, module_class in inspect.getmembers(sys.modules[module_name], inspect.isclass)
                    if module_class_name.endswith("Task")
                }
            )

        return classes


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
            int(number): filter_dict(node, DEPENDENCY_TREE_KEEP_FIELDS)
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


def deserialize_dependency_tree(line):
    """
    Convert dependency node addresses from string to integers.
    """
    sentence_id, raw_tree = deserialize_line(line)
    final_tree = dict({"root": raw_tree["root"]})

    final_tree["nodes"] = {
            int(address): node
            for address, node in raw_tree["nodes"].items()
        }

    return sentence_id, final_tree


def get_serialized_dependency_tree_connections(serialized_dependency_tree):
    """
    Extract the connection from a dependency parse tree.
    """
    connections = defaultdict(set)

    nodes = serialized_dependency_tree["nodes"]
    for address, node in nodes.items():
        if address == 0:
            continue

        if node["head"] is not None:
            connections[address].add(node["head"])

        for dependency, target_nodes in node["deps"].items():
            if dependency == "rel":
                continue

            for target_node in target_nodes:
                connections[address].add(target_node)

    return connections
