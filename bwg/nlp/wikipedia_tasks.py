# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

# STD
import codecs
import re

# EXT
import luigi
import luigi.format
import pywikibot
from pywikibot.data import api

# PROJECT
from bwg.misc.helpers import is_collection, time_function, construct_dict_from_source
from bwg.nlp.utilities import (
    serialize_article,
    get_nes_from_sentence,
    serialize_wikidata_entity,
    retry_with_fallback,
    retry_when_exception
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


class PropertiesCompletionTask(luigi.Task, ArticleProcessingMixin):
    """
    Add attributes from Wikidata to Named Entities.
    """
    default_ne_tag = "O"  # TODO (Refactor): Make this a config parameters?
    wikidata_site = pywikibot.Site("wikidata", "wikidata")
    fallback_language_abbreviation = None

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
        # TODO (Improve): Speed this up
        article_meta, article_data = article["meta"], article["data"]
        language_abbreviation = self.task_config["LANGUAGE_ABBREVIATION"]
        request_cache = {}
        requested_ids = set()
        wikidata_entities = []

        for sentence_id, sentence_json in article_data.items():
            nes = get_nes_from_sentence(sentence_json["data"], self.default_ne_tag, include_tag=True)

            entity_number = 0
            for named_entity, ne_tag in nes:
                entity_senses = self.get_entity_senses(named_entity, language=language_abbreviation)

                if len(entity_senses) == 0:
                    continue

                elif len(entity_senses) > 1:
                    ambiguous_entities = []

                    # Deal with ambiguous entities
                    for entity_sense in entity_senses:
                        entity_id = entity_sense["id"]

                        if entity_id in requested_ids:
                            wikidata_entity = request_cache[entity_id]
                        else:
                            wikidata_entity = self.get_entity(entity_id, ne_tag, language=language_abbreviation)
                            request_cache[entity_id] = wikidata_entity
                            requested_ids.add(entity_id)

                        ambiguous_entities.append(wikidata_entity)

                    wikidata_entities.append(ambiguous_entities)

                else:
                    entity_sense = entity_senses[0]
                    wikidata_entity = self.get_entity(
                        entity_sense["id"], ne_tag, language=language_abbreviation
                    )

                    wikidata_entities.append([wikidata_entity])

                entity_number += 1

            serializing_arguments = {
                "sentence_id": sentence_id,
                "wikidata_entities": wikidata_entities,
                "infix": "WDE"
            }

            yield serializing_arguments

    @property
    def workflow_resources(self):
        """
        Property that provides resources necessary to complete the task's workflow.
        """
        self.fallback_language_abbreviation = self.task_config["FALLBACK_LANGUAGE_ABBREVIATION"]

        return {}

    @retry_with_fallback(triggering_error=KeyError, language="en")
    @retry_when_exception(triggering_error=api.APIError)
    def get_entity_senses(self, name, language):
        """
        Gets matches for an entity name in wikidata.
        """
        request_parameters = {
            'action': 'wbsearchentities',
            'format': 'json',
            'language': language,
            'type': 'item',
            'search': name
        }
        request = api.Request(site=self.wikidata_site, use_get=True, **request_parameters)
        response = request.submit()

        if len(response["search"]) == 0:
            return []

        return [
            construct_dict_from_source(
                {
                    "uri": lambda source: source["concepturi"],
                    "id": lambda source: source["id"],
                    "description": lambda source: source["description"],
                    "label": lambda source: source["label"]
                },
                search_result
            )
            for search_result in response["search"]
        ]

    @retry_with_fallback(triggering_error=KeyError, language="en")
    @retry_when_exception(triggering_error=api.APIError)
    def get_entity(self, wikidata_id, ne_tag, language):
        """
        Get an entity and further information from wikidate based its ID and Named Entity tag.
        """
        request = api.Request(
            site=self.wikidata_site,
            action='wbgetentities',
            format='json',
            ids=wikidata_id,
            use_get=True,
            throttle=False
        )
        response = request.submit()

        if len(response["entities"]) == 0:
            return {}

        return [
            construct_dict_from_source(
                {
                    "aliases": lambda source: [alias_dict["value"] for alias_dict in source["aliases"][language]],
                    "description": lambda source: source["descriptions"][language]["value"],
                    "id": lambda source: source["id"],
                    "label": lambda source: source["labels"][language]["value"],
                    "modified": lambda source: source["modified"],
                    "claims": lambda source: self._resolve_claims(source["claims"], ne_tag, language=language)
                },
                entity
            )
            for id_, entity in response["entities"].items()
        ][0]

    @retry_with_fallback(triggering_error=KeyError, language="en")
    @retry_when_exception(triggering_error=api.APIError)
    def _resolve_claims(self, claims, ne_tag, language):
        """
        Resolve the claims (~ claimed facts) about a wikidata entity. 
        """
        relevant_properties = self.task_config["RELEVANT_WIKIDATA_PROPERTIES"][ne_tag]

        return {
            self._get_property_name(property_id, language):
                self._get_entity_name(claim[0]["mainsnak"]["datavalue"]["value"]["id"], language=language)
            for property_id, claim in claims.items()
            if property_id in relevant_properties
        }

    @retry_with_fallback(triggering_error=KeyError, language="en")
    @retry_when_exception(triggering_error=api.APIError)
    def _get_property_name(self, property_id, language):
        """
        Get the name of a wikidata property.
        """
        request = api.Request(
            site=self.wikidata_site,
            action='wbgetentities',
            format='json',
            ids=property_id,
            use_get=True,
            throttle=False
        )
        response = request.submit()

        return [
            entity["labels"][language]["value"]
            for id_, entity in response["entities"].items()
        ][0]

    @retry_with_fallback(triggering_error=KeyError, language="en")
    @retry_when_exception(triggering_error=api.APIError)
    def _get_entity_name(self, entity_id, language):
        """
        Get the name of a wikidata entity.
        """
        request = api.Request(
            site=self.wikidata_site,
            action='wbgetentities',
            format='json',
            ids=entity_id,
            use_get=True,
            throttle=False
        )
        response = request.submit()

        return [
            entity["labels"][language]["value"]
            for id_, entity in response["entities"].items()
        ][0]
