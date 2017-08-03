# -*- coding: utf-8 -*-
"""
Testing standard tasks for the NLP pipeline.
"""

# STD
import json
import unittest
import unittest.mock as mock

# PROJECT
import bwg
import bwg.tasks.dependency_parsing
import bwg.tasks.ner
import bwg.tasks.participation_extraction
import bwg.tasks.pos_tagging
from bwg.serializing import get_nes_from_sentence
from bwg.tasks.participation_extraction import ParticipationExtractionTask
from tests.fixtures import (
    PARTICIPATION_EXTRACTION_TASK,
    NE_TAGGED_PINEAPPLE_SENTENCE
)
from tests.toolkit import MockInput, MockOutput


class ParticipationExtractionTaskTestCase(unittest.TestCase):
    """
    Testing ParticipationExtractionTask.
    """
    participation_phrases = {
        "I-P": "is pineappled with",
        "I-N": "is related with",
        "DEFAULT": "is boringly related with"
    }

    @mock.patch('bwg.tasks.participation_extraction.ParticipationExtractionTask.output')
    @mock.patch('bwg.tasks.participation_extraction.ParticipationExtractionTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
            "bwg.tasks.participation_extraction.ParticipationExtractionTask.workflow_resources",
            new_callable=mock.PropertyMock()
        ) as workflow_mock:
            task_config = {
                "DEFAULT_NE_TAG": "O",
                "PARTICIPATION_PHRASES": self.participation_phrases,
                "PE_OUTPUT_PATH": "",
                "CORPUS_ENCODING": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = MockInput(PARTICIPATION_EXTRACTION_TASK["input"])
            workflow_mock.__get__ = mock.Mock(return_value={})

            task = bwg.tasks.participation_extraction.ParticipationExtractionTask(task_config=task_config)

            # Testing
            self._test_task(task)
            self._test_build_participation_relations()
            self._test_get_sentence()

    @staticmethod
    def _test_task(task):
        task.run()
        output_mock = task.output()
        assert [json.loads(content, encoding="utf-8") for content in output_mock.contents] == \
               PARTICIPATION_EXTRACTION_TASK["output"]

    def _test_build_participation_relations(self):
        nes = get_nes_from_sentence(NE_TAGGED_PINEAPPLE_SENTENCE, "O", True)
        assert ParticipationExtractionTask._build_participation_relations(
            nes, "The pineapple affair", self.participation_phrases
        ) == [
            ('pineapple', 'is pineappled with', 'The pineapple affair'),
            ('sample', 'is related with', 'The pineapple affair')
        ]

    @staticmethod
    def _test_get_sentence():
        tagged_sentence = NE_TAGGED_PINEAPPLE_SENTENCE
        assert ParticipationExtractionTask._get_sentence(tagged_sentence) == \
               "this pineapple is part of a sample sentence in an article"
