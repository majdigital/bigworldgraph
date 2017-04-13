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
    PoSTaggingTask,
    ParticipationExtractionTask
)
from bwg.nlp.additional_tasks import RelationMergingTask
from bwg.nlp.corenlp_server_tasks import (
    ServerNERTask,
    ServerDependencyParseTask,
    ServerPoSTaggingTask,
    ServerNaiveOpenRelationExtractionTask
)
from bwg.nlp.wikipedia_tasks import WikipediaReadingTask, PropertiesCompletionTask
from bwg.nlp.config_management import build_task_config_for_language


# ---------------------------- Default tasks for french ---------------------------------
# TODO (Refactor): Could this be simplified with a Meta-programming approach?

class FrenchWikipediaReadingTask(WikipediaReadingTask):
    """
    A luigi task for reading a Wikipedia corpus, but sentences are split in a way that's appropriate for french.
    """
    def _additional_formatting(self, line):
        french_sentence_tokenizer_path = self.task_config["SENTENCE_TOKENIZER_PATH"]
        download_nltk_resource_if_missing(french_sentence_tokenizer_path, "punkt")

        tokenizer = nltk.data.load(french_sentence_tokenizer_path)
        sentences = tokenizer.tokenize(line)
        return sentences


class FrenchNERTask(NERTask):
    """
    A luigi task tagging Named Entities in a sentence, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)


class FrenchPoSTaggingTask(PoSTaggingTask):
    """
    A luigi task tagging a sentence with PoS tags, but it's specifically to the french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)


class FrenchDependencyParseTask(DependencyParseTask):
    """
    A luigi task dependency-parsing a sentence, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)


class FrenchNaiveOpenRelationExtractionTask(NaiveOpenRelationExtractionTask):
    """
    A luigi task performing a naive version of Open Relation Extraction on a sentence, but it's specifically for the french
    Wikipedia.
    """
    def requires(self):
        return FrenchNERTask(task_config=self.task_config),\
               FrenchDependencyParseTask(task_config=self.task_config),\
               FrenchPoSTaggingTask(task_config=self.task_config)


class FrenchParticipationExtractionTask(ParticipationExtractionTask):
    """
    A luigi Task performing participation extraction, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchNERTask(task_config=self.task_config)


class FrenchRelationMergingTask(RelationMergingTask):
    """
    A luigi Task that merges extracted relations from other tasks, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchParticipationExtractionTask(task_config=self.task_config),\
               FrenchNaiveOpenRelationExtractionTask(task_config=self.task_config)


class FrenchPropertiesCompletionTask(PropertiesCompletionTask):
    """
    A luigi Task that  adds attributes from Wikidata to Named Entities, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchNERTask(task_config=self.task_config)


# -------------------- Tasks for french using Stanford CoreNLP server --------------------

class FrenchServerNERTask(ServerNERTask):
    """
    A luigi task tagging Named Entities in a sentence using a Stanford CoreNLP server, but it's specifically for the
    french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)

    @property
    def _corenlp_server_overriding_properties(self):
        return {
            "ner.model": self.task_config["CORENLP_STANFORD_NER_MODEL_PATH"],
            "pos.model": "edu/stanford/nlp/models/pos-tagger/french/french.tagger"
        }


class FrenchServerPoSTaggingTask(ServerPoSTaggingTask):
    """
    A luigi task tagging a sentence with PoS tags using a Stanford CoreNLP server, but it's specifically to the french
    Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)

    @property
    def _corenlp_server_overriding_properties(self):
        return {"pos.model": "edu/stanford/nlp/models/pos-tagger/french/french.tagger"}


class FrenchServerDependencyParseTask(ServerDependencyParseTask):
    """
    A luigi task dependency-parsing a sentence using a Stanford CoreNLP server, but it's specifically for the french
    Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)

    @property
    def _corenlp_server_overriding_properties(self):
        return {
            "parse.model": "edu/stanford/nlp/models/lexparser/frenchFactored.ser.gz",
            "pos.model": "edu/stanford/nlp/models/pos-tagger/french/french.tagger"
        }


class FrenchServerNaiveOpenRelationExtractionTask(ServerNaiveOpenRelationExtractionTask):
    """
    A luigi task performing a naive version of Open Relation Extraction on a sentence using a Stanford CoreNLP server,
    but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchServerNERTask(task_config=self.task_config),\
               FrenchServerDependencyParseTask(task_config=self.task_config),\
               FrenchServerPoSTaggingTask(task_config=self.task_config)


class FrenchServerParticipationExtractionTask(FrenchParticipationExtractionTask):
    """
    A luigi Task performing participation extraction, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchServerNERTask(task_config=self.task_config)


class FrenchServerRelationMergingTask(RelationMergingTask):
    """
    A luigi Task that merges extracted relations from other tasks, but it's specifically for the french Wikipedia.
    """

    def requires(self):
        return FrenchServerParticipationExtractionTask(task_config=self.task_config), \
               FrenchServerNaiveOpenRelationExtractionTask(task_config=self.task_config)


class FrenchServerPropertiesCompletionTask(FrenchPropertiesCompletionTask):
    """
    A luigi Task that  adds attributes from Wikidata to Named Entities, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchServerNERTask(task_config=self.task_config)


# --------------------------- Pipeline composition & starting ----------------------------

if __name__ == "__main__":
    # TODO (FEATURE): Use remote scheduler for server deployment
    french_task_config = build_task_config_for_language(
        tasks=[
            "wikipedia_reading",
            "named_entity_recognition",
            "pos_tagging",
            "dependency_parsing",
            "open_relation_extraction",
            "participation_extraction",
            "relation_merging",
            "properties_completion"
        ],
        language="french",
        config_file_path="../../pipeline_config.py"
    )

    import cProfile
    cProfile.run(
    """luigi.build(
        [FrenchServerPropertiesCompletionTask(task_config=french_task_config)],
        local_scheduler=True, workers=1, log_level="INFO"
    )""", sort=True
    )
