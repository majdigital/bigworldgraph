import luigi

from bwg.decorators import time_function
from bwg.mixins import ArticleProcessingMixin
from bwg.serializing import serialize_relation
from bwg.tasks.naive_ore import NaiveOpenRelationExtractionTask
from bwg.tasks.participation_extraction import ParticipationExtractionTask


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