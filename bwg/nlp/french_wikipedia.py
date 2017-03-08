# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

import luigi.format

# PROJECT
from bwg.nlp.standard_tasks import (
    NERTask,
    DependencyParseTask,
    NaiveOpenRelationExtractionTask,
    PoSTaggingTask
)
from bwg.nlp.wikipedia_tasks import WikipediaReadingTask
from bwg.nlp.config_management import build_task_config_for_language


class FrenchNERTask(NERTask):
    """
    A luigi task tagging Named Entities in a sentence, but it's specific for the french Wikipedia.
    """
    def requires(self):
        return WikipediaReadingTask(task_config=self.task_config)


class FrenchPoSTaggingTask(PoSTaggingTask):
    """
    A luigi task tagging a sentence with PoS tags, but it's tailored to the french Wikipedia.
    """
    def requires(self):
        return WikipediaReadingTask(task_config=self.task_config)


class FrenchDependencyParseTask(DependencyParseTask):
    """
    A luigi task dependency-parsing a sentence, but it's specific for the french Wikipedia.
    """
    def requires(self):
        return WikipediaReadingTask(task_config=self.task_config)


class FrenchNaiveOpenRelationExtractionTask(NaiveOpenRelationExtractionTask):
    """
    A luigi task performing a naive version of Open Relation Extraction on a sentence, but it's specific for the french
    Wikipedia.
    """
    def requires(self):
        return FrenchNERTask(task_config=self.task_config),\
               FrenchDependencyParseTask(task_config=self.task_config),\
               FrenchPoSTaggingTask(task_config=self.task_config)


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
        local_scheduler=True, workers=1
    )
