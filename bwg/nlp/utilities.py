# -*- coding: utf-8 -*-
"""
Utilities for the NLP pipeline.
"""

# STD
import json
import abc

# PROJECT
from bwg.misc.helpers import filter_dict
from pipeline_config import DEPENDENCY_TREE_KEEP_FIELDS


class TaskWorkflowMixin:
    """
    Enable Luigi tasks to process single lines as well as articles or other input types.
    """
    task_config = None

    @abc.abstractmethod
    def task_workflow(self, target_object, **workflow_kwargs):
        """
        Define the tasks workflow here - it usually includes extracting necessary resources from workflow_kwargs,
        performing the actual task on the sentence and wrapping all the arguments for the serializing function in a
        dictionary, returning it in the end.
        """
        return {}

    def process_line(self, line, workflow_kwargs, new_state, serializing_function, output_file, pretty=False):
        """
        Process line from the input and apply this task's workflow. Serialize the result afterwards and finally write
        it to the output file.
        """
        # TODO (Refactor): Make it possible to a variable number of lines
        corpus_encoding = self.task_config["CORPUS_ENCODING"]
        line_object = deserialize_line(line, corpus_encoding)
        meta, data = line_object["meta"], line_object["data"]

        # Determine if it's just one line or an article, proceed accordingly
        if meta["type"] == "article":
            # Apply workflow to every sentence in article
            sentences = {}
            sentence_dicts = [
                serializing_function(
                    **self.task_workflow(sentence, **workflow_kwargs), state=new_state, pretty=pretty, dump=False
                )
                for sentence_id, sentence in data.items()
            ]

            # Aggregate them
            for sentence_dict in sentence_dicts:
                sentences.update(sentence_dict)

            # Preserve article structure
            output_file.write(
                serialize_article(
                    meta["id"], meta["url"], meta["title"], sentences,
                    from_scratch=False, pretty=pretty, state=new_state
                )
            )

        elif meta["type"] == "sentence":
            serializing_args = self.task_workflow(line_object)
            output_file.write("{}\n".format(serializing_function(**serializing_args)))

        else:
            raise TypeError("Unknown input data type '{}'.".format(meta["type"]))


def serialize_tagged_sentence(sentence_id, tagged_sentence, state="raw", pretty=False, dump=True):
    """
    Serialize a sentence tagged with Nnmed entitiy tags s.t. it can be passed between Luigi tasks.
    """
    options = {"ensure_ascii": False}

    if pretty:
        options.update({"indent": 4, "sort_keys": True})

    serialized_tagged_sentence = {
        sentence_id: {
            "meta": {
                "id": sentence_id,
                "type": "sentence",
                "state": state
            },
            "data": tagged_sentence
        }
    }

    if dump:
        return json.dumps(serialized_tagged_sentence, **options)

    return serialized_tagged_sentence


def serialize_dependency_parse_tree(sentence_id, parse_trees, state="raw", pretty=False, dump=True):
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

    serialized_dependency_parse_tree = {
        sentence_id: {
            "meta": {
                "id": sentence_id,
                "state": state,
                "type": "sentence"
            },
            "data": simplified_tree
        }
    }

    if dump:
        return json.dumps(serialized_dependency_parse_tree, **options)

    return serialized_dependency_parse_tree


def serialize_relation(sentence_id, subj_phrase, verb, obj_phrase, sentence, state="raw", pretty=False, dump=True):
    """
    Serialize an extracted relation.
    """
    options = {"ensure_ascii": False}

    if pretty:
        options["indent"] = 4

    serialized_relation = {
        sentence_id: {
            "meta": {
                "id": sentence_id,
                "state": state,
                "type": "sentence"
            },
            "data": {
                "subject_phrase": subj_phrase,
                "verb_phrase": verb,
                "object_phrase": obj_phrase,
                "sentence": sentence
            }
        }
    }

    if dump:
        return json.dumps(serialized_relation, **options)

    return serialized_relation


def serialize_article(article_id, article_url, article_title, sentences, state="raw", from_scratch=True, pretty=False,
                      dump=True):
    """
    Serialize a Wikipedia article.
    """
    options = {"ensure_ascii": False}

    if pretty:
        options["indent"] = 4

    if from_scratch:
        sentences = {
            "{}/{}".format(article_id, str(sentence_id).zfill(5)): {
                "meta": {
                    "id": "{}/{}".format(article_id, str(sentence_id).zfill(5)),
                    "type": "sentence",
                    "state": state
                },
                "data": sentence
            }
            for sentence, sentence_id in zip(sentences, range(1, len(sentences) + 1))
        }

    serialized_article = {
        article_id: {
            "meta": {
                "id": article_id,
                "url": article_url,
                "title": article_title,
                "type": "article",
                "state": state
            },
            "data": sentences
        },
    }

    if dump:
        return json.dumps(serialized_article, **options)

    return serialized_article


def deserialize_line(line, encoding="utf-8"):
    """
    Transform a line in a file that was created as a result from a Luigi task into its metadata and main data.
    """
    json_object = json.loads(line, encoding=encoding)
    return list(json_object.values())[0]


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
