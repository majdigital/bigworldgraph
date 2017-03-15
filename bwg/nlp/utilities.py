# -*- coding: utf-8 -*-
"""
Utilities for the NLP pipeline.
"""

# STD
import json
import abc
import copy

# EXT
import luigi

# PROJECT
from bwg.misc.helpers import filter_dict, flatten_dictlist, time_function, seconds_to_hms
from pipeline_config import DEPENDENCY_TREE_KEEP_FIELDS


class ArticleProcessingMixin:
    """
    Enable Luigi tasks to process single lines as well as articles or other input types.
    """
    task_config = luigi.DictParameter()
    runtimes = []

    @abc.abstractmethod
    def task_workflow(self, article, bulk=False, **workflow_kwargs):
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

            # Afterwards, put all the arguments for the corresponding serializing function into a dict and yield it.
            serializing_kwargs = {}

            yield serializing_kwargs

    @property
    @abc.abstractmethod
    def workflow_resources(self):
        """
        Property that provides resources necessary to complete the task's workflow.
        """
        workflow_resources = {}

        return workflow_resources

    @time_function(out=None, return_time=True)
    def process_articles(self, raw_articles, new_state, serializing_function, output_file, pretty=False):
        """
        Process line from the input and apply this task's workflow. Serialize the result afterwards and finally write
        it to the output file.
        """
        debug = self.task_config.get("PIPELINE_DEBUG", False)
        article = self._combine_articles(raw_articles)
        sentences = []

        # Main processing
        if debug:
            print("{} processing article '{}'...".format(self.__class__.__name__, article["meta"]["title"]))

        for serializing_kwargs in self.task_workflow(article, **self.workflow_resources):
            if debug:
                print("{} finished sentence #{}.".format(self.__class__.__name__, serializing_kwargs["sentence_id"]))

            serialized_sentence = serializing_function(**serializing_kwargs, state=new_state, dump=False)

            if self.is_relevant_sentence(serialized_sentence):
                sentences.append(serialized_sentence)

        sentences = flatten_dictlist(sentences)
        meta = article["meta"]
        article_id, article_url, article_title = meta["id"], meta["url"], meta["title"]
        serialized_article = serialize_article(
            article_id, article_url, article_title, sentences, state=new_state, from_scratch=False, dump=False,
            pretty=pretty
        )

        # Output
        if self.is_relevant_article(serialized_article):
            output_file.write("{}\n".format(just_dump(serialized_article)))

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
            sample_article = copy.deepcopy(article_jsons[0])
            # Combine meta dates
            new_article = dict(meta=sample_article["meta"])
            new_article["meta"]["state"] = " | ".join(
                [article_json["meta"]["state"] for article_json in article_jsons]
            )

            # Combine dates
            new_article["data"] = {}
            for sentence_id, sentence_json in sample_article["data"].items():
                sentence_meta = sentence_json["meta"]
                sentence_meta["state"] = " | ".join(
                    [article_json["meta"]["state"] for article_json in article_jsons]
                )

                new_article["data"].update(
                    {
                        sentence_id: {
                            "meta": sentence_meta,
                            "data": {
                                "data_{}".format(article_json["meta"]["state"]): article_json["data"][sentence_id]
                                for article_json in article_jsons
                            }
                        }
                    }
                )

            return new_article

    def is_relevant_article(self, article):
        """
        Filter articles in the output by a relevance criterion that subclasses can define in this function.

        All articles are relevant if the flag is not set; only relevant ones are relevant if the flag is set (duh).
        """
        relevance_flag_set = self.task_config.get("ONLY_INCLUDE_RELEVANT_ARTICLES", False)
        return not relevance_flag_set or self._is_relevant_article(article)

    def is_relevant_sentence(self, sentence):
        """
        Filter sentences of an article in the output by a relevance criterion that subclasses can define in this
        function.

        All sentences are relevant if the flag is not set; only relevant ones are relevant if the flag is set (duh).
        """
        relevance_flag_set = self.task_config.get("ONLY_INCLUDE_RELEVANT_SENTENCES", False)
        return not relevance_flag_set or self._is_relevant_sentence(sentence)

    def _is_relevant_article(self, article):
        """
        Filter articles in the output by a relevance criterion that subclasses can define in this function.
        """
        return True

    def _is_relevant_sentence(self, sentence):
        """
        Filter sentences of an article in the output by a relevance criterion that subclasses can define in this
        function.
        """
        return True

    @staticmethod
    def calculate_average_processing_time(runtimes):
        return sum(runtimes) / len(runtimes)

    @staticmethod
    def calculate_average_processing_speed(runtimes):
        return len(runtimes) / sum(runtimes)

    def give_runtime_report(self, runtimes):
        average_processing_speed = self.calculate_average_processing_speed(runtimes)
        average_processing_time = self.calculate_average_processing_time(runtimes)

        print("Processing articles in {}:\n\tOn average {:.2f} articles per second.\n\tOn average {:.2f} hour(s), {:.2f}"
              " minute(s) and {:.2f} second(s) per article.".format(
            self.__class__.__name__, average_processing_time, *seconds_to_hms(average_processing_speed))
        )


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


def serialize_relation(sentence_id, sentence, relations, state="raw", pretty=False, dump=True):
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
