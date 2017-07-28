import luigi
from nltk import StanfordTokenizer, StanfordNERTagger

from bwg.decorators import time_function
from bwg.mixins import ArticleProcessingMixin
from bwg.serializing import serialize_tagged_sentence
from bwg.tasks.reading_tasks import WikipediaReadingTask


class NERTask(luigi.Task, ArticleProcessingMixin):
    """
    Luigi task that performs Named Entity Recognition on a corpus.
    """
    def requires(self):
        return WikipediaReadingTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["NES_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file:
                self.process_articles(
                    line, new_state="ne_tagged", serializing_function=serialize_tagged_sentence, output_file=output_file
                )

    @property
    def workflow_resources(self):
        stanford_models_path = self.task_config["STANFORD_MODELS_PATH"]
        stanford_ner_model_path = self.task_config["STANFORD_NER_MODEL_PATH"]
        corpus_encoding = self.task_config["CORPUS_ENCODING"]

        tokenizer = StanfordTokenizer(stanford_models_path, encoding=corpus_encoding)
        ner_tagger = StanfordNERTagger(stanford_ner_model_path, stanford_models_path, encoding=corpus_encoding)

        workflow_resources = {
            "tokenizer": tokenizer,
            "ner_tagger": ner_tagger
        }

        return workflow_resources

    def task_workflow(self, article, **workflow_resources):
        article_data = article["data"]

        for sentence_id, sentence_json in article_data.items():
            sentence_data = sentence_json["data"]
            ner_tagged_sentence = self._ner_tag(sentence_data, **workflow_resources)

            serializing_arguments = {
                "sentence_id": sentence_id,
                "tagged_sentence": ner_tagged_sentence
            }

            yield serializing_arguments

    def _ner_tag(self, sentence_data, **workflow_resources):
        """
        Tag a single sentence with named entities.

        :param sentence_data: Data of the sentence that is going to be named entity tagged.
        :type sentence_data: str
        :param workflow_resources: Additional resources for this step.
        :type workflow_resources: dict
        :return: Processed sentence.
        :rtype: dict
        """
        tokenizer = workflow_resources["tokenizer"]
        ner_tagger = workflow_resources["ner_tagger"]

        tokenized_sentence = tokenizer.tokenize(sentence_data)
        ner_tagged_sentence = ner_tagger.tag(tokenized_sentence)

        return ner_tagged_sentence