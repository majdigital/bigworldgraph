# -*- coding: utf-8 -*-
"""
Utilities for the NLP pipeline.
"""

# STD
import functools
import json

# PROJECT
from bwg.pipeline_config import DEPENDENCY_TREE_KEEP_FIELDS
from bwg.helpers import filter_dict


def serialize_tagged_sentence(sentence_id, tagged_sentence, state="raw", pretty=False, dump=True):
    """
    Serialize a sentence tagged with Named entity tags s.t. it can be passed between Luigi tasks.
    
    :param sentence_id: ID of current sentence.
    :type sentence_id: int
    :param tagged_sentence: Tagged sentence.
    :type tagged_sentence: list
    :param state: State that describes the kind of processing that is applied to the data in this step. It's 
    included in the metadata of each sentence.
    :type state: str
    :param pretty: Flag to indicate whether the output should be pretty-printed.
    :type pretty: bool
    :param dump: Flag to indicate whether the serialized data should already be dumped.
    :type dump: bool
    :return: Serialized (and maybe dumped) data.
    :rtype: str, dict
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
    
    :param sentence_id: ID of current sentence.
    :type sentence_id: int
    :param parse_trees: Parse trees for this sentence.
    :type parse_trees: dict, None
    :param state: State that describes the kind of processing that is applied to the data in this step. It's 
    included in the metadata of each sentence.
    :type state: str
    :param pretty: Flag to indicate whether the output should be pretty-printed.
    :type pretty: bool
    :param dump: Flag to indicate whether the serialized data should already be dumped.
    :type dump: bool
    :return: Serialized (and maybe dumped) data.
    :rtype: str, dict
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


def serialize_sentence(sentence_id, sentence, state="raw", pretty=False, dump=True):
    """
   Serialize a simple sentence.

   :param sentence_id: ID of current sentence.
   :type sentence_id: str
   :param sentence: Sentence.
   :type sentence: str
   :param state: State that describes the kind of processing that is applied to the data in this step. It's 
   included in the metadata of each sentence.
   :type state: str
   :param pretty: Flag to indicate whether the output should be pretty-printed.
   :type pretty: bool
   :param dump: Flag to indicate whether the serialized data should already be dumped.
   :type dump: bool
   :return: Serialized (and maybe dumped) data.
   :rtype: str, dict
   """
    options = {"ensure_ascii": False}

    if pretty:
        options["indent"] = 4

    serialized_sentence = {
        sentence_id: {
            "meta": {
                "id": sentence_id,
                "state": state,
                "type": "sentence"
            },
            "data": sentence
        }
    }

    if dump:
        return json.dumps(serialized_sentence, **options)

    return serialized_sentence


def serialize_relation(sentence_id, sentence, relations, state="raw", infix="", pretty=False, dump=True):
    """
    Serialize an extracted relation.
    
    :param sentence_id: ID of current sentence.
    :type sentence_id: str
    :param sentence: Sentence.
    :type sentence: str
    :param relations: Extracted relations.
    :type relations: list
    :param infix: Infix for relation ID.
    :type infix: str
    :param state: State that describes the kind of processing that is applied to the data in this step. It's 
    included in the metadata of each sentence.
    :type state: str
    :param pretty: Flag to indicate whether the output should be pretty-printed.
    :type pretty: bool
    :param dump: Flag to indicate whether the serialized data should already be dumped.
    :type dump: bool
    :return: Serialized (and maybe dumped) data.
    :rtype: str, dict
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
    
    :param sentence_id: ID of current sentence.
    :type sentence_id: int
    :param wikidata_entities: List of Wikidata entities in a certain sentence.
    :type wikidata_entities: list
    :param infix: Infix for Wikidata entity ID.
    :type infix: str
    :param state: State that describes the kind of processing that is applied to the data in this step. It's 
    included in the metadata of each sentence.
    :type state: str
    :param pretty: Flag to indicate whether the output should be pretty-printed.
    :type pretty: bool
    :param dump: Flag to indicate whether the serialized data should already be dumped.
    :type dump: bool
    :return: Serialized (and maybe dumped) data.
    :rtype: str, dict
    """
    options = {"ensure_ascii": False}

    if pretty:
        options["indent"] = 4

    serialized_entity = {
        sentence_id: {
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
    }

    if dump:
        return json.dumps(serialized_entity, **options)

    return serialized_entity


def serialize_article(article_id, article_url, article_title, sentences, state="raw", from_scratch=True, pretty=False,
                      dump=True):
    """
    Serialize a Wikipedia article.
    
    :param article_id: ID of current article.
    :type article_id: str
    :param article_url: URL of current article.
    :type article_url: str
    :param article_title: Title of current article.
    :type article_title: str
    :param sentences: Sentences of current article.
    :type sentences: list, dict
    :param state: State that describes the kind of processing that is applied to the data in this step. It's 
    included in the metadata of each sentence.
    :type state: str
    :param from_scratch: Flag to indicate whether sentences IDs and metadata should be created from scratch.
    :type from_scratch: bool
    :param pretty: Flag to indicate whether the output should be pretty-printed.
    :type pretty: bool
    :param dump: Flag to indicate whether the serialized data should already be dumped.
    :type dump: bool
    :return: Serialized (and maybe dumped) data.
    :rtype: str, dict
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
    
    :param sentence_data: Tagged sentence data.
    :type sentence_data: list
    :param default_ne_tag: Default Named Entity tag for words that are not Named Entities.
    :type default_ne_tag: str
    :param include_tag: Flag to indicate whether the Named entity tag should be included.
    :type include_tag: bool
    :return: Extracted Named Entities.
    :rtype: list
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
    
    :param json_object: Serialized JSON object
    :type json_object: dict
    :param pretty: Prettify the JSON object.
    :type pretty: bool
    :return: Dumped JSON object.
    :rtype: str
    """
    options = {"ensure_ascii": False}

    if pretty:
        options["indent"] = 4

    return json.dumps(json_object, **options)


def deserialize_line(line, encoding="utf-8"):
    """
    Transform a line in a file that was created as a result from a Luigi task into its metadata and main data.
    
    :param line: Line to be serialized.
    :type line: str
    :param encoding: Encoding of line (default is utf-8).
    :type encoding: str
    """
    return json.loads(line, encoding=encoding)


def retry_with_fallback(triggering_error, **fallback_kwargs):
    """
    Rerun a function in case a specific error occurs with new arguments.
    
    :param triggering_error: Error class that triggers the decorator to re-run the function.
    :type triggering_error: Exception
    :param fallback_kwargs: Fallback named arguments that are applied when the function is re-run.
    :type fallback_kwargs: dict
    :return: Decorator.
    :rtype: func
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
