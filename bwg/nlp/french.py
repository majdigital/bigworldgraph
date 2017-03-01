# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

# EXT
import luigi

# PROJECT
from bwg.nlp.standard_tasks import OpenRelationExtractionTask
from bwg.nlp.utilities import build_task_config_for_language

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
        config_file_path="../../config.py"
    )
    pass
    luigi.build([OpenRelationExtractionTask(task_config=french_task_config)], local_scheduler=True)
    # luigi.run(["OpenRelationExtractionTask"])
