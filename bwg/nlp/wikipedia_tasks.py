# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

# STD
import codecs
import threading
import re

# EXT
import luigi
import luigi.format

# PROJECT
from bwg.misc.helpers import is_collection, time_function
from bwg.misc.wikidata import WikidataAPIMixin  # , WikidataScraperMixin
from bwg.nlp.utilities import (
    serialize_article,
    get_nes_from_sentence,
    serialize_wikidata_entity
)
from bwg.nlp.mixins import ArticleProcessingMixin
import bwg.nlp.standard_tasks


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
        article_json = serialize_article(
            id_, url, title, sentences, state=additional["state"]
        )
        output_file.write("{}\n".format(article_json))

    def _additional_formatting(self, line):
        """
        Provide additional formatting for a line possible subclasses by overwriting this function.
        """
        return line

    @staticmethod
    def _reset_vars():
        return "", "", "", []

    def _extract_article_info(self, line):
        article_tag_pattern = self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"]
        groups = re.match(article_tag_pattern, line).groups()
        return groups


class RequestCache:
        def __init__(self):
            self.lock = threading.Lock()
            self.cache = {}
            self.requested = set()

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

    @time_function(is_classmethod=True, give_report=True)
    def run(self):
        with self.input().open("r") as nes_input_file, self.output().open("w") as output_file:
            for nes_line in nes_input_file:
                self.process_articles(
                    nes_line, new_state="added_properties",
                    serializing_function=serialize_wikidata_entity, output_file=output_file
                )

    def task_workflow(self, article, **workflow_resources):
        # TODO (Improve): Speed this up [Comment DU 18.04.17]
        # Not so easy: See branch parallelize_scraper for the most recent attempt:
        #   - Accessing Wikidata via Scraper is much slower than via API
        #   - Language support is very limited for the scraper
        #   - Using multithreading only has minimal gains / is even slower so far
        #   (probably due to GIL and sharing resources between threads)
        article_meta, article_data = article["meta"], article["data"]
        language_abbreviation = self.task_config["LANGUAGE_ABBREVIATION"]
        relevant_properties_all = self.task_config["RELEVANT_WIKIDATA_PROPERTIES"]
        default_ne_tag = self.task_config["DEFAULT_NE_TAG"]
        request_cache = RequestCache()
        wikidata_entities = []

        for sentence_id, sentence_json in article_data.items():
            nes = get_nes_from_sentence(sentence_json["data"], default_ne_tag, include_tag=True)

            entity_number = 0
            for named_entity, ne_tag in nes:
                entity_senses = self.get_matches(named_entity, language=language_abbreviation)
                relevant_properties = relevant_properties_all.get(ne_tag, [])

                # No matches - skip
                if len(entity_senses) == 0:
                    continue

                # Deal with ambiguous entities
                elif len(entity_senses) > 1:
                    ambiguous_entities = []

                    for entity_sense in entity_senses:
                        entity_id = entity_sense["id"]

                        if entity_id in request_cache:
                            wikidata_entity = request_cache[entity_id]
                        else:
                            wikidata_entity, request_cache = self._request_or_use_cache(
                                entity_sense["id"], language_abbreviation, relevant_properties, request_cache
                            )
                            request_cache[entity_id] = wikidata_entity

                        ambiguous_entities.append(wikidata_entity)

                    wikidata_entities.append(ambiguous_entities)

                # One match - lucky!
                else:
                    entity_sense = entity_senses[0]
                    wikidata_entity, request_cache = self._request_or_use_cache(
                        entity_sense["id"], language_abbreviation, relevant_properties, request_cache
                    )

                    wikidata_entities.append([wikidata_entity])

                entity_number += 1

            serializing_arguments = {
                "sentence_id": sentence_id,
                "wikidata_entities": wikidata_entities,
                "infix": "WDE"
            }

            yield serializing_arguments

    def _request_or_use_cache(self, entity_id, language_abbreviation, relevant_properties, cache, caching=True):
        if caching:
            if entity_id in cache:
                return cache[entity_id], cache

        wikidata_entity = self.get_entity(
            entity_id, language=language_abbreviation,
            relevant_properties=relevant_properties
        )

        if caching:
            cache[entity_id] = wikidata_entity

        return wikidata_entity, cache
