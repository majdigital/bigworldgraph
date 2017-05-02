# -*- coding: utf-8 -*-
"""
Defining additional tasks for the NLP pipeline.
"""

# STD
import datetime
import time

# EXT
import luigi
import luigi.format

from bwg.helpers import time_function
from bwg.neo4j import Neo4jTarget
from bwg.nlp.mixins import ArticleProcessingMixin
# PROJECT
from bwg.nlp.standard_tasks import NaiveOpenRelationExtractionTask, ParticipationExtractionTask
from bwg.nlp.utilities import serialize_relation, deserialize_line, just_dump
from bwg.nlp.wikipedia_tasks import PropertiesCompletionTask, WikipediaReadingTask


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
        """
        Create relation tuples based on a sentence JSON object.
        
        :param sentence_json: Sentence as JSON object.
        :type sentence_json: dict
        :return: List of relations as tuples.
        :rtype: list
        """
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
        
        :return: Result of check.
        :rtype: bool
        """
        return len(article["data"]) > 0

    def _is_relevant_sentence(self, sentence):
        """
        Override ArticleProcessingMixin's relevance criterion.
        
        :return: Result of check.
        :rtype: bool
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
        ne_tag_to_model = self.task_config["NEO4J_NETAG2MODEL"]
        user = self.task_config["NEO4J_USER"]
        password = self.task_config["NEO4J_PASSWORD"]
        return Neo4jTarget(self.pipeline_run_info, user, password, ne_tag_to_model=ne_tag_to_model)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input()[0].open("r") as mr_file, self.input()[1].open("r") as pc_file,\
                self.input()[1].open("r") as pri_file:
            self._read_pipeline_run_info(pri_file)
            entity_properties = self._read_properties_file(pc_file)
            with self.output() as database:
                for mr_line in mr_file:
                    self.process_article(mr_line, database, entity_properties)

    @time_function(is_classmethod=True)
    def process_article(self, raw_article, database, entity_properties):
        """
        Process an article generated by previous tasks and process them.
        
        :param raw_article: Raw unserialized article.
        :type raw_article: str
        :param database: Neo4j luigi target.
        :type database: bwg.db.neo4j.Neo4jTarget
        :param entity_properties: Wikidata properties of all entities as dictionary.
        :type entity_properties: dict
        """
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
                database.add_relation(relation_json, sentence_json["data"]["sentence"], entity_properties)

    def _read_properties_file(self, properties_file):
        """
        Read all Wikidata properties from properties file.
        
        :param properties_file: File with Wikidata properties.
        :type properties_file: luigi.Target.
        :return: Wikidata properties of all entities as dictionary.
        :rtype: dict
        """
        encoding = self.task_config["CORPUS_ENCODING"]
        entity_properties = {}

        for line in properties_file:
            article = deserialize_line(line, encoding)
            article_meta, article_data = article["meta"], article["data"]

            entity_properties.update(self._extract_properties(article_data))

        return entity_properties

    def _extract_properties(self, article_data):
        """
        Extract all Wikidata properties from an article's data.
        
        :param article_data: Article data.
        :type article_data: dict
        :return: All properties of entities in this article.
        :rtype: dict
        """
        entity_properties = {}

        for sentence_id, sentence_json in article_data.items():
            sentence_meta, sentence_data = sentence_json["meta"], sentence_json["data"]

            for entity_id, entity_json in sentence_data["entities"].items():
                entity_meta, entity_data = entity_json["meta"], entity_json["data"]

                if entity_meta["type"] == "Ambiguous Wikidata entity":
                    new_entity_data = {
                        "ambiguous": True,
                        "senses": [self._convert_entity_sense(entity_sense) for entity_sense in entity_data]
                    }

                    for entity_sense in new_entity_data["senses"]:
                        entity_properties = self._add_entity_data_to_properties_dict(entity_sense, entity_properties)

                else:
                    new_entity_data = self._convert_entity_sense(entity_data[0])
                    new_entity_data["ambiguous"] = False

                    entity_properties = self._add_entity_data_to_properties_dict(new_entity_data, entity_properties)

        return entity_properties

    @staticmethod
    def _add_entity_data_to_properties_dict(entity_data, entity_properties):
        """
        Add an entity and its aliases to the properties dictionary.
        
        :param entity_data: Data of target entity.
        :type entity_data: dict
        :param entity_properties: Properties_dictionary that the entity and its aliases are added to. 
        :type entity_properties: dict
        :return: Properties dictionary with new entry.
        :rtype: dict
        """
        if "label" not in entity_data:
            return entity_properties

        entity_properties[entity_data["label"]] = entity_data

        if "aliases" in entity_data:
            for alias in entity_data["aliases"]:
                # Adjust label and aliases appropriatly
                alias_entity_data = dict(entity_data)
                alias_entity_data["label"] = alias
                alias_entity_data["aliases"].remove(alias)
                alias_entity_data["aliases"].append(entity_data["label"])
                entity_properties[alias] = alias_entity_data

        return entity_properties

    def _convert_entity_sense(self, entity_data):
        """
        Rename some fields for clarity.
        
        :param entity_data: Data with fields to be renamed.
        :type entity_data: dict
        :return: Data with renamed fields.
        :rtype: dict
        """
        new_entity_data = dict(entity_data)
        new_entity_data = self._rename_field("modified", "wikidata_last_modified", new_entity_data)
        new_entity_data = self._rename_field("id", "wikidata_id", new_entity_data)

        return new_entity_data

    @staticmethod
    def _rename_field(field, new_name, dictionary):
        """
        Rename a field in a dictionary.
        
        :param field: Field to be renamed.
        :type field: str
        :param new_name: New name of field.
        :type new_name: str
        :param dictionary: Dictionary in which the field occurs.
        :type dictionary: dict
        :return: Dictionary with renamed field.
        :rtype: dict
        """
        dictionary[new_name] = dictionary[field]
        del dictionary[field]
        return dictionary

    def _read_pipeline_run_info(self, pri_file):
        """
        Read the current pipeline run info.
        
        :param pri_file: File with pipeline run info.
        :type: Luigi.target.
        :return: Pipeline run info.
        :rtype: dict
        """
        encoding = self.task_config["CORPUS_ENCODING"]

        for line in pri_file:
            self.pipeline_run_info = deserialize_line(line, encoding)
            break
