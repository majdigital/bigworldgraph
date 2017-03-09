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


class ArticleProcessingMixin:
    """
    Enable Luigi tasks to process single lines as well as articles or other input types.
    """
    task_config = None

    @abc.abstractmethod
    def task_workflow(self, article, **workflow_kwargs):
        """
        Define the tasks workflow here - it usually includes extracting necessary resources from workflow_kwargs,
        performing the actual task on the sentence and wrapping all the arguments for the serializing function in a
        dictionary, returning it in the end.

        The input is considered an article, e.g. some text that consists of a variable number of sentences. Here's a
        proposal how to fit real world media types to this requirement:
            * Wikipedia article: Intuitive. If you want want to work with the articles subsection, treat them as small
                                 articles themselves.
            * Newspaper article: Same intuition as above.
            * Books: Treat chapters as articles.
            * Single paragraphs of text: Treat as articles that may not contain a headline.
            * Single sentence: Treat as single paragraph with only one "data" entry.
            * Pictures, tables, movies: Implement another workflow and also another Pipeline? This one is only for
                                        (written) natural language.
        """
        # Do main work here, e.g. iterating through every sentence in an articles "data" dict, performing a specific
        # task.
        for sentence_id, sentence in article["data"]:
            # https://www.youtube.com/watch?v=HL1UzIK-flA
            pass

        # Afterwards, put all the arguments for the corresponding serializing function into a dict and return it.
        serializing_kwargs = {}

        return serializing_kwargs

    def process_articles(self, raw_articles, workflow_kwargs, new_state, serializing_function, output_file,
                         pretty=False):
        """
        Process line from the input and apply this task's workflow. Serialize the result afterwards and finally write
        it to the output file.
        """
        article = self._combine_articles(raw_articles)

        # Main processing
        serializing_kwargs = self.task_workflow(article, **workflow_kwargs)
        serialized_article = serializing_function(**serializing_kwargs, state=new_state, pretty=pretty)

        # Output
        output_file.write("{}\n".format(serialized_article))

    def _combine_articles(self, raw_articles):
        """
        Combine multiple articles into one data structure, if necessary.

        Example:
            article1 = {
                "meta": {
                    "id": "0001",
                    "type:": "article",
                    "state": "pos_tagged",
                    ...
                },
                "data": {
                    "0001/0001": {
                        "meta": {...},
                        "data": {...}
                    },
                    ...
                }
            }

            article2 = {
                "meta": {
                    "id": "0001",
                    "type": "article",
                    "state": "dependency_parsed",
                    ...
                },
                "data": {...}
            }

            == is combined to ==>

            combined_article = {
                "meta": {
                    "id": "0001",
                    "type": "article",
                    "state": "pos_tagged | dependency_parsed",
                    ...
                },
                "data": {
                    "0001/0001": {
                        "meta": {...},
                        "data": {
                            "data_pos_tagged": {...},
                            "data_dependency_parsed": {...}
                        }
                    },
                    ...
                }
            }
        """
        corpus_encoding = self.task_config["CORPUS_ENCODING"]

        # Standardize input
        if type(raw_articles) == str:
            raw_articles = (raw_articles, )

        if len(raw_articles) == 0:
            raise AssertionError("No input detected.")

        elif len(raw_articles) == 1:
            return deserialize_line(raw_articles[0], corpus_encoding)

        else:
            # Multiple versions of an article detected (for example all sentences of an article PoS tagged, NE tagged,
            # dependency parsed)- merge them!

            # Get articles as json
            article_jsons = [deserialize_line(raw_article, corpus_encoding) for raw_article in raw_articles]

            # Check integrity of inputs
            article_ids = [article_json["meta"]["id"] for article_json in article_jsons]
            article_types = [article_json["meta"]["type"] for article_json in article_jsons]

            if len(set(article_ids)) != 1 or len(set(article_types)) != 1:
                raise AssertionError(
                    "Combining input objects requires them to have the same id and same type: {} and {} found.".format(
                        ", ".join(article_ids), ", ".join(article_types)
                    )
                )

            # Combine inputs
            sample_article = article_jsons[0]
            # Combine meta dates
            new_articles = dict(meta=list(sample_article["meta"]))
            new_articles["meta"]["state"] = " | ".join(
                [article_json["meta"]["state"] for article_json in article_jsons]
            )

            # Combine dates
            new_articles["data"] = {
                sentence_id: {
                    "data_{}".format(article_json["meta"]["type"]): article_json["data"]["sentence_id"]
                    for article_json in article_jsons
                }
                for sentence_id in sample_article["data"].keys()
            }

            return new_articles


def serialize_tagged_sentence(sentence_id, tagged_sentence, state="raw", pretty=False, dump=True):
    """
    Serialize a sentence tagged with Named entity tags s.t. it can be passed between Luigi tasks.
    """
    options = {"ensure_ascii": False}

    if pretty:
        options.update({"indent": 4, "sort_keys": True})

    serialized_tagged_sentence = {
        "meta": {
            "id": sentence_id,
            "type": "sentence",
            "state": state
        },
        "data": tagged_sentence
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
        "meta": {
            "id": sentence_id,
            "state": state,
            "type": "sentence"
        },
        "data": simplified_tree
    }

    if dump:
        return json.dumps(serialized_dependency_parse_tree, **options)

    return serialized_dependency_parse_tree


def serialize_relation(sentence_id, sentence, relations, state="raw", pretty=False, dump=True):
    """
    Serialize an extracted relation.
    """
    options = {"ensure_ascii": False}

    if pretty:
        options["indent"] = 4

    serialized_relation = {
        "meta": {
            "id": sentence_id,
            "state": state,
            "type": "sentence"
        },
        "data": {
            "sentence": sentence,
            "relations": {
                "{}/{}".format(sentence_id, str(relation_id).zfill(5)): {
                    "meta": {
                        "id": "{}/{}".format(sentence_id, str(relation_id).zfill(5)),
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


def deserialize_line(line, encoding="utf-8"):
    """
    Transform a line in a file that was created as a result from a Luigi task into its metadata and main data.
    """
    return json.loads(line, encoding=encoding)


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
