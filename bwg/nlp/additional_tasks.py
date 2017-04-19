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
from bwg.db.mongo import MongoDBTarget
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
                    output_file=output_file, pretty=True
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


class DatabaseWritingTask(luigi.Task, ArticleProcessingMixin):
    """
    Writes information extracted from text by means of the NLP pipeline into a database.
    """
    # TODO (Implement)
    pass


class RelationsDatabaseWritingTask(DatabaseWritingTask):
    """
    Writes relations extracted via (naive) Open Relation Extraction and Participation Extraction into a graph database.
    """
    # TODO (Implement) [DU 19.04.17]
    def requires(self):
        RelationMergingTask(task_config=self.task_config)

    def output(self):
        uri = self.task_config["NEO4J_URI"]
        user = self.task_config["NEO4J_USER"]
        password = self.task_config["NEO4J_PASSWORD"]
        schemata = self.task_config["NEO$J_SCHEMATA"]
        return Neo4jTarget(uri, user, password, schemata)


class PropertiesDatabaseWritingTask(DatabaseWritingTask):
    """
    Writes properties of entities extracted from Wikidata into a database.
    """
    # TODO (Implement) [DU 19.04.17]
    def requires(self):
        PropertiesCompletionTask(task_config=self.task_config)

    def output(self):
        # TODO (Implement): Add necessary config parameters [DU 19.04.17]
        pass
        #return MongoDBTarget(task_config=self.task_config)
