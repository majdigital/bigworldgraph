# STD
import json
import unittest
from unittest import mock as mock

# PROJECT
import bwg
from tests.fixtures import NER_TASK
from tests.mock_nlp import MockTokenizer, MockTagger
from tests.test_participation_extraction import NE_TAGGED_PINEAPPLE_SENTENCE
from tests.toolkit import MockOutput, MockInput


class NERTaskTestCase(unittest.TestCase):
    """
    Testing NERTask.
    """
    @mock.patch('bwg.tasks.ner.NERTask.output')
    @mock.patch('bwg.tasks.ner.NERTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
            "bwg.tasks.ner.NERTask.workflow_resources", new_callable=mock.PropertyMock()
        ) as workflow_mock:

            task_config = {
                "STANFORD_MODELS_PATH": "",
                "STANFORD_NER_MODEL_PATH": "",
                "CORPUS_ENCODING": "",
                "WIKIPEDIA_READING_OUTPUT_PATH": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = MockInput(NER_TASK["input"])
            workflow_mock.__get__ = mock.Mock(
                return_value={
                    "tokenizer": MockTokenizer(),
                    "ner_tagger": MockTagger(self.naive_ner_tag)
                }
            )

            task = bwg.tasks.ner.NERTask(task_config=task_config)

            # Testing
            self._test_task(task)
            self._test_ner_tag(task)

    @staticmethod
    def naive_ner_tag(token, tokenized_sentence):
        tag_rules = {
            "sample": "I-N",
            "article": "I-N",
            "pineapple": "I-P"
        }

        if token in tag_rules:
            return token, tag_rules[token]
        return token, "O"

    @staticmethod
    def _test_task(task):
        task.run()
        output_mock = task.output()
        assert [json.loads(content, encoding="utf-8") for content in output_mock.contents] == NER_TASK["output"]

    @staticmethod
    def _test_ner_tag(task):
        sentence_data = "this pineapple is part of a sample sentence in an article"
        ner_tagged_sentence = task._ner_tag(sentence_data, **task.workflow_resources)
        assert ner_tagged_sentence == NE_TAGGED_PINEAPPLE_SENTENCE