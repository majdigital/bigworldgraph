# STD
import json
import unittest
from unittest import mock as mock

# PROJECT
import bwg
from tests.fixtures import POS_TAGGING_TASK
from tests.mock_nlp import MockTokenizer, MockTagger
from tests.toolkit import MockOutput, MockInput


class PoSTaggingTaskTestCase(unittest.TestCase):
    """
    Testing PoSTaggingTask.
    """
    @mock.patch('bwg.tasks.pos_tagging.PoSTaggingTask.output')
    @mock.patch('bwg.tasks.pos_tagging.PoSTaggingTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
                "bwg.tasks.pos_tagging.PoSTaggingTask.workflow_resources", new_callable=mock.PropertyMock()
        ) as workflow_mock:
            task_config = {
                "STANFORD_POSTAGGER_PATH": "",
                "STANFORD_MODELS_PATH": "",
                "STANFORD_POS_MODEL_PATH": "",
                "CORPUS_ENCODING": "",
                "POS_OUTPUT_PATH": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = MockInput(POS_TAGGING_TASK["input"])
            workflow_mock.__get__ = mock.Mock(
                return_value={
                    "tokenizer": MockTokenizer(),
                    "pos_tagger": MockTagger(self.naive_pos_tag)
                }
            )

            task = bwg.tasks.pos_tagging.PoSTaggingTask(task_config=task_config)

            # Testing
            self._test_task(task)
            self._test_pos_tag(task)

    @staticmethod
    def naive_pos_tag(token, tokenized_sentence):
        tag_rules = {
            "sample": "ADJ",
            "article": "NN",
            "pineapple": "NN",
            "first": "ADJ",
            "sentence": "NN",
            "the": "DET",
            "second": "ADJ",
            "this": "DET",
            "is": "VV",
            "a": "DET"
        }

        if token in tag_rules:
            return token, tag_rules[token]
        return token, "UKW"

    @staticmethod
    def _test_task(task):
        task.run()
        output_mock = task.output()
        assert [json.loads(content, encoding="utf-8") for content in output_mock.contents] == POS_TAGGING_TASK["output"]

    @staticmethod
    def _test_pos_tag(task):
        sentence_data = "this pineapple is a sentence"
        pos_tagged_sentence = task._pos_tag(sentence_data, **task.workflow_resources)
        assert pos_tagged_sentence == [
            ("this", "DET"), ("pineapple", "NN"), ("is", "VV"), ("a", "DET"), ("sentence", "NN")
        ]