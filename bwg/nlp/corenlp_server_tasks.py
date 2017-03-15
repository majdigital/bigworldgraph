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


class ServerNERTask(NERTask, CoreNLPServerMixin):
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

    @staticmethod
    def _postprocess_ner_tagged(result_json):
        token_dicts = result_json["sentences"][0]["tokens"]
        return [
            (token_dict["word"], token_dict["ner"])
            for token_dict in token_dicts
        ]


class ServerDependencyParseTask(DependencyParseTask, CoreNLPServerMixin):
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

    @staticmethod
    def _postprocess_dependency_parsed(result_json):
        return result_json["sentences"][0]["basicDependencies"]


class ServerPoSTaggingTask(PoSTaggingTask, CoreNLPServerMixin):
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

    @staticmethod
    def _postprocess_pos_tagged(result_json):
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
