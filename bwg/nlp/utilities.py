# -*- coding: utf-8 -*-
"""
Utilities for the NLP pipeline.
"""

# STD
import json
import functools
import time

# PROJECT
from bwg.misc.helpers import filter_dict, is_collection
from pipeline_config import DEPENDENCY_TREE_KEEP_FIELDS


def serialize_tagged_sentence(sentence_id, tagged_sentence, state="raw", pretty=False, dump=True):
    """
    Serialize a sentence tagged with Named entity tags s.t. it can be passed between Luigi tasks.
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

    if type(parse_trees) != dict:
        if len(parse_trees) == 0:
            empty_tree = {
                sentence_id: {
                    "meta": {
                        "id": sentence_id,
                        "state": state,
                        "type": "sentence"
                    },
                    "data": {
                        "root": None,
                        "nodes": {}
                    }
                }
            }

            if dump:
                return json.dumps(empty_tree, **options)
            return empty_tree

        parse_tree = vars([tree for tree in parse_trees][0])
    else:
        parse_tree = parse_trees

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


def serialize_relation(sentence_id, sentence, relations, state="raw", infix="", pretty=False, dump=True):
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
                "sentence": sentence,
                "relations": {
                    "{}/{}{}".format(sentence_id, infix, str(relation_id).zfill(5)): {
                        "meta": {
                            "id": "{}/{}{}".format(sentence_id, infix, str(relation_id).zfill(5)),
                            "state": state,
                            "type": "sentence"
                        },
                        "data": {
                            "subject_phrase": subj_phrase,
                            "verb": verb,
                            "object_phrase": obj_phrase
                        }
                    }
                    for (subj_phrase, verb, obj_phrase), relation_id in zip(relations, range(1, len(relations) + 1))
                }
            }
        }
    }

    if dump:
        return json.dumps(serialized_relation, **options)

    return serialized_relation


def serialize_wikidata_entity(sentence_id, wikidata_entities, infix="", state="raw", pretty=False, dump=True):
    """
    Serialize relevant information of a Wikidata entity.
    """
    options = {"ensure_ascii": False}

    if pretty:
        options["indent"] = 4

    serialized_entity = {
        "meta": {
            "id": sentence_id,
            "state": state,
            "type": "wikidata_entity"
        },
        "data": {
            "entities": {
                "{}/{}{}".format(sentence_id, infix, str(wd_entity_id).zfill(5)): {
                    "meta": {
                        "id": "{}/{}{}".format(sentence_id, infix, str(wd_entity_id).zfill(5)),
                        "state": state,
                        "type": "Wikidata entity" if len(wd_entity) == 1 else "Ambiguous Wikidata entity"
                    },
                    "data": wd_entity
                }
                for wd_entity, wd_entity_id in zip(wikidata_entities, range(1, len(wikidata_entities) + 1))
            }
        }
    }

    if dump:
        return json.dumps(serialized_entity, **options)

    return serialized_entity


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
        "meta": {
            "id": article_id,
            "url": article_url,
            "title": article_title,
            "type": "article",
            "state": state
        },
        "data": sentences
    }

    if dump:
        return json.dumps(serialized_article, **options)

    return serialized_article


def get_nes_from_sentence(sentence_data, default_ne_tag, include_tag=False):
    """
    Extract all named entities from a named entity tagged sentence.
    """
    def add_ne(nes_, current_ne_, current_ne_tag_, include_tag_):
        ne = " ".join(current_ne_)
        to_add = ne if not include_tag_ else (ne, current_ne_tag_)
        nes_.append(to_add)
        return nes_

    nes = []
    current_ne = []
    current_ne_tag = ""

    for word, ne_tag in sentence_data:
        # Start of named entity
        if ne_tag != default_ne_tag and not current_ne:
            current_ne.append(word)
            current_ne_tag = ne_tag

        # End of named entity
        elif ne_tag == default_ne_tag and current_ne:
            nes = add_ne(nes, current_ne, current_ne_tag, include_tag)
            current_ne = []
            current_ne_tag = ""

        # Decide if named entity is ongoing or not
        elif ne_tag != default_ne_tag and current_ne:
            # New named entity
            if current_ne_tag == ne_tag:
                current_ne.append(word)
            # New named entity
            else:
                nes = add_ne(nes, current_ne, current_ne_tag, include_tag)
                current_ne = [word]
                current_ne_tag = ne_tag

    return nes


def just_dump(json_object, pretty=False):
    """
    Self-documenting?
    """
    options = {"ensure_ascii": False}

    if pretty:
        options["indent"] = 4

    return json.dumps(json_object, **options)


def deserialize_line(line, encoding="utf-8"):
    """
    Transform a line in a file that was created as a result from a Luigi task into its metadata and main data.
    """
    return json.loads(line, encoding=encoding)


def retry_with_fallback(triggering_error, **fallback_kwargs):
    """
    Rerun a function in case a specific error occurs with new arguments.
    """
    def decorator(func):
        """
        Actual decorator
        """
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            try:
                function_result = func(*args, **kwargs)
            except triggering_error:
                kwargs.update(fallback_kwargs)
                function_result = func(*args, **kwargs)

            return function_result

        return func_wrapper

    return decorator


def retry_when_exception(triggering_error, max_times=10):
    """
    Rerun a function if a specific error occurs.
    """
    def decorator(func):
        """
        Actual decorator.
        """
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            unsuccessful_tries = 0

            while True:
                try:
                    function_result = func(*args, **kwargs)
                    break
                except triggering_error:
                    unsuccessful_tries += 1
                    if unsuccessful_tries > max_times:
                        raise
                    time.sleep(0.5)

            return function_result

        return func_wrapper

    return decorator
