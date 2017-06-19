# -*- coding: utf-8 -*-
# WARNING: DO NOT USE SETS HERE!

# ---------------------------------- Meta config ----------------------------------------
# Finds out which parts of the config are necessary for a specific task
CONFIG_DEPENDENCIES = {
    # Obligatory config parameter
    "all": [
        "PIPELINE_DEBUG",  # Debug mode for Pipeline, will produce more terminal output
        "{language}_LANGUAGE_ABBREVIATION"  # Abbreviation of pipeline language, e.g. "en"
    ],
    # Optional config parameter
    "optional": [
        "OPTIONAL_PARAMETER"
    ],
    # Exclude the following parameters from the target config
    "exclude": [
        "CONFIG_DEPENDENCIES",
        "SUPPORTED_LANGUAGES",
    ],
    "task1": [
        "PARAM1"
    ],
    "task2": [
        "PARAM2",
        "{language}_PARAM"
    ],
    "task3": [
        "PARAM3"
    ]
}
SUPPORTED_LANGUAGES = ["DEMO"]

# --------------------------------- General config --------------------------------------
PARAM1 = "abc"
PARAM2 = 12
PARAM3 = True
DEMO_PARAM = 3.5
REDUNDANT_PARAM = "yada yada"
PIPELINE_DEBUG = True
DEMO_LANGUAGE_ABBREVIATION = "demo"
OPTIONAL_PARAMETER = "I am optional"

