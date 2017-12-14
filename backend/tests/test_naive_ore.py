# STD
import copy
import json
import unittest
from unittest import mock as mock

# PROJECT
import bwg
from bwg.tasks.naive_ore import NaiveOpenRelationExtractionTask
from tests.fixtures import NAIVE_OPEN_RELATION_EXTRACTION_TASK, DEPENDENCY_TREE, NE_TAGGED_PINEAPPLE_SENTENCE, \
    NE_DEPENDENCY_PINEAPPLE_TREE
from tests.toolkit import MockOutput, MockInput


class NaiveOpenRelationExtractionTaskTestCase(unittest.TestCase):
    """
    Testing NaiveOpenRelatioNExtractionTask.
    """
    @mock.patch('bwg.tasks.naive_ore.rst.NaiveOpenRelationExtractionTask.output')
    @mock.patch('bwg.tasks.naive_ore.rst.NaiveOpenRelationExtractionTask.input')
    def test_task_functions(self, input_patch, output_patch):
        with mock.patch(
            "bwg.tasks.naive_ore.rst.NaiveOpenRelationExtractionTask.workflow_resources", new_callable=mock.PropertyMock()
        ) as workflow_mock:
            task_config = {
                "NER_TAGSET": ["I-P", "I-N"],
                "DEFAULT_NE_TAG": "O",
                "VERB_NODE_POS_TAGS": ["VV"],
                "OMITTED_TOKENS_FOR_ALIGNMENT": [],
                "CORPUS_ENCODING": "",
                "ORE_OUTPUT_PATH": ""
            }

            output_patch.return_value = MockOutput()
            input_patch.return_value = (
                MockInput(NAIVE_OPEN_RELATION_EXTRACTION_TASK["input"][0]),
                MockInput(NAIVE_OPEN_RELATION_EXTRACTION_TASK["input"][1]),
                MockInput(NAIVE_OPEN_RELATION_EXTRACTION_TASK["input"][2])
            )
            workflow_mock.__get__ = mock.Mock(return_value={})

            task = bwg.tasks.naive_ore.NaiveOpenRelationExtractionTask(task_config=task_config)

            # Testing
            self._test_task(task)
            self._test_extract_relations_from_sentence(task)
            self._test_get_sentence()
            self._test_align_tagged_sentence(task)
            self._test_normalize_node_addresses()
            self._test_extract_verb_nodes(task)
            self._test_expand_node(task)
            self._test_word_is_ne_tagged(task)
            self._test_join_expanded_node()
            self._test_get_subj_and_obj()
            self._test_extract_relations(task)

    @staticmethod
    def _test_task(task):
        task.run()
        output_mock = task.output()
        assert [json.loads(content, encoding="utf-8") for content in output_mock.contents] == \
               NAIVE_OPEN_RELATION_EXTRACTION_TASK["output"]

    @staticmethod
    def _test_extract_relations_from_sentence(task):
        ne_tagged_line = [("pineapples", "I-P"), ("are", "O"), ("juicy", "I-N"), ("fruits", "I-N")]
        pos_tagged_line = [("pineapples", "NN"), ("are", "VV"), ("juicy", "ADJ"), ("fruits", "NN")]
        dependency_tree = copy.deepcopy(NE_DEPENDENCY_PINEAPPLE_TREE)
        sentence_dates = {
            "data_ne_tagged": {"data": ne_tagged_line},
            "data_dependency_parsed": {"data": dependency_tree},
            "data_pos_tagged": {"data": pos_tagged_line}
        }

        assert task._extract_relations_from_sentence(sentence_dates) == (
            [("pineapples", "are", "juicy fruits")], "pineapples are juicy fruits"
        )

    @staticmethod
    def _test_get_sentence():
        tagged_sentence = NE_TAGGED_PINEAPPLE_SENTENCE
        assert NaiveOpenRelationExtractionTask._get_sentence(tagged_sentence) == \
               "this pineapple is part of a sample sentence in an article"

    @staticmethod
    def _test_align_tagged_sentence(task):
        assert task._align_tagged_sentence(NE_TAGGED_PINEAPPLE_SENTENCE) == NE_TAGGED_PINEAPPLE_SENTENCE

        # TODO (Bug): Find a way to do this test [DU 22.06.17]
        #new_config = {"OMITTED_TOKENS_FOR_ALIGNMENT": [token for token, _ in NE_TAGGED_PINEAPPLE_SENTENCE]}
        #with mock.patch("bwg.tasks.dependency_parsing.py.NaiveOpenRelationExtractionTask.task_config", return_value=new_config):
        #    assert task._align_tagged_sentence(NE_TAGGED_PINEAPPLE_SENTENCE) == []

    @staticmethod
    def _test_normalize_node_addresses():
        empty_tree = {"nodes": {}, "root": {}}
        assert NaiveOpenRelationExtractionTask._normalize_node_addresses(empty_tree) == empty_tree

        normalized_tree = NaiveOpenRelationExtractionTask._normalize_node_addresses(DEPENDENCY_TREE)
        assert normalized_tree["nodes"][0]["word"] not in (None, "ROOT")
        assert normalized_tree["root"]["word"] not in (None, "ROOT")

    @staticmethod
    def _test_extract_verb_nodes(task):
        dependency_tree = NE_DEPENDENCY_PINEAPPLE_TREE
        pos_tagged_line = [("pineapples", "NN"), ("are", "VV"), ("juicy", "ADJ"), ("fruits", "NN")]

        assert task._extract_verb_nodes({"nodes": {}}, []) == []
        assert task._extract_verb_nodes(dependency_tree, pos_tagged_line) == [dependency_tree["nodes"][1]]

    @staticmethod
    def _test_expand_node(task):
        dependecy_tree = copy.deepcopy(NE_DEPENDENCY_PINEAPPLE_TREE)
        fruits_node, verb_node = dependecy_tree["nodes"][3], dependecy_tree["nodes"][1]
        juicy_node = dependecy_tree["nodes"][2]
        assert task._expand_node(verb_node, dependecy_tree, is_verb_node=True) == [
            (verb_node["address"], verb_node["word"])
        ]
        assert task._expand_node(fruits_node, dependecy_tree) == [
            (fruits_node["address"], fruits_node["word"]), (juicy_node["address"], juicy_node["word"])
        ]

    @staticmethod
    def _test_word_is_ne_tagged(task):
        assert task._word_is_ne_tagged(0, [("word", "I-P")])
        assert task._word_is_ne_tagged(0, [("Another word", "I-N")])
        assert not task._word_is_ne_tagged(0, [("untagged word", "O")])

    @staticmethod
    def _test_expanded_node_is_ne_tagged(task):
        ne_tagged_line = [
            ("this", "O"), ("is", "O"), ("an", "I-N"), ("expanded", "I-N"), ("node", "I-N"), ("and", "O"), ("a", "I-P"),
            ("pineapple", "I-P")
        ]
        assert task._expanded_node_is_ne_tagged([(2, "an"), (3, "expanded"), (4, "node")], ne_tagged_line)
        assert task._expanded_node_is_ne_tagged([(6, "a"), (7, "pineapple")], ne_tagged_line)
        assert not task._expanded_node_is_ne_tagged([(0, "this"), (1, "is")], ne_tagged_line)

    @staticmethod
    def _test_join_expanded_node():
        assert NaiveOpenRelationExtractionTask._join_expanded_node([(6, "a"), (7, "pineapple")]) == "a pineapple"
        assert NaiveOpenRelationExtractionTask._join_expanded_node(
            [(3, "expanded"), (2, "an"), (4, "node")]
        ) == "an expanded node"
        assert NaiveOpenRelationExtractionTask._join_expanded_node([(5, "word")]) == "word"

    @staticmethod
    def _test_get_subj_and_obj():
        dependency_tree = copy.deepcopy(NE_DEPENDENCY_PINEAPPLE_TREE)
        verb_node = dependency_tree["nodes"][1]
        subj_node, obj_node = dependency_tree["nodes"][0], dependency_tree["nodes"][3]
        assert NaiveOpenRelationExtractionTask._get_subj_and_obj(verb_node, dependency_tree) == (subj_node, obj_node)

    @staticmethod
    def _test_extract_relations(task):
        ne_tagged_line = [("pineapples", "I-P"), ("are", "O"), ("juicy", "I-N"), ("fruits", "I-N")]
        pos_tagged_line = [("pineapples", "NN"), ("are", "VV"), ("juicy", "ADJ"), ("fruits", "NN")]
        dependency_tree = copy.deepcopy(NE_DEPENDENCY_PINEAPPLE_TREE)

        assert task.extract_relations(ne_tagged_line, dependency_tree, pos_tagged_line) == [
            ("pineapples", "are", "juicy fruits")
        ]