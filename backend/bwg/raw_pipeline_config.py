# -*- coding: utf-8 -*-
# WARNING: DO NOT USE SETS HERE!

# --------------------------------- General config --------------------------------------
PIPELINE_DEBUG = True
ONLY_INCLUDE_RELEVANT_SENTENCES = True
ONLY_INCLUDE_RELEVANT_ARTICLES = True

# ---------------------------------- Meta config ----------------------------------------
# Finds out which parts of the config are necessary for a specific task
TASK_PARAMETERS = {
    # Obligatory config parameter
    "all": [
        "PIPELINE_DEBUG",  # Debug mode for Pipeline, will produce more terminal output
        "{language}_LANGUAGE_ABBREVIATION"  # Abbreviation of pipeline language, e.g. "en"
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
    ]
}
SUPPORTED_LANGUAGES = ["DEMO"]
