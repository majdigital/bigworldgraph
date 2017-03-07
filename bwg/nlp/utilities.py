# -*- coding: utf-8 -*-
"""
Utilities for the NLP pipeline.
"""

# STD
import pkgutil
import json
import luigi
import inspect
import sys
import uuid

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


def serialize_tagged_sentence(sentence_id, tagged_sentence, pretty=False):
    """
    Serialize a sentence tagged with Nnmed entitiy tags s.t. it can be passed between Luigi tasks.
    """
    options = {"ensure_ascii": False}

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
    options = {"ensure_ascii": False}

    parse_tree = vars([tree for tree in parse_trees][0])
    simplified_tree = {
        "root": parse_tree["root"]["address"],
        "nodes": {
            int(number): filter_dict(node, DEPENDENCY_TREE_KEEP_FIELDS)
            for number, node in parse_tree["nodes"].items()
        }
    }

    if pretty:
        options["indent"] = 4

    return json.dumps(
        {
            "sentence_id": sentence_id,
            "data": simplified_tree
        },
        **options
    )


def serialize_relation(sentence_id, subj_phrase, verb, obj_phrase, sentence, pretty=False):
    """
    Serialize an extracted relation.
    """
    options = {"ensure_ascii": False}

    if pretty:
        options["indent"] = 4

    return json.dumps(
        {
            "sentence_id": sentence_id,
            "data": {
                "subject_phrase": subj_phrase,
                "verb_phrase": verb,
                "object_phrase": obj_phrase,
                "sentence": sentence
            }
        },
        **options
    )


def serialize_article(article_id, article_url, article_title, sentences, article_state="raw", pretty=False):
    options = {"ensure_ascii": False}

    if pretty:
        options["indent"] = 4

    return json.dumps(
        {
            "meta": {
                "id": article_id,
                "url": article_url,
                "title": article_title,
                "state": article_state
            },
            "data": {
                "{}/{}".format(article_id, str(sentence_id).zfill(5)): sentence
                for sentence, sentence_id in zip(sentences, range(1, len(sentences)+1))
            }
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
    final_tree = dict(root=raw_tree["root"])

    final_tree["nodes"] = {
            int(address): node
            for address, node in raw_tree["nodes"].items()
        }

    return sentence_id, final_tree
