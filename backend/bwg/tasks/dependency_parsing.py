import luigi
from nltk.parse.stanford import StanfordDependencyParser

from bwg.decorators import time_function
from bwg.mixins import ArticleProcessingMixin
from bwg.serializing import serialize_dependency_parse_tree
from bwg.tasks.reading_tasks import WikipediaReadingTask


class DependencyParseTask(luigi.Task, ArticleProcessingMixin):
    """
    Luigi task that dependency-parses sentences in a corpus.
    """
    def requires(self):
        return WikipediaReadingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["DEPENDENCY_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_articles(
                    line, new_state="dependency_parsed",
                    serializing_function=serialize_dependency_parse_tree, output_file=output_file,
                )

    @property
    def workflow_resources(self):
        corpus_encoding = self.task_config["CORPUS_ENCODING"]
        stanford_dependency_model_path = self.task_config["STANFORD_DEPENDENCY_MODEL_PATH"]
        stanford_corenlp_models_path = self.task_config["STANFORD_CORENLP_MODELS_PATH"]

        dependency_parser = StanfordDependencyParser(
            stanford_dependency_model_path, stanford_corenlp_models_path, encoding=corpus_encoding
        )

        workflow_resources = {
            "dependency_parser": dependency_parser
        }

        return workflow_resources

    def task_workflow(self, article, **workflow_resources):
        article_data = article["data"]

        for sentence_id, sentence_json in article_data.items():
            sentence_data = sentence_json["data"]
            parsed_sentence = self._dependency_parse(sentence_data, **workflow_resources)

            serializing_arguments = {
                "sentence_id": sentence_id,
                "parse_trees": parsed_sentence
            }

            yield serializing_arguments

    def _dependency_parse(self, sentence_data, **workflow_resources):
        """
        Dependency parse a sentence.

        :param sentence_data: Data of the sentence that is going to be dependency parsed.
        :type sentence_data: dict
        :param workflow_resources: Additional resources for this step.
        :type workflow_resources: dict
        :return: Processed sentence.
        :rtype: dict
        """
        dependency_parser = workflow_resources["dependency_parser"]

        parsed_sentence = dependency_parser.raw_parse(sentence_data)

        return parsed_sentence