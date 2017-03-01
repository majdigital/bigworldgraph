# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

# EXT
import luigi

# PROJECT
from config import (
    FRENCH_CORPUS_FILE_PATH,
    FRENCH_DEPENDENCY_FILE_PATH,
    FRENCH_NES_FILE_PATH,
    FRENCH_RELATIONS_FILE_PATH,
    FRENCH_SENTENCES_FILE_PATH,
    FRENCH_STANFORD_MODELS_PATH,
    FRENCH_STANFORD_NER_MODEL_PATH,
    STANFORD_CORENLP_MODELS_PATH,
    FRENCH_STANFORD_DEPENDENCY_MODEL_PATH,
    PRETTY_SERIALIZATION
)
from bwg.nlp.standard_tasks import OpenRelationExtractionTask

# CONST
FRENCH_TASK_CONFIG = {
    "corpus_file_path": FRENCH_CORPUS_FILE_PATH,
    "dependency_file_path": FRENCH_DEPENDENCY_FILE_PATH,
    "nes_file_path": FRENCH_NES_FILE_PATH,
    "relations_file_path": FRENCH_RELATIONS_FILE_PATH,
    "sentences_file_path": FRENCH_SENTENCES_FILE_PATH,
    "stanford_models_path": FRENCH_STANFORD_MODELS_PATH,
    "stanford_ner_model_path": FRENCH_STANFORD_NER_MODEL_PATH,
    "stanford_dependency_model_path": FRENCH_STANFORD_DEPENDENCY_MODEL_PATH,
    "stanford_corenlp_models_path": STANFORD_CORENLP_MODELS_PATH,
    "pretty_serialization": PRETTY_SERIALIZATION
}

if __name__ == "__main__":
    # _anti_pipeline()
    # TODO: Use remote scheduler for server deployment
    luigi.build([OpenRelationExtractionTask(task_config=FRENCH_TASK_CONFIG)], local_scheduler=True)
    # luigi.run(["OpenRelationExtractionTask"])
