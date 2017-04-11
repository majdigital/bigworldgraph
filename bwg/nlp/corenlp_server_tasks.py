# -*- coding: utf-8 -*-
"""
Rewriting standard tasks for the NLP pipeline using the Stanford CoreNLP server. The main motivation to do this lies
in the following problem: When the respective Stanford tools are run through their NLTK wrappers, they load their
necessary models from scratch every time. This slows down the pipeline quite a load. In contrast, the server loads them
only once.

Also, this approach comes with some other merits as well:
    * Reducing the number of necessary Stanford model files
    * Avoiding using bulk operations like "parse_sents()" which complicate the current architecture of the pipeline
"""

# PROJECT
from bwg.nlp.mixins import CoreNLPServerMixin
from bwg.nlp.standard_tasks import (
    NERTask,
    DependencyParseTask,
    PoSTaggingTask,
    NaiveOpenRelationExtractionTask
)


class ServerNERTask(CoreNLPServerMixin, NERTask):
    """
    Luigi task that performs Named Entity Recognition on a corpus, but using a Stanford CoreNLP server.
    """
    def _ner_tag(self, sentence_data, **workflow_resources):
        """
        Tag a single sentence with named entities using a Stanford CoreNLP server.
        """
        corenlp_server = workflow_resources["corenlp_server"]

        return self.process_sentence_with_corenlp_server(
            sentence_data, action="ner", server=corenlp_server,
            postprocessing_func=self._postprocess_ner_tagged,
        )

    def _postprocess_ner_tagged(self, result_json):
        if len(result_json["sentences"]) == 0:
            return []

        token_dicts = result_json["sentences"][0]["tokens"]
        return [
            (token_dict["word"], token_dict["ner"])
            for token_dict in token_dicts
        ]


class ServerDependencyParseTask(CoreNLPServerMixin, DependencyParseTask):
    """
    Luigi task that dependency-parses sentences in a corpus, but using a Stanford CoreNLP server.
    """
    def _dependency_parse(self, sentence_data, **workflow_resources):
        """
        Dependency parse a sentence using a Stanford CoreNLP server.
        """
        corenlp_server = workflow_resources["corenlp_server"]

        return self.process_sentence_with_corenlp_server(
            sentence_data, action="depparse", server=corenlp_server,
            postprocessing_func=self._postprocess_dependency_parsed,
        )

    def _postprocess_dependency_parsed(self, result_json):
        if len(result_json["sentences"]) == 0:
            return []

        edges = result_json["sentences"][0]["basicDependencies"]
        return self.edges_to_nodes(edges)

    def edges_to_nodes(self, edges):
        nodes = {}

        for edge in edges:
            # Create not if they don't exist
            governing_address = edge["governor"]
            if governing_address not in nodes:
                nodes[governing_address] = self._create_node(governing_address, edge["governorGloss"], None)

            dependent_address = edge["dependent"]
            if dependent_address not in nodes:
                nodes[dependent_address] = self._create_node(dependent_address, edge["dependentGloss"], edge["dep"])

            elif nodes[dependent_address]["rel"] is None:
                nodes[dependent_address]["rel"] = edge["dep"]

            # Create connections if they don't exist
            if dependent_address not in nodes[governing_address]["deps"]:
                if edge["dep"] in nodes[governing_address]["deps"]:
                    nodes[governing_address]["deps"][edge["dep"]].append(dependent_address)
                else:
                    nodes[governing_address]["deps"][edge["dep"]] = [dependent_address]

        root = [node for node_address, node in nodes.items() if node["rel"] == "ROOT"][0]

        return {
            "nodes": nodes,
            "root": root
        }

    @staticmethod
    def _create_node(node_address, node_gloss, node_rel):
        return {
            "address": node_address,
            "word": node_gloss,
            "rel": node_rel,
            "deps": {}
        }


class ServerPoSTaggingTask(CoreNLPServerMixin, PoSTaggingTask):
    """
    Luigi task that PoS tags a sentence in a corpus, but using a Stanford CoreNLP server.
    """
    def _pos_tag(self, sentence_data, **workflow_resources):
        """
        Tag a single sentence with Part-of-Speech tags using a Stanford CoreNLP server.
        """
        corenlp_server = workflow_resources["corenlp_server"]

        return self.process_sentence_with_corenlp_server(
            sentence_data, action="pos", server=corenlp_server,
            postprocessing_func=self._postprocess_pos_tagged,
        )

    def _postprocess_pos_tagged(self, result_json):
        if len(result_json["sentences"]) == 0:
            return []

        token_dicts = result_json["sentences"][0]["tokens"]
        return [
            (token_dict["word"], token_dict["pos"])
            for token_dict in token_dicts
        ]


class ServerNaiveOpenRelationExtractionTask(NaiveOpenRelationExtractionTask):
    """
    Luigi task that performs Open Relation extraction on a corpus. The only adjustment in this case are the requirements
    for this task, this task doesn't use the CoreNLP server at all.
    """
    def requires(self):
        return ServerNERTask(task_config=self.task_config),\
               ServerDependencyParseTask(task_config=self.task_config),\
               ServerPoSTaggingTask(task_config=self.task_config)
