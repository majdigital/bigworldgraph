# EXT
import luigi
from nltk import StanfordTokenizer, StanfordPOSTagger

# PROJECT
from bwg.decorators import time_function
from bwg.mixins import ArticleProcessingMixin
from bwg.serializing import serialize_tagged_sentence
from bwg.tasks.reading_tasks import WikipediaReadingTask


class PoSTaggingTask(luigi.Task, ArticleProcessingMixin):
    """
    Luigi task that PoS tags a sentence in a corpus.
    """
    def requires(self):
        return WikipediaReadingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["POS_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_articles(
                    line, new_state="pos_tagged", serializing_function=serialize_tagged_sentence,
                    output_file=output_file
                )

    @property
    def workflow_resources(self):
        corpus_encoding = self.task_config["CORPUS_ENCODING"]
        stanford_postagger_path = self.task_config["STANFORD_POSTAGGER_PATH"]
        stanford_models_path = self.task_config["STANFORD_MODELS_PATH"]
        stanford_pos_model_path = self.task_config["STANFORD_POS_MODEL_PATH"]

        tokenizer = StanfordTokenizer(stanford_models_path, encoding=corpus_encoding)
        pos_tagger = StanfordPOSTagger(
            stanford_pos_model_path, path_to_jar=stanford_postagger_path, encoding=corpus_encoding
        )

        workflow_resources = {
            "tokenizer": tokenizer,
            "pos_tagger": pos_tagger
        }

        return workflow_resources

    def task_workflow(self, article, **workflow_resources):
        article_data = article["data"]

        for sentence_id, sentence_json in article_data.items():
            sentence_data = sentence_json["data"]
            pos_tagged_sentence = self._pos_tag(sentence_data, **workflow_resources)

            serializing_arguments = {
                "sentence_id": sentence_id,
                "tagged_sentence": pos_tagged_sentence
            }

            yield serializing_arguments

    def _pos_tag(self, sentence_data, **workflow_resources):
        """
        Tag a single sentence with Part-of-Speech tags.

        Tag a single sentence with Part-of-Speech tags using a Stanford CoreNLP server.

        :param sentence_data: Data of the sentence that is going to be pos tagged.
        :type sentence_data: dict
        :param workflow_resources: Additional resources for this step.
        :type workflow_resources: dict
        :return: Processed sentence.
        :rtype: dict
        """
        tokenizer = workflow_resources["tokenizer"]
        pos_tagger = workflow_resources["pos_tagger"]

        tokenized_sentence = tokenizer.tokenize(sentence_data)
        pos_tagged_sentence = pos_tagger.tag(tokenized_sentence)

        return pos_tagged_sentence