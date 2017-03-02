# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

# EXT
import luigi

# PROJECT
from bwg.nlp.standard_tasks import NaiveOpenRelationExtractionTask
from bwg.nlp.config_management import build_task_config_for_language


#class FrenchWikipediaCorpusCleaningTask(luigi.task):
#    pass


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
    pass
    luigi.build(
        [NaiveOpenRelationExtractionTask(task_config=french_task_config)],
        local_scheduler=True,
        no_lock=True
    )
    # luigi.run(["OpenRelationExtractionTask"])
