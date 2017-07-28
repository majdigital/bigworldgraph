import luigi

from bwg.decorators import time_function
from bwg.mixins import ArticleProcessingMixin
from bwg.serializing import serialize_relation, get_nes_from_sentence
from bwg.tasks.ner import NERTask


class ParticipationExtractionTask(luigi.Task, ArticleProcessingMixin):
    """
    Luigi task that extracts all Named Entity participating in an issue or topic.
    """
    def requires(self):
        return NERTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["PE_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        with self.input().open("r") as nes_input_file, self.output().open("w") as output_file:
            for nes_line in nes_input_file:
                self.process_articles(
                    nes_line, new_state="extracted_participations",
                    serializing_function=serialize_relation, output_file=output_file
                )

    def task_workflow(self, article, **workflow_resources):
        article_meta, article_data = article["meta"], article["data"]
        article_title = article_meta["title"]
        participation_phrases = self.task_config["PARTICIPATION_PHRASES"]
        default_ne_tag = self.task_config["DEFAULT_NE_TAG"]

        for sentence_id, sentence_json in article_data.items():
            nes = get_nes_from_sentence(sentence_json["data"], default_ne_tag, True)
            relations = self._build_participation_relations(nes, article_title, participation_phrases)
            sentence = self._get_sentence(sentence_json["data"])

            serializing_arguments = {
                "sentence_id": sentence_id,
                "sentence": sentence,
                "relations": relations,
                "infix": "PE"
            }

            yield serializing_arguments

    @staticmethod
    def _build_participation_relations(nes, title, participation_phrases):
        """
        Build participation relations based on the Named entities in a sentence, the current articles titles and a
        dictionary of specific phrases for each Named entity tag.

        :param nes: List of named entities in the current sentence.
        :type nes: list
        :param title: Title of current article.
        :type title: str
        :param participation_phrases: Dictionary of participation phrases for different Named Entity tags.
        :type participation_phrases: dict
        :return: List of participation relations.
        :rtype: list
        """
        return [
            (ne, participation_phrases.get(tag, participation_phrases["DEFAULT"]), title) for ne, tag in nes
        ]

    @staticmethod
    def _get_sentence(sentence_data):
        """
        Get the original (not de-tokenized) sentence from a line tagged with NE tags.

        :param sentence_data: Sentence with Named Entity tags.
        :type sentence_data: list
        :return: Raw sentence.
        :rtype: str
        """
        return " ".join([word for word, ne_tag in sentence_data])