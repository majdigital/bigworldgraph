# -*- coding: utf-8 -*-
"""
Define a pipeline task that enriches named entities from a sentence with information from Wikidata.
"""

# EXT
import luigi

import bwg
from bwg.decorators import time_function
from bwg.mixins import ArticleProcessingMixin
from bwg.serializing import serialize_wikidata_entity, get_nes_from_sentence
from bwg.wikidata_mixins import WikidataAPIMixin


class PropertiesCompletionTask(luigi.Task, ArticleProcessingMixin, WikidataAPIMixin):
    """
    Add attributes from Wikidata to Named Entities.
    """
    def requires(self):
        return bwg.standard_tasks.NERTask(task_config=self.task_config)

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
        properties_implying_relations = self.task_config["WIKIDATA_PROPERTIES_IMPLYING_RELATIONS"]
        default_ne_tag = self.task_config["DEFAULT_NE_TAG"]
        wikidata_entities = []

        for sentence_id, sentence_json in article_data.items():
            nes = get_nes_from_sentence(sentence_json["data"], default_ne_tag, include_tag=True)

            entity_number = 0
            for named_entity, ne_tag in nes:
                entity_senses = self.match_cache.request(
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
                        wikidata_entity = self.request_cache.request(
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
                    wikidata_entity = self.request_cache.request(
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