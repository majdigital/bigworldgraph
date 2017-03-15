# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

# EXT
import luigi.format
import nltk

# PROJECT
from bwg.misc.helpers import download_nltk_resource_if_missing
from bwg.nlp.standard_tasks import (
    NERTask,
    DependencyParseTask,
    NaiveOpenRelationExtractionTask,
    PoSTaggingTask
)
from bwg.nlp.corenlp_server_tasks import (
    ServerNERTask,
    ServerDependencyParseTask,
    ServerPoSTaggingTask,
    ServerNaiveOpenRelationExtractionTask
)
from bwg.nlp.wikipedia_tasks import WikipediaReadingTask
from bwg.nlp.config_management import build_task_config_for_language


# ---------------------------- Default tasks for french ---------------------------------

class FrenchWikipediaReadingTask(WikipediaReadingTask):

    def _additional_formatting(self, line):
        french_sentence_tokenizer_path = self.task_config["SENTENCE_TOKENIZER_PATH"]
        download_nltk_resource_if_missing(french_sentence_tokenizer_path, "punkt")

        tokenizer = nltk.data.load(french_sentence_tokenizer_path)
        sentences = tokenizer.tokenize(line)
        return sentences


class FrenchNERTask(NERTask):
    """
    A luigi task tagging Named Entities in a sentence, but it's specific for the french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)


class FrenchPoSTaggingTask(PoSTaggingTask):
    """
    A luigi task tagging a sentence with PoS tags, but it's specific to the french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)


class FrenchDependencyParseTask(DependencyParseTask):
    """
    A luigi task dependency-parsing a sentence, but it's specific for the french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)


class FrenchNaiveOpenRelationExtractionTask(NaiveOpenRelationExtractionTask):
    """
    A luigi task performing a naive version of Open Relation Extraction on a sentence, but it's specific for the french
    Wikipedia.
    """
    def requires(self):
        return FrenchNERTask(task_config=self.task_config),\
               FrenchDependencyParseTask(task_config=self.task_config),\
               FrenchPoSTaggingTask(task_config=self.task_config)

# -------------------- Tasks for french using Stanford CoreNLP server --------------------


class FrenchServerNERTask(ServerNERTask):
    """
    A luigi task tagging Named Entities in a sentence using a Stanford CoreNLP server, but it's specific for the
    french Wikipedia.
    """
    # TODO (Feature): Implement
    pass


class FrenchServerPoSTaggingTask(ServerPoSTaggingTask):
    """
    A luigi task tagging a sentence with PoS tags using a Stanford CoreNLP server, but it's specific to the french
    Wikipedia.
    """
    # TODO (Feature): Implement
    pass


class FrenchServerDependencyTask(ServerDependencyParseTask):
    """
    A luigi task dependency-parsing a sentence using a Stanford CoreNLP server, but it's specific for the french
    Wikipedia.
    """
    # TODO (Feature): Implement
    pass


class FrenchServerNaiveOPenRelationExtractionTask(ServerNaiveOpenRelationExtractionTask):
    """
    A luigi task performing a naive version of Open Relation Extraction on a sentence using a Stanford CoreNLP server,
    but it's specific for the french Wikipedia.
    """
    # TODO (Feature): Implement
    pass


# --------------------------- Pipeline composition & starting ----------------------------

if __name__ == "__main__":
    # TODO (FEATURE): Use remote scheduler for server deployment
    french_task_config = build_task_config_for_language(
        tasks=[
            "wikipedia_reading",
            "named_entity_recognition",
            "pos_tagging",
            "dependency_parsing",
            "open_relation_extraction"
        ],
        language="french",
        config_file_path="../../pipeline_config.py"
    )
    luigi.build(
        [FrenchNaiveOpenRelationExtractionTask(task_config=french_task_config)],
        local_scheduler=True, workers=2, log_level="INFO"
    )
