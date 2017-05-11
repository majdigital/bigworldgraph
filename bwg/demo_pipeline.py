# -*- coding: utf-8 -*-
"""
Demo pipeline to demonstrate configuration management and the way ``Luigi`` pipelines are used in this project.
"""

# EXT
import luigi

# PROJECT
from bwg.helpers import time_function
from bwg.mixins import ArticleProcessingMixin
from bwg.standard_tasks import SimpleReadingTask
from bwg.utilities import serialize_sentence
from bwg.config_management import build_task_config_for_language


class DemoTask1(luigi.Task, ArticleProcessingMixin):
    """
    Tasks that reads in the demo corpus and replaces pre-defined characters with an x.
    """
    def requires(self):
        return SimpleReadingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["REPLACED_CORPUS_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_articles(
                    line, new_state="replaced", serializing_function=serialize_sentence, output_file=output_file
                )

    def task_workflow(self, article, **workflow_resources):
        article_data = article["data"]
        replace_characters = self.task_config["REPLACE_CHARACTERS"]

        for sentence_id, sentence_json in article_data.items():
            sentence = sentence_json["data"]

            for replace_character in replace_characters:
                sentence = sentence.replace(replace_character, "x")

            serializing_arguments = {
                "sentence_id": sentence_id,
                "sentence": sentence
            }

            yield serializing_arguments


class DemoTask2(luigi.Task, ArticleProcessingMixin):
    """
    Task that duplicates pre-defined characters.
    """
    def requires(self):
        return DemoTask1(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["DUPLICATED_CORPUS_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_articles(
                    line, new_state="duplicated", serializing_function=serialize_sentence, output_file=output_file
                )

    def task_workflow(self, article, **workflow_resources):
        article_data = article["data"]
        duplicate_characters = self.task_config["DUPLICATE_CHARACTERS"]

        for sentence_id, sentence_json in article_data.items():
            sentence = sentence_json["data"]

            for duplicate_character in duplicate_characters:
                sentence = sentence.replace(duplicate_character, duplicate_character*2)

            serializing_arguments = {
                "sentence_id": sentence_id,
                "sentence": sentence
            }

            yield serializing_arguments


class DemoTask3(luigi.Task, ArticleProcessingMixin):
    """
    Task that removes pre-defined characters.
    """
    def requires(self):
        return DemoTask2(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["REMOVED_CORPUS_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_articles(
                    line, new_state="removed", serializing_function=serialize_sentence, output_file=output_file,
                    pretty=True
                )

    def task_workflow(self, article, **workflow_resources):
        article_data = article["data"]
        remove_characters = self.task_config["REMOVE_CHARACTERS"]

        for sentence_id, sentence_json in article_data.items():
            sentence = sentence_json["data"]

            for remove_character in remove_characters:
                sentence = sentence.replace(remove_character, "")

            serializing_arguments = {
                "sentence_id": sentence_id,
                "sentence": sentence
            }

            yield serializing_arguments


if __name__ == "__main__":
    demo_task_config = build_task_config_for_language(
        # List tasks used in this pipeline
        tasks=[
            "simple_reading",
            "demo_task1",
            "demo_task2",
            "demo_task3"
        ],
        language="demo",
        config_file_path="./demo_pipeline_config.py"
    )

    # Run the pipeline
    luigi.build(
        [DemoTask3(task_config=demo_task_config)],
        local_scheduler=True, workers=1, log_level="INFO"
    )


