# -*- coding: utf-8 -*-
# WARNING: DO NOT USE SETS HERE!

SUPPORTED_LANGUAGES = ["DEMO"]

# --------------------------------- General config --------------------------------------
PIPELINE_DEBUG = True

ONLY_INCLUDE_RELEVANT_SENTENCES = True
ONLY_INCLUDE_RELEVANT_ARTICLES = True

# ---------------------------------- Demo config -----------------------------------------

DEMO_WIKIPEDIA_ARTICLE_TAG_PATTERN = '<doc id="(\d+)" url="(.+?)" title="(.+?)">'
DEMO_LANGUAGE_ABBREVIATION = "dm"
CORPUS_ENCODING = "utf-8"
DEMO_LUIGI_DATA_PATH = "../data/pipeline_demo/"
DEMO_CORPORA_PATH = "../data/corpora_demo/"
DEMO_CORPUS_INPATH = DEMO_CORPORA_PATH + "demo_corpus.xml"
DEMO_SIMPLE_READING_OUTPUT_PATH = DEMO_LUIGI_DATA_PATH + "demo_corpus_read.json"
DEMO_REPLACED_CORPUS_OUTPUT_PATH = DEMO_LUIGI_DATA_PATH + "demo_corpus_replaced.json"
DEMO_DUPLICATED_CORPUS_OUTPUT_PATH = DEMO_LUIGI_DATA_PATH + "demo_corpus_duplicated.json"
DEMO_REMOVED_CORPUS_OUTPUT_PATH = DEMO_LUIGI_DATA_PATH + "demo_corpus_removed.json"

REPLACE_CHARACTERS = ["a", "m"]
DUPLICATE_CHARACTERS = ["b", "o", "n", "k"]
REMOVE_CHARACTERS = ["l", "r", "p"]

# ---------------------------------- Meta config ----------------------------------------
# Finds out which parts of the config are necessary for a specific task
TASK_PARAMETERS = {
    # Obligatory config parameter
    "all": [
        "PIPELINE_DEBUG",  # Debug mode for Pipeline, will produce more terminal output
        "{language}_LANGUAGE_ABBREVIATION",  # Abbreviation of pipeline language, e.g. "en"
        "CORPUS_ENCODING"
    ],
    # Optional config parameter
    "optional": [
        "ONLY_INCLUDE_RELEVANT_SENTENCES",  # Flag to only include relevant sentences in task results
        "ONLY_INCLUDE_RELEVANT_ARTICLES"  # Flag to only include relevant articles in task results
    ],
    # Exclude the following parameters from the target config
    "exclude": [
        "CONFIG_DEPENDENCIES",
        "SUPPORTED_LANGUAGES",
        "{language}_LUIGI_DATA_PATH",
    ],
    "demo_task1": [
        "REPLACE_CHARACTERS",
        "{language}_CORPUS_INPATH",
        "{language}_REPLACED_CORPUS_OUTPUT_PATH"
    ],
    "demo_task2": [
        "DUPLICATE_CHARACTERS",
        "{language}_DUPLICATED_CORPUS_OUTPUT_PATH"
    ],
    "demo_task3": [
        "REMOVE_CHARACTERS",
        "{language}_REMOVED_CORPUS_OUTPUT_PATH"
    ],
    "simple_reading": [
        "{language}_WIKIPEDIA_ARTICLE_TAG_PATTERN",
        "CORPUS_ENCODING",
        "{language}_SIMPLE_READING_OUTPUT_PATH",
        "{language}_CORPUS_INPATH"
    ]
}
