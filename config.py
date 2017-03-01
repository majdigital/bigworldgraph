# ---------------------------------- Meta config ----------------------------------------
# Finds out which parts of the config are necessary for a specific task
# Possible tasks (so far) are:
#   - corpus_reading
#   - named_entity_recognition
#   - dependency_parsing
#   - open_relation_extraction
CONFIG_DEPENDENCIES = {
    "all": [
    ],
    "optional": [
        "PRETTY_SERIALIZATION"
    ],
    "exclude": [
        "DEPENDENCIES",
        "SUPPORTED_LANGUAGES"
        "{language}_LUIGI_DATA_PATH",
        "STANFORD_PATH"
    ],
    "corpus_reading": [
        "{language}_CORPUS_FILE_PATH",
        "{language}_SENTENCES_FILE_PATH"
    ],
    "named_entity_recognition": [
        "{language}_STANFORD_MODELS_PATH",
        "{language}_STANFORD_NER_MODEL_PATH",
        "{language}_SENTENCES_FILE_PATH",
        "{language}_NES_FILE_PATH"
    ],
    "dependency_parsing": [
        "DEPENDENCY_TREE_KEEP_FIELDS",
        "STANFORD_CORENLP_MODELS_PATH",
        "{language}_SENTENCES_FILE_PATH",
        "{language}_DEPENDENCY_FILE_PATH",
        "{language}_STANFORD_DEPENDENCY_MODEL_PATH"
    ],
    "open_relation_extraction": [
        "{language}_DEPENDENCY_FILE_PATH",
        "{language}_NES_FILE_PATH",
        "{language}_RELATIONS_FILE_PATH"
    ]
}
SUPPORTED_LANGUAGES = [
    "FRENCH"
]

# --------------------------------- General config --------------------------------------
STANFORD_CORENLP_MODELS_PATH = "../../data/stanford/models/stanford-corenlp-3.7.0-models.jar"
PRETTY_SERIALIZATION = False
DEPENDENCY_TREE_KEEP_FIELDS = [
    "address", "ctag", "deps", "word", "head", "rel"
]
STANFORD_PATH = "../../data/stanford/models/"

# ------------------------------- French configurations ---------------------------------
# Paths for Luigi task outputs
FRENCH_LUIGI_DATA_PATH = "../../data/pipeline_french/"
FRENCH_CORPUS_FILE_PATH = FRENCH_LUIGI_DATA_PATH + "corpus_fr.txt"
FRENCH_SENTENCES_FILE_PATH = FRENCH_LUIGI_DATA_PATH + "sentences_fr.txt"
FRENCH_NES_FILE_PATH = FRENCH_LUIGI_DATA_PATH + "nes_fr.txt"
FRENCH_DEPENDENCY_FILE_PATH = FRENCH_LUIGI_DATA_PATH + "dependency_fr.txt"
FRENCH_RELATIONS_FILE_PATH = FRENCH_LUIGI_DATA_PATH + "relations_fr.txt"

# Paths for french Stanford models
FRENCH_STANFORD_NER_MODEL_PATH = STANFORD_PATH + "ner-model-french.ser.gz"
FRENCH_STANFORD_MODELS_PATH = STANFORD_PATH + "french.jar"
FRENCH_STANFORD_DEPENDENCY_MODEL_PATH = STANFORD_PATH + "UD_French.gz"
