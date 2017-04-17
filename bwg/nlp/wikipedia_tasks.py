# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

# STD
import codecs
import threading
import re
import requests
import queue
import collections

# EXT
import luigi
import luigi.format
import pywikibot

# PROJECT
from bwg.misc.helpers import is_collection, time_function
from bwg.misc.wikidata import WikidataAPIMixin, WikidataScraperMixin
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
    default_ne_tag = "O"  # TODO (Refactor): Make this a config parameters?
    wikidata_site = pywikibot.Site("wikidata", "wikidata")

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
                # TODO (Debug): Remove prettyprint
                self.process_articles(
                    nes_line, new_state="added_properties",
                    serializing_function=serialize_wikidata_entity, output_file=output_file, pretty=True
                )

    def task_workflow(self, article, **workflow_resources):
        global EXIT_FLAG
        global NE_DEQUE
        global CACHE
        global SERIALIZING_ARGUMENTS_DICT

        EXIT_FLAG = 0
        # TODO (Improve): Speed this up
        # TODO (Bug): Not all data in final output [DU 14.04.17]
        # Reqests fail because they are stupid
        article_meta, article_data = article["meta"], article["data"]
        language_abbreviation = self.task_config["LANGUAGE_ABBREVIATION"]
        relevant_properties_all = self.task_config["RELEVANT_WIKIDATA_PROPERTIES"]

        # Init resources
        #cache = RequestCache()
        #manager = threading.Manager()
        #entity_number = manager.Value("i", 0)
        #entity_number = 0
        #ne_queue = queue.Queue()
        #ne_deque = collections.deque()
        ne_deque_lock = threading.Lock()
        entity_number_lock = threading.Lock()
        #serializing_arguments_dict = manager.dict()
        #serializing_arguments_dict = {}
        #cache = manager.dict()
        #cache = RequestCache()
        number_of_processes = 32

        for sentence_id, sentence_json in article_data.items():
            nes = get_nes_from_sentence(sentence_json["data"], self.default_ne_tag, include_tag=True)

            for ne in nes:
                NE_DEQUE.append((sentence_id, ne))
                #ne_queue.put((sentence_id, ne))

        jobs = []
        for i in range(number_of_processes):
            job = threading.Thread(
                target=self._process_task_workflow,
                args=(i+1, language_abbreviation, relevant_properties_all, ne_deque_lock, entity_number_lock)
            )
            jobs.append(job)

        for job in jobs:
            job.start()

        #while not ne_queue.empty():
        #    pass
        while NE_DEQUE:
            pass

        EXIT_FLAG = 1

        for job in jobs:
            job.join()

        for key, serializing_arguments in SERIALIZING_ARGUMENTS_DICT.items():
            if serializing_arguments is not None:
                yield serializing_arguments

    def _process_task_workflow(self, thread_id, language_abbreviation, relevant_properties_all, ne_deque_lock,
                               entity_number_lock):
        global EXIT_FLAG
        global ENTITY_NUMBER
        global NE_DEQUE
        global CACHE
        global SERIALIZING_ARGUMENTS_DICT

        while EXIT_FLAG == 0:
            try:
                with ne_deque_lock:
                    sentence_id, ne = NE_DEQUE.pop()
                #print("Thread #{}: NE in sentence #{}: {} left.".format(thread_id, sentence_id, len(NE_DEQUE)))
            except:
                continue
            #sentence_id, ne = ne_queue.get(True, timeout=3)
            named_entity, ne_tag = ne
            wikidata_entities = []

            print("Thread #{} searching Wikidata for matches...".format(thread_id))
            entity_senses = self.get_matches(named_entity, language=language_abbreviation)
            relevant_properties = relevant_properties_all.get(ne_tag, [])

            if len(entity_senses) == 0:
                return None

            elif len(entity_senses) > 1:
                ambiguous_entities = []

                # Deal with ambiguous entities
                for entity_sense in entity_senses:
                    print("Thread #{} requesting more information about '{}' (ambiguous)".format(thread_id, entity_sense["id"]))
                    wikidata_entity, CACHE = self._request_or_use_cache(
                        entity_sense["id"], language_abbreviation, relevant_properties, CACHE
                    )

                    ambiguous_entities.append(wikidata_entity)

                wikidata_entities.append(ambiguous_entities)

            else:
                entity_sense = entity_senses[0]
                print("Thread #{} requesting more information about '{}'".format(thread_id, entity_sense["id"]))
                wikidata_entity, CACHE = self._request_or_use_cache(
                    entity_sense["id"], language_abbreviation, relevant_properties, CACHE
                )

                wikidata_entities.append([wikidata_entity])

            print("Thread #{} preparing serializing arguments...".format(thread_id))
            serializing_arguments = {
                "sentence_id": sentence_id,
                "wikidata_entities": wikidata_entities,
                "infix": "WDE"
            }

            SERIALIZING_ARGUMENTS_DICT[ENTITY_NUMBER] = serializing_arguments

            print("Thread #{} trying to increment entity number (current {})".format(thread_id, ENTITY_NUMBER))
            with entity_number_lock:
                ENTITY_NUMBER += 1

            #ne_queue.task_done()

    def _request_or_use_cache(self, entity_id, language_abbreviation, relevant_properties, cache, caching=True):
        if caching:
            with cache:
                if entity_id in cache:
                    return cache[entity_id], cache

        wikidata_entity = self.get_entity(
            entity_id, language=language_abbreviation,
            relevant_properties=relevant_properties
        )

        if caching:
            with cache:
                cache[entity_id] = wikidata_entity

        return wikidata_entity, cache

EXIT_FLAG = 0
ENTITY_NUMBER = 1
CACHE = RequestCache()
NE_DEQUE = collections.deque()
SERIALIZING_ARGUMENTS_DICT = {}
