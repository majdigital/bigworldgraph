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
from bwg.misc.helpers import is_collection, time_function
from bwg.nlp.utilities import serialize_article, get_nes_from_sentence, serialize_relation
from bwg.nlp.mixins import ArticleProcessingMixin
from bwg.nlp.standard_tasks import NERTask


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
        corpus_inpath = self.workflow_resources["corpus_inpath"]
        corpus_encoding = self.workflow_resources["corpus_encoding"]

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
                if re.match(self.workflow_resources["article_tag_pattern"], line):
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

    @property
    def workflow_resources(self):
        corpus_inpath = self.task_config["CORPUS_INPATH"]
        corpus_encoding = self.task_config["CORPUS_ENCODING"]
        article_tag_pattern = self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"]

        workflow_resources = {
            "corpus_inpath": corpus_inpath,
            "corpus_encoding": corpus_encoding,
            "article_tag_pattern": article_tag_pattern
        }

        return workflow_resources

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


class AttributeCompletionTask(luigi.Task, ArticleProcessingMixin):
    """
    Add attributes from Wikidata to Named Entities.
    """
    default_ne_tag = "O"  # TODO (Refactor): Make this a config parameters?

    def requires(self):
        return NERTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["AC_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True, give_report=True)
    def run(self):
        # TODO (Refactor)
        with self.input().open("r") as nes_input_file, self.output().open("w") as output_file:
            for nes_line in nes_input_file:
                self.process_articles(
                    nes_line, new_state="added_attributes",
                    serializing_function=serialize_relation, output_file=output_file
                )

    def task_workflow(self, article, **workflow_resources):
        # TODO (Feature): Implement
        article_meta, article_data = article["meta"], article["data"]

        for sentence_id, sentence_json in article_data.items():
            nes = get_nes_from_sentence(sentence_json["data"], self.default_ne_tag)

            for named_entity in nes:
                self.request_entity(entity=named_entity)

            serializing_arguments = {
            }

            yield serializing_arguments

    @property
    def workflow_resources(self):
        """
        Property that provides resources necessary to complete the task's workflow.
        """
        wikidata_site = pywikibot.Site("en", "wikipedia")
        language_abbreviation = self.task_config["language_abbreviation"]
        fallback_language_abbreviation = self.task_config["fallback_language_abbreviation"]

        workflow_resources = {
            "wikidata_site": wikidata_site,
            "language_abbrevation": language_abbreviation,
            "fallback_language_abbreviation": fallback_language_abbreviation
        }

        return workflow_resources

    def get_entity_senses(self, name, language=LANGUAGE_ABBREVIATION):
        site = pywikibot.Site("wikidata", "wikidata")  # TODO (Refactor): Make this class variable
        request_parameters = {
            'action': 'wbsearchentities',
            'format': 'json',
            'language': language,
            'type': 'item',
            'search': name
        }
        request = api.Request(site=site, **request_parameters)
        response = request.submit()

        if len(response["search"]) == 0:
            return []

        return [
            {
                "uri": search_result["concepturi"],
                "id": search_result["id"],
                "description": search_result["description"],
                "label": search_result["label"]
            }
            for search_result in response["search"]
        ]

    def get_entity(self, wikidata_id, ne_tag, language=LANGUAGE_ABBREVIATION):
        site = pywikibot.Site("wikidata", "wikidata")  # TODO (Refactor): Make this class variable
        request = api.Request(
            site=site,
            action='wbgetentities',
            format='json',
            ids=wikidata_id
        )
        response = request.submit()

        if len(response["entities"]) == 0:
            return {}

        return [
            {
                "aliases": [alias_dict["value"] for alias_dict in entity["aliases"][language]],
                "description": entity["descriptions"][language]["value"],
                "id": entity["id"],
                "label": entity["labels"][language]["value"],
                "modified": entity["modified"],
                "claims": self._resolve_claims(entity["claims"], language)
            }
            for id_, entity in response["entities"].items()
        ][0]

    def _resolve_claims(self, claims, ne_tag, language=LANGUAGE_ABBREVIATION):
        global RELEVANT_PROPERTIES_PER
        # TODO (Refactor): Make relevant properties available in config
        return {
            self._get_property_name(property_id, language):
                self._get_entity_name(claim[0]["mainsnak"]["datavalue"]["value"]["id"])
            for property_id, claim in claims.items()
            if property_id in RELEVANT_PROPERTIES_PER
        }

    def _get_property_name(self, property_id, language=LANGUAGE_ABBREVIATION):
        site = pywikibot.Site("wikidata", "wikidata")  # TODO (Refactor): Make this class variable
        request = api.Request(
            site=site,
            action='wbgetentities',
            format='json',
            ids=property_id
        )
        response = request.submit()

        return [
            entity["labels"][language]["value"]
            for id_, entity in response["entities"].items()
        ][0]

    def _get_entity_name(self, entity_id, language=LANGUAGE_ABBREVIATION):
        site = pywikibot.Site("wikidata", "wikidata")  # TODO (Refactor): Make this class variable
        request = api.Request(
            site=site,
            action='wbgetentities',
            format='json',
            ids=entity_id
        )
        response = request.submit()

        return [
            entity["labels"][language]["value"]
            for id_, entity in response["entities"].items()
        ][0]
