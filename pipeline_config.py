# -*- coding: utf-8 -*-

# ---------------------------------- Meta config ----------------------------------------
# Finds out which parts of the config are necessary for a specific task
CONFIG_DEPENDENCIES = {
    "all": [
        "PIPELINE_DEBUG",
        "CORPUS_ENCODING"
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
    "pos_tagging": [
        "STANFORD_POSTAGGER_PATH",
        "{language}_STANFORD_POS_MODEL_PATH",
        "{language}_STANFORD_MODELS_PATH",
        "{language}_POS_OUTPUT_PATH"
    ],
    "dependency_parsing": [
        "DEPENDENCY_TREE_KEEP_FIELDS",
        "STANFORD_CORENLP_MODELS_PATH",
        "{language}_STANFORD_DEPENDENCY_MODEL_PATH",
        "{language}_DEPENDENCY_OUTPUT_PATH"
    ],
    "open_relation_extraction": [
        "VERB_NODE_POS_TAGS",
        "OMITTED_TOKENS_FOR_ALIGNMENT",
        "NER_TAGSET",
        "{language}_ORE_OUTPUT_PATH"
    ],
    "wikipedia_corpus_cleaning": [
        "CORPUS_ENCODING",
        "{language}_WIKIPEDIA_CLEANING_OUTPUT_PATH",
        "{language}_WIKIPEDIA_CLEANING_INPUT_PATH",
        "{language}_WIKIPEDIA_REFERENCE_PATTERN"
    ],
    "wikipedia_sentence_splitting": [
        "{language}_WIKIPEDIA_SPLITTING_OUTPUT_PATH"
    ],
    "wikipedia_reading": [
        "CORPUS_ENCODING",
        "{language}_CORPUS_INPATH",
        "{language}_WIKIPEDIA_ARTICLE_TAG_PATTERN",
        "{language}_WIKIPEDIA_READING_OUTPUT_PATH"
    ]
}
SUPPORTED_LANGUAGES = ["FRENCH"]

# --------------------------------- General config --------------------------------------
STANFORD_CORENLP_MODELS_PATH = "../../data/stanford/models/stanford-corenlp-3.7.0-models.jar"
STANFORD_POSTAGGER_PATH = "../../data/stanford/models/stanford-postagger.jar"
PRETTY_SERIALIZATION = False
DEPENDENCY_TREE_KEEP_FIELDS = ["address", "ctag", "deps", "word", "head", "rel"]
STANFORD_PATH = "../../data/stanford/models/"
VERB_NODE_POS_TAGS = ["VPP", "V", "VINF", "VPR", "VS"]
NER_TAGSET = ["I-PERS", "B-PERS", "I-LOC", "B-LOC", "I-ORG", "B-ORG", "I-MISC", "B-MISC"]
PIPELINE_DEBUG = True
CORPUS_ENCODING = "utf-8"
OMITTED_TOKENS_FOR_ALIGNMENT = [",", ".", "-LRB-", "-RRB-"]

# ------------------------------- French configurations ---------------------------------

# Paths for Luigi task outputs
FRENCH_LUIGI_DATA_PATH = "../../data/pipeline_french/"
FRENCH_CORPORA_PATH = "../../data/corpora_french/"
FRENCH_NES_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_nes.json"
FRENCH_POS_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_pos.json"
FRENCH_DEPENDENCY_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_dependencies.json"
FRENCH_ORE_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_relations.txt"
FRENCH_WIKIPEDIA_CLEANING_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "wikipedia_cleaned_fr.txt"
FRENCH_WIKIPEDIA_CLEANING_INPUT_PATH = FRENCH_LUIGI_DATA_PATH + "corpus_100_fr.txt"
FRENCH_WIKIPEDIA_SPLITTING_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "wikipedia_split_fr.txt"
FRENCH_ID_TAGGING_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "id_tagged_fr.txt"
FRENCH_WIKIPEDIA_READING_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles.json"
FRENCH_CORPUS_INPATH = FRENCH_CORPORA_PATH + "corpus_affairs_french_sample.xml"

# Paths for french Stanford models
FRENCH_STANFORD_NER_MODEL_PATH = STANFORD_PATH + "ner-model-french.ser.gz"
FRENCH_STANFORD_POS_MODEL_PATH = STANFORD_PATH + "french.tagger"
FRENCH_STANFORD_MODELS_PATH = STANFORD_PATH + "french.jar"
FRENCH_STANFORD_DEPENDENCY_MODEL_PATH = STANFORD_PATH + "UD_French.gz"

# Misc
FRENCH_WIKIPEDIA_ARTICLE_TAG_PATTERN = '<doc id="(\d+)" url="(.+?)" title="(.+?)">'
FRENCH_WIKIPEDIA_REFERENCE_PATTERN = "[a-zA-Z-'áéíúóàèìùòâêîôûäëïöüçÇÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÄËÏÖÜ]+\d+((,\d+)+)?"
