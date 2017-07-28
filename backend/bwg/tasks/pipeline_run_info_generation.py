import datetime
import time

import luigi

from bwg.decorators import time_function
from bwg.serializing import deserialize_line, just_dump
from bwg.tasks.reading_tasks import WikipediaReadingTask


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