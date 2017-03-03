# ---------------------------------- Meta config ----------------------------------------
# Finds out which parts of the config are necessary for a specific task
# Possible tasks (so far) are:
#   - corpus_reading
#   - named_entity_recognition
#   - dependency_parsing
#   - open_relation_extraction
CONFIG_DEPENDENCIES = {
    "all": [
        "PIPELINE_DEBUG"
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
    "id_tagging": [
        "{language}_ID_TAGGING_OUTPUT_PATH"
    ],
    "named_entity_recognition": [
        "{language}_STANFORD_MODELS_PATH",
        "{language}_STANFORD_NER_MODEL_PATH",
        "{language}_NES_OUTPUT_PATH"
    ],
    "dependency_parsing": [
        "DEPENDENCY_TREE_KEEP_FIELDS",
        "STANFORD_CORENLP_MODELS_PATH",
        "{language}_STANFORD_DEPENDENCY_MODEL_PATH",
        "{language}_DEPENDENCY_OUTPUT_PATH"
    ],
    "open_relation_extraction": [
        "MODERATING_NODE_CTAGS",
        "NER_TAGSET",
        "{language}_ORE_OUTPUT_PATH"
    ],
    "wikipedia_corpus_cleaning": [
        "CORPUS_ENCODING",
        "{language}_WIKIPEDIA_CLEANING_OUTPUT_PATH",
        "{language}_WIKIPEDIA_CLEANING_INPUT_PATH"
    ],
    "wikipedia_sentence_splitting": [
        "{language}_WIKIPEDIA_SPLITTING_OUTPUT_PATH"
    ]
}
SUPPORTED_LANGUAGES = ["FRENCH"]

# --------------------------------- General config --------------------------------------
STANFORD_CORENLP_MODELS_PATH = "../../data/stanford/models/stanford-corenlp-3.7.0-models.jar"
PRETTY_SERIALIZATION = False
DEPENDENCY_TREE_KEEP_FIELDS = ["address", "ctag", "deps", "word", "head", "rel"]
STANFORD_PATH = "../../data/stanford/models/"
MODERATING_NODE_CTAGS = ["VBP", "VBZ"]
NER_TAGSET = ["I-PERS", "B-PERS", "I-LOC", "B-LOC", "I-ORG", "B-ORG", "I-MISC", "B-MISC"]
PIPELINE_DEBUG = True
CORPUS_ENCODING = "latin-1"

# ------------------------------- French configurations ---------------------------------
# Luigi task dependencies
# This would be cool if it worked but it doesn't due to weird Luigi scheduler problems.
# TODO: Ask this on Stack overflow? / Luigi Github?
#FRENCH_PIPELINE_DEPENDENCIES = {
#    "ReadCorpusTask": [],
#    "NERTask": ["ReadCorpusTask"],
#    "DependencyParseTask": ["ReadCorpusTask"],
#    "NaiveOpenRelationExtractionTask": ["NERTask", "DependencyParseTask"]
#}

# Paths for Luigi task outputs
FRENCH_LUIGI_DATA_PATH = "../../data/pipeline_french/"
FRENCH_NES_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "nes_fr.txt"
FRENCH_DEPENDENCY_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "dependencies_fr.txt"
FRENCH_ORE_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "relations_fr.txt"
FRENCH_WIKIPEDIA_CLEANING_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "wikipedia_cleaned_fr.txt"
FRENCH_WIKIPEDIA_CLEANING_INPUT_PATH = FRENCH_LUIGI_DATA_PATH + "corpus_french.txt"
FRENCH_WIKIPEDIA_SPLITTING_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "wikipedia_split_fr.txt"
FRENCH_ID_TAGGING_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "id_tagged_fr.txt"

# Paths for french Stanford models
FRENCH_STANFORD_NER_MODEL_PATH = STANFORD_PATH + "ner-model-french.ser.gz"
FRENCH_STANFORD_MODELS_PATH = STANFORD_PATH + "french.jar"
FRENCH_STANFORD_DEPENDENCY_MODEL_PATH = STANFORD_PATH + "UD_French.gz"
