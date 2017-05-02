# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

# STD
import codecs
import re
import threading

# EXT
import luigi
import luigi.format

import bwg.nlp.standard_tasks
# PROJECT
from bwg.helpers import is_collection, time_function
from bwg.nlp.mixins import ArticleProcessingMixin
from bwg.nlp.utilities import (
    serialize_article,
    get_nes_from_sentence,
    serialize_wikidata_entity
)
from bwg.wikidata import WikidataAPIMixin  # , WikidataScraperMixin


class WikipediaReadingTask(luigi.Task):
    """
    A luigi task that reads an extracted Wikipedia corpus (see README).
    """
    task_config = luigi.DictParameter()

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["WIKIPEDIA_READING_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        corpus_inpath = self.task_config["CORPUS_INPATH"]
        corpus_encoding = self.task_config["CORPUS_ENCODING"]

        # Init "parsing" variables
        current_title = ""
        current_id = ""
        current_url = ""
        current_sentences = []
        skip_line = False
        comment = False

        with codecs.open(corpus_inpath, "r", corpus_encoding) as input_file, self.output().open("w") as output_file:
            for line in input_file.readlines():
                line = line.strip()

                # Skip lines that should be ignored (article headers withing the article, xml comments, etc.)
                if skip_line:
                    if not comment or "-->" in line:
                        comment = False
                        skip_line = False
                    continue

                # Skip line if line is the title (title is already given in the <doc> tag)
                if line == current_title:
                    continue

                # Identify xml/html comments
                if "<!--" in line:
                    if "-->" not in line:
                        skip_line = True
                        comment = True
                    continue

                # Identify beginning of new article
                if re.match(self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"], line):
                    current_id, current_url, current_title = self._extract_article_info(line)

                # Identify end of article
                elif line.strip() == "</doc>":
                    self._output_article(
                        current_id, current_url, current_title, current_sentences, output_file, state="parsed"
                    )
                    current_title, current_id, current_url, current_sentences = self._reset_vars()

                # Just add a new line to ongoing article
                else:
                    if not line.strip():
                        continue

                    # Apply additional formatting to line if an appropriate function is given
                    line = re.sub("</?.+?>", "", line)  # Remove other xml markup
                    formatted = self._additional_formatting(line.strip())

                    # Add line
                    if is_collection(formatted):
                        for line_ in formatted:
                            current_sentences.append(line_)

                    else:
                        current_sentences.append(line)

    def _output_article(self, id_, url, title, sentences, output_file, **additional):
        """
        Write read article to file.
        
        :param id_: Article ID.
        :type id_: int
        :param url: URL of current article.
        :type url: str
        :param title: Title of current article.
        :type title: str
        :param sentences: Article sentences. 
        :type sentences: list
        :param output_file: Output file the article is written to.
        :type output_file: _io.TextWrapper
        :param additional: Additional parameters for serialization.
        :type additional: dict
        """
        article_json = serialize_article(
            id_, url, title, sentences, **additional
        )
        output_file.write("{}\n".format(article_json))

    def _additional_formatting(self, line):
        """
        Provide additional formatting for a line possible subclasses by overwriting this function.
        
        :param line: Line to be formatted.
        :type line: str
        :return: Formatted line.
        :rtype: str
        """
        return line

    @staticmethod
    def _reset_vars():
        """
        Reset temporary variables used while reading the input corpus.
        
        :return: Reset variables.
        :rtype: tuple
        """
        return "", "", "", []

    def _extract_article_info(self, line):
        """
        Extract important information from the opening article XML tag.
        
        :param line: Line with article information.
        :type line: str
        :return: Information about article.
        :rtype: tuple
        """
        article_tag_pattern = self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"]
        groups = re.match(article_tag_pattern, line).groups()
        return groups


class RequestCache:
    """
    Special class used as a Cache, so that requests being made don't have to be repeated if they occurred in the past.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.cache = {}
        self.requested = set()
        self.number_of_requests = 0
        self.number_of_avoided_requests = 0

    def __contains__(self, item):
        return item in self.requested

    def __delitem__(self, key):
        del self.cache[key]
        self.requested.remove(key)

    def __getitem__(self, key):
        return self.cache[key]

    def __setitem__(self, key, value):
        self.cache[key] = value
        self.requested.add(key)

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()

    def __len__(self):
        return len(self.requested)

    def request(self, key, request_func, *request_args, **request_kwargs):
        """
        Make a request, but make a lookup to the cache first to see if you may be able to avoid it.

        :param key: Key that should be used to cache the request.
        :type key: str, int
        :param request_func: Function to do the request.
        :type request_func: func
        :param request_args: Arguments for request.
        :type request_args: tuple
        :param request_kwargs: Key word arguments for request.
        :type request_kwargs: dict
        """
        if key in self:
            self.number_of_avoided_requests += 1
            return self[key]

        request_result = request_func(*request_args, **request_kwargs)
        self.number_of_requests += 1

        self[key] = request_result

        return request_result


class PropertiesCompletionTask(luigi.Task, ArticleProcessingMixin, WikidataAPIMixin):
    """
    Add attributes from Wikidata to Named Entities.
    """
    def requires(self):
        return bwg.nlp.standard_tasks.NERTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["PC_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input().open("r") as nes_input_file, self.output().open("w") as output_file:
            for nes_line in nes_input_file:
                self.process_articles(
                    nes_line, new_state="added_properties",
                    serializing_function=serialize_wikidata_entity, output_file=output_file
                )

    def task_workflow(self, article, **workflow_resources):
        article_meta, article_data = article["meta"], article["data"]
        language_abbreviation = self.task_config["LANGUAGE_ABBREVIATION"]
        relevant_properties_all = self.task_config["RELEVANT_WIKIDATA_PROPERTIES"]
        properties_implying_relations = set(self.task_config["WIKIDATA_PROPERTIES_IMPLYING_RELATIONS"])
        default_ne_tag = self.task_config["DEFAULT_NE_TAG"]
        request_cache = RequestCache()
        match_cache = RequestCache()
        wikidata_entities = []

        for sentence_id, sentence_json in article_data.items():
            nes = get_nes_from_sentence(sentence_json["data"], default_ne_tag, include_tag=True)

            entity_number = 0
            for named_entity, ne_tag in nes:
                entity_senses = match_cache.request(
                    named_entity, self.get_matches, named_entity, language=language_abbreviation
                )
                relevant_properties = relevant_properties_all.get(ne_tag, [])

                # No matches - skip
                if len(entity_senses) == 0:
                    continue

                # Deal with ambiguous entities
                elif len(entity_senses) > 1:
                    ambiguous_entities = []

                    for entity_sense in entity_senses:
                        wikidata_entity = request_cache.request(
                            entity_sense["id"], self.get_entity,
                            entity_sense["id"], language=language_abbreviation,
                            relevant_properties=relevant_properties,
                            properties_implying_relations=properties_implying_relations
                        )
                        wikidata_entity["type"] = ne_tag

                        ambiguous_entities.append(wikidata_entity)

                    wikidata_entities.append(ambiguous_entities)

                # One match - lucky!
                else:
                    entity_sense = entity_senses[0]
                    wikidata_entity = request_cache.request(
                        entity_sense["id"], self.get_entity,
                        entity_sense["id"], language=language_abbreviation,
                        relevant_properties=relevant_properties,
                        properties_implying_relations=properties_implying_relations
                    )
                    wikidata_entity["type"] = ne_tag

                    wikidata_entities.append([wikidata_entity])

                entity_number += 1

            serializing_arguments = {
                "sentence_id": sentence_id,
                "wikidata_entities": wikidata_entities,
                "infix": "WDE"
            }

            yield serializing_arguments
