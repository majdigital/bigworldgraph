# -*- coding: utf-8 -*-
# WARNING: DO NOT USE SETS HERE!

# ---------------------------------- Meta config ----------------------------------------
# Finds out which parts of the config are necessary for a specific task
CONFIG_DEPENDENCIES = {
    "all": [
        "PIPELINE_DEBUG",
        "CORPUS_ENCODING",
        "STANFORD_CORENLP_SERVER_ADDRESS",
        "{language}_LANGUAGE_ABBREVIATION"
    ],
    "optional": [
        "ONLY_INCLUDE_RELEVANT_SENTENCES",
        "ONLY_INCLUDE_RELEVANT_ARTICLES"
    ],
    "exclude": [
        "DEPENDENCIES",
        "SUPPORTED_LANGUAGES"
        "{language}_LUIGI_DATA_PATH",
        "STANFORD_PATH"
    ],
    "named_entity_recognition": [
        "{language}_STANFORD_MODELS_PATH",
        "{language}_STANFORD_NER_MODEL_PATH",
        "{language}_NES_OUTPUT_PATH",
        "{language}_CORENLP_STANFORD_NER_MODEL_PATH",
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
    "wikipedia_reading": [
        "{language}_SENTENCE_TOKENIZER_PATH",
        "CORPUS_ENCODING",
        "{language}_CORPUS_INPATH",
        "{language}_WIKIPEDIA_ARTICLE_TAG_PATTERN",
        "{language}_WIKIPEDIA_READING_OUTPUT_PATH"
    ],
    "participation_extraction": [
        "{language}_PARTICIPATION_PHRASE",
        "{language}_PE_OUTPUT_PATH"
    ],
    "relation_merging": [
        "{language}_RELATION_MERGING_OUTPUT_PATH"
    ],
    "properties_completion": [
        "{language}_PC_OUTPUT_PATH",
        "{language}_LANGUAGE_ABBREVIATION",
        "{language}_FALLBACK_LANGUAGE_ABBREVIATION",
        "{language}_RELEVANT_WIKIDATA_PROPERTIES"
    ]
}
SUPPORTED_LANGUAGES = ["FRENCH"]

# --------------------------------- General config --------------------------------------
STANFORD_CORENLP_MODELS_PATH = "../../data/stanford/models/stanford-corenlp-3.7.0-models.jar"
STANFORD_CORENLP_SERVER_ADDRESS = "http://localhost:9000"
STANFORD_POSTAGGER_PATH = "../../data/stanford/models/stanford-postagger.jar"
DEPENDENCY_TREE_KEEP_FIELDS = ["address", "ctag", "deps", "word", "head", "rel"]
STANFORD_PATH = "../../data/stanford/models/"
VERB_NODE_POS_TAGS = ["VPP", "V", "VINF", "VPR", "VS"]
NER_TAGSET = ["I-PERS", "B-PERS", "I-LOC", "B-LOC", "I-ORG", "B-ORG", "I-MISC", "B-MISC"]
PIPELINE_DEBUG = True
CORPUS_ENCODING = "utf-8"
OMITTED_TOKENS_FOR_ALIGNMENT = []
# OMITTED_TOKENS_FOR_ALIGNMENT = [",", ".", "-LRB-", "-RRB-"]
ONLY_INCLUDE_RELEVANT_SENTENCES = True
ONLY_INCLUDE_RELEVANT_ARTICLES = True

# ------------------------------- French configurations ---------------------------------

# Paths for Luigi task outputs
FRENCH_LUIGI_DATA_PATH = "../../data/pipeline_french/"
FRENCH_CORPORA_PATH = "../../data/corpora_french/"
FRENCH_NES_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_nes.json"
FRENCH_POS_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_pos.json"
FRENCH_DEPENDENCY_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_dependencies.json"
FRENCH_ORE_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_relations.json"
FRENCH_WIKIPEDIA_READING_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles.json"
FRENCH_PE_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_participations.json"
FRENCH_RELATION_MERGING_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_merged_relations.json"
FRENCH_PC_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_properties.json"
FRENCH_CORPUS_INPATH = FRENCH_CORPORA_PATH + "corpus_affairs_french_sample.xml"

# Paths for french Stanford models
FRENCH_STANFORD_NER_MODEL_PATH = STANFORD_PATH + "ner-model-french.ser.gz"
FRENCH_CORENLP_STANFORD_NER_MODEL_PATH = "./" + "ner-model-french.ser.gz"
FRENCH_STANFORD_POS_MODEL_PATH = STANFORD_PATH + "french.tagger"
FRENCH_STANFORD_MODELS_PATH = STANFORD_PATH + "french.jar"
FRENCH_STANFORD_DEPENDENCY_MODEL_PATH = STANFORD_PATH + "UD_French.gz"

# Misc
FRENCH_PARTICIPATION_PHRASE = "participé à"
FRENCH_LANGUAGE_ABBREVIATION = "fr"
FRENCH_FALLBACK_LANGUAGE_ABBREVIATION = "en"
FRENCH_SENTENCE_TOKENIZER_PATH = "tokenizers/punkt/PY3/french.pickle"
FRENCH_WIKIPEDIA_ARTICLE_TAG_PATTERN = '<doc id="(\d+)" url="(.+?)" title="(.+?)">'
FRENCH_WIKIPEDIA_REFERENCE_PATTERN = "[a-zA-Z-'áéíúóàèìùòâêîôûäëïöüçÇÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÄËÏÖÜ]+\d+((,\d+)+)?"
FRENCH_RELEVANT_WIKIDATA_PROPERTIES = {
    "I-PER": [
        "P21",    # Sex or gender
        "P463",   # Member of
        "P106",   # Occupation
        "P108",   # Employer
        "P39",    # Position held
        "P102",   # Member of political party
        "P1416"   # Affiliation
    ],
    "I-LOC": [
        "P30",    # Continent
        "P17"     # Country
    ],
    "I-ORG": [
        "P1384",  # Political alignment
        "P335",   # Subsidiary
        "P159"    # Headquarters location
    ],
    "I-MISC": []
}
