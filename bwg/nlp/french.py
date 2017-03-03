# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

# EXT
import luigi

# PROJECT
from bwg.nlp.standard_tasks import (
    ReadCorpusTask,
    NERTask,
    DependencyParseTask,
    NaiveOpenRelationExtractionTask
)
from bwg.nlp.config_management import build_task_config_for_language


class FrenchWikipediaCorpusCleaningTask(luigi.task):
    """
    A Luigi task that cleans the corpus of certain Wikipedia artifacts, like
        * Deleting references from words ("décolé21" -> "décolé" / "Kwan3,4" -> "Kwan")
        * Deleting leftover Wikipedia markup, like "[masquer]"
        * Joining shortened articles with their nouns ("L enquête" -> "L'enquête")
    """
    task_config = luigi.DictParameter()
    # TODO: Delete references from words
    # TODO: Delete wikipedia markup
    # TODO: Join L-articles with words

    def output(self):
        pass

    def run(self):
        pass


class FrenchWikipediaSentenceSplittingTask(luigi.task):
    """
    A Luigi task that splits sentences in the Wikipedia corpus and removes useless, empty lines.
    """
    task_config = luigi.DictParameter()
    # TODO: Remove empty lines
    # TODO: Split sentences

    def requires(self):
        return FrenchWikipediaCorpusCleaningTask(task_config=self.task_config)

    def output(self):
        pass

    def run(self):
        pass


class FrenchReadCorpusTask(ReadCorpusTask):
    """
    A luigi task reading a corpus, but it's specific for the french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaSentenceSplittingTask(task_config=self.task_config)


class FrenchNERTask(NERTask):
    """
    A luigi task tagging Named Entities in a sentence, but it's specific for the french Wikipedia.
    """
    def requires(self):
        return FrenchReadCorpusTask(task_config=self.task_config)


class FrenchDependencyParseTask(DependencyParseTask):
    """
    A luigi task dependency-parsing a sentence, but it's specific for the french Wikipedia.
    """
    def requires(self):
        return FrenchReadCorpusTask(task_config=self.task_config)


class FrenchNaiveOpenRelationExtractionTask(NaiveOpenRelationExtractionTask):
    """
    A luigi task performing a naive version of Open Relation Extraciton on a sentence, but it's specific for the french
    Wikipedia.
    """
    def requires(self):
        return FrenchNERTask(task_config=self.task_config), FrenchDependencyParseTask(task_config=self.task_config)


if __name__ == "__main__":
    # TODO: Use remote scheduler for server deployment
    french_task_config = build_task_config_for_language(
        tasks=[
            "corpus_reading",
            "named_entity_recognition",
            "dependency_parsing",
            "open_relation_extraction"
        ],
        language="french",
        config_file_path="../../pipeline_config.py"
    )
    luigi.build(
        [FrenchNaiveOpenRelationExtractionTask(task_config=french_task_config)],
        local_scheduler=True,
        no_lock=True
    )
    # luigi.run(["OpenRelationExtractionTask"])
