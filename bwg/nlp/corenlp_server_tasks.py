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
from bwg.nlp.standard_tasks import (
    NERTask,
    DependencyParseTask,
    PoSTaggingTask,
    NaiveOpenRelationExtractionTask
)


class ServerNERTask(NERTask):
    """
    Luigi task that performs Named Entity Recognition on a corpus, but using a Stanford CoreNLP server.
    """
    def requires(self):
        # TODO (Feature): Implement
        pass

    @property
    def workflow_resources(self):
        # TODO (Feature): Implement
        workflow_resources = {}

        return workflow_resources

    def _ner_tag(self, sentence_data, **workflow_resources):
        """
        Tag a single sentence with named entities using a Stanford CoreNLP server.
        """
        # TODO (Feature): Implement
        pass


class ServerDependencyParseTask(DependencyParseTask):
    """
    Luigi task that dependency-parses sentences in a corpus, but using a Stanford CoreNLP server.
    """
    def requires(self):
        # TODO (Feature): Implement
        pass

    @property
    def workflow_resources(self):
        # TODO (Feature): Implement
        workflow_resources = {}

        return workflow_resources

    def _dependency_parse(self, sentence_data, **workflow_resources):
        """
        Dependency parse a sentence using a Stanford CoreNLP server.
        """
        # TODO (Feature): Implement
        pass


class ServerPoSTaggingTask(PoSTaggingTask):
    """
    Luigi task that PoS tags a sentence in a corpus, but using a Stanford CoreNLP server.
    """
    def requires(self):
        # TODO (Feature): Implement
        pass

    @property
    def workflow_resources(self):
        # TODO (Feature): Implement
        workflow_resources = {}

        return workflow_resources

    def _pos_tag(self, sentence_data, **workflow_resources):
        """
        Tag a single sentence with Part-of-Speech tags using a Stanford CoreNLP server.
        """
        # TODO (Feature): Implement
        pass


class ServerNaiveOpenRelationExtractionTask(NaiveOpenRelationExtractionTask):
    """
    Luigi task that performs Open Relation extraction on a corpus. The only adjustment in this case are the requirements
    for this task, this task doesn't use the CoreNLP server at all.
    """
    def requires(self):
        return ServerNERTask(task_config=self.task_config),\
               ServerDependencyParseTask(task_config=self.task_config),\
               ServerPoSTaggingTask(task_config=self.task_config)
