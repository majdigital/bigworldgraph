# -*- coding: utf-8 -*-
"""
Defining additional tasks for the NLP pipeline.
"""

# STD
import time
import datetime

# EXT
import luigi
import luigi.format
from bwg.nlp.mixins import ArticleProcessingMixin

# PROJECT
from bwg.nlp.standard_tasks import NaiveOpenRelationExtractionTask, ParticipationExtractionTask
from bwg.misc.helpers import time_function
from bwg.nlp.utilities import serialize_relation, deserialize_line, just_dump
from bwg.nlp.wikipedia_tasks import PropertiesCompletionTask, WikipediaReadingTask
from bwg.db.neo4j import Neo4jTarget


class RelationMergingTask(luigi.Task, ArticleProcessingMixin):
    """
    Merge relations gained from OpenRelationExtractionTask and ParticipationExtractionTask.
    """
    def requires(self):
        return ParticipationExtractionTask(task_config=self.task_config),\
               NaiveOpenRelationExtractionTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["RELATION_MERGING_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input()[0].open("r") as pe_file, self.input()[1].open("r") as ore_file, \
                self.output().open("w") as output_file:
            for pe_line, ore_line in zip(pe_file, ore_file):
                self.process_articles(
                    (pe_line, ore_line), new_state="merged_relations", serializing_function=serialize_relation,
                    output_file=output_file
                )

    def task_workflow(self, article, **workflow_resources):
        article_data = article["data"]

        for sentence_id, sentence_json in article_data.items():
            sentence_dates = sentence_json["data"]
            sentence = sentence_dates["data_extracted_participations"]["data"]["sentence"]
            relations = self._get_relations_from_sentence_json(sentence_dates["data_extracted_participations"])
            relations.extend(self._get_relations_from_sentence_json(sentence_dates["data_extracted_relations"]))

            serializing_arguments = {
                "sentence_id": sentence_id,
                "sentence": sentence,
                "relations": relations,
                "infix": "ORE:PE"
            }

            yield serializing_arguments

    @staticmethod
    def _get_relations_from_sentence_json(sentence_json):
        return [
            (
                relation_json["data"]["subject_phrase"],
                relation_json["data"]["verb"],
                relation_json["data"]["object_phrase"]
            )
            for relation_id, relation_json in sentence_json["data"]["relations"].items()
        ]

    def _is_relevant_article(self, article):
        """
        Override ArticleProcessingMixin's relevance criterion.
        """
        return len(article["data"]) > 0

    def _is_relevant_sentence(self, sentence):
        """
        Override ArticleProcessingMixin's relevance criterion.
        """
        # Separate sentence from sentence ID
        sentence = list(sentence.values())[0]
        return len(sentence["data"]["relations"]) > 0


class PipelineRunInfoGenerationTask(luigi.Task):
    """
    Generates information about the current run of the pipeline.
    """
    task_config = luigi.DictParameter()

    def requires(self):
        return WikipediaReadingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["PIPELINE_RUN_INFO_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        encoding = self.task_config["CORPUS_ENCODING"]
        article_ids = []

        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                article = deserialize_line(line, encoding)
                article_ids.append(article["meta"]["id"])

            run_info = self._generate_run_information(article_ids)
            output_file.write("{}\n".format(just_dump(run_info)))

    def _generate_run_information(self, article_ids):
        """
        Generate information about this pipeline run.
        
        :param article_ids: List of all article IDs.
        :type article_ids: list
        :return: Information about this run.
        :rtype: dict
        """
        return {
            "run_id": self._generate_run_hash(article_ids),
            "article_ids": article_ids,
            "timestamp": self._generate_timestamp()
        }

    @staticmethod
    def _generate_run_hash(article_ids):
        """
        Generate a specific hash for this run based on the articles that the pipeline processed.
        
        :param article_ids: List of all article IDs.
        :type article_ids: list
        :return: Hash value for this run.
        :rtype: int
        """
        return hash(frozenset(article_ids))

    @staticmethod
    def _generate_timestamp():
        """
        Generate a timestamp containing date and time for this pipeline run.
        
        :return: Timestamp.
        :rtype: str
        """
        now = time.time()
        return datetime.datetime.fromtimestamp(now).strftime('%Y.%m.%d %H:%M:%S')


class RelationsDatabaseWritingTask(luigi.Task):
    """
    Writes relations extracted via (naive) Open Relation Extraction and Participation Extraction into a graph database.
    """
    task_config = luigi.DictParameter()
    pipeline_run_info = None

    def requires(self):
        return RelationMergingTask(task_config=self.task_config),\
               PropertiesCompletionTask(task_config=self.task_config),\
               PipelineRunInfoGenerationTask(task_config=self.task_config)

    def output(self):
        user = self.task_config["NEO4J_USER"]
        password = self.task_config["NEO4J_PASSWORD"]
        return Neo4jTarget(self.pipeline_run_info, user, password)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input()[0].open("r") as mr_file, self.input()[1].open("r") as pc_file,\
                self.input()[1].open("r") as pri_file:
            self._read_pipeline_run_info(pri_file)
            self._read_properties(pc_file)
            with self.output() as database:
                for mr_line in mr_file:
                    self.process_article(mr_line, database)

    @time_function(is_classmethod=True)
    def process_article(self, raw_article, database):
        debug = self.task_config.get("PIPELINE_DEBUG", False)
        encoding = self.task_config["CORPUS_ENCODING"]
        article = deserialize_line(raw_article, encoding)
        article_meta, article_data = article["meta"], article["data"]

        if debug:
            print("{} processing article '{}'...".format(self.__class__.__name__, article["meta"]["title"]))

        for sentence_id, sentence_json in article_data.items():
            if debug:
                print("{} finished sentence #{}.".format(self.__class__.__name__, sentence_id))

            for relation_id, relation_json in sentence_json["data"]["relations"].items():
                database.add_relation(relation_json, sentence_json["data"]["sentence"])

    def _read_properties(self, properties_file):
        encoding = self.task_config["CORPUS_ENCODING"]
        entity_properties = {}

        for line in properties_file:
            article = deserialize_line(line, encoding)
            article_meta, article_data = article["meta"], article["data"]

            for sentence_id, sentence_json in article_data.items():
                sentence_meta, sentence_data = sentence_json["meta"], sentence_json["data"]

                for entity_id, entity_json in sentence_data["entities"].items():
                    entity_meta, entity_data = entity_json["meta"], entity_json["data"]

                    if entity_meta["type"] == "Ambiguous Wikidata entity":
                        pass

                    else:
                        entity_info = dict(entity_data)
                        del entity_info["label"]
                        entity_info = self._rename_field("modified", "wikidata_last_modified", entity_info)
                        entity_info = self._rename_field("id", "wikidata_id, entity_info", entity_info)
                        del entity_info["aliases"]

                    entity_properties[entity_data["label"]] = entity_info

                    if "aliases" in entity_data:
                        for alias in entity_data["aliases"]:
                            entity_properties[alias] = entity_info

        print(entity_properties)

    def _rename_field(self, field, new_name, dictionary):
        dictionary[new_name] = dictionary[field]
        del dictionary[field]
        return dictionary



    def _read_pipeline_run_info(self, pri_file):
        encoding = self.task_config["CORPUS_ENCODING"]

        for line in pri_file:
            self.pipeline_run_info = deserialize_line(line, encoding)
            break
