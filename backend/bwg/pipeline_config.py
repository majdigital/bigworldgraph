# -*- coding: utf-8 -*-
# WARNING: DO NOT USE SETS HERE!

# ---------------------------------- Meta config ----------------------------------------
# Finds out which parts of the config are necessary for a specific task
CONFIG_DEPENDENCIES = {
    # Obligatory config parameter
    "all": [
        "PIPELINE_DEBUG",  # Debug mode for Pipeline, will produce more terminal output
        "CORPUS_ENCODING",  # Encoding of corpus and interim .json files
        "STANFORD_CORENLP_SERVER_ADDRESS",  # Address of Stanford CoreNLP server
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
        "STANFORD_PATH"
    ],
    # Necessary config parameters for Named Entity Recognition
    "named_entity_recognition": [
        "{language}_STANFORD_MODELS_PATH",  # Path to language-specific Stanford NLP model files
        "{language}_STANFORD_NER_MODEL_PATH",  # Path to language-specific Stanford NER model file
        "{language}_NES_OUTPUT_PATH",  # Path to output file of this task
        "{language}_CORENLP_STANFORD_NER_MODEL_PATH"  # Path to language-specific CoreNLP Stanford NER model path
    ],
    # Necessary config parameters for Part-of-Speech tagging
    "pos_tagging": [
        "STANFORD_POSTAGGER_PATH",  # Path to Stanford PoS tagger
        "{language}_STANFORD_POS_MODEL_PATH",  # Path to language-specific Stanford PoS tagger model file
        "{language}_STANFORD_MODELS_PATH",  # Path to language-specific Stanford model file
        "{language}_POS_OUTPUT_PATH"  # Path to output file of this task
    ],
    # Necessary config parameters for Dependency Parsing
    "dependency_parsing": [
        "DEPENDENCY_TREE_KEEP_FIELDS",  # Fields of dependency tree that are relevant to the task
        "STANFORD_CORENLP_MODELS_PATH",  # Path to Stanford CoreNLP models file (jar)
        "{language}_STANFORD_DEPENDENCY_MODEL_PATH",  # Path to language-specific Stanford model file
        "{language}_DEPENDENCY_OUTPUT_PATH"  # Path to output file of this task
    ],
    # Necessary config parameters for Open Relation Extraction
    "open_relation_extraction": [
        "VERB_NODE_POS_TAGS",  # PoS tags indicating verbs
        "OMITTED_TOKENS_FOR_ALIGNMENT",  # Omitted tokens to align dependency parse with ne tagged sentence
        "NER_TAGSET",  # Named entity tag set without the default tag
        "{language}_ORE_OUTPUT_PATH"  # Path to output file of this task
    ],
    # Necessary config parameters for reading a Wikipedia corpus file
    "wikipedia_reading": [
        "{language}_SENTENCE_TOKENIZER_PATH",  # Path to language-specific sentence tokenizer
        "{language}_CORPUS_INPATH",  # Path to corpus file
        "{language}_WIKIPEDIA_ARTICLE_TAG_PATTERN",  # Regex to recognize the beginning of a new article
        "{language}_WIKIPEDIA_READING_OUTPUT_PATH"  # Path to output file of this task
    ],
    # Necessary config parameters for Participation Extraction
    "participation_extraction": [
        "{language}_PARTICIPATION_PHRASES",  # Language-specific phrases to indicate involvement in an article
        "{language}_PE_OUTPUT_PATH",  # Path to output file of this task
        "DEFAULT_NE_TAG"  # Default tag for words that aren't named entities
    ],
    # Necessary config parameters for merging relations from PE and ORE
    "relation_merging": [
        "{language}_RELATION_MERGING_OUTPUT_PATH"  # Path to output file of this task
    ],
    # Necessary config parameters for Property Completion via Wikidata
    "properties_completion": [
        "{language}_PC_OUTPUT_PATH",  # Path to output file of this task
        "{language}_RELEVANT_WIKIDATA_PROPERTIES",  # Relevant Wikidata properties for different kind of named entities
        "{language}_WIKIDATA_PROPERTIES_IMPLYING_RELATIONS"  # Create relations out of these Wikidata properties later
    ],
    # Necessary config parameters to generate general information about the current pipeline run
    "pipeline_run_info_generation": [
        "{language}_PIPELINE_RUN_INFO_OUTPUT_PATH"  # Path to output file of this task
    ],
    "relations_database_writing_task": [
        "NEO4J_USER",
        "NEO4J_PASSWORD",
        "{language}_DATABASE_CATEGORIES"  # Categories of nodes in the database with their level of detail as int
    ]
}
SUPPORTED_LANGUAGES = ["FRENCH"]

# --------------------------------- General config --------------------------------------
STANFORD_CORENLP_MODELS_PATH = "../data/stanford/models/stanford-corenlp-3.7.0-models.jar"
STANFORD_CORENLP_SERVER_ADDRESS = "http://localhost:9000"
STANFORD_POSTAGGER_PATH = "../data/stanford/models/stanford-postagger.jar"
DEPENDENCY_TREE_KEEP_FIELDS = ["address", "ctag", "deps", "word", "head", "rel"]
STANFORD_PATH = "../data/stanford/models/"
VERB_NODE_POS_TAGS = ["VPP", "V", "VINF", "VPR", "VS"]
NER_TAGSET = ["I-PERS", "B-PERS", "I-LOC", "B-LOC", "I-ORG", "B-ORG", "I-MISC", "B-MISC"]
DEFAULT_NE_TAG = "O"
PIPELINE_DEBUG = True
CORPUS_ENCODING = "utf-8"
OMITTED_TOKENS_FOR_ALIGNMENT = []
# OMITTED_TOKENS_FOR_ALIGNMENT = [",", ".", "-LRB-", "-RRB-"]
ONLY_INCLUDE_RELEVANT_SENTENCES = True
ONLY_INCLUDE_RELEVANT_ARTICLES = True

# ------------------------------ Database configurations --------------------------------

# Neo4j
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jj"

# ------------------------------- French configurations ---------------------------------

# Paths for Luigi task outputs
FRENCH_LUIGI_DATA_PATH = "../data/pipeline_french/"
FRENCH_CORPORA_PATH = "../data/corpora_french/"
FRENCH_NES_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_nes.json"
FRENCH_POS_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_pos.json"
FRENCH_DEPENDENCY_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_dependencies.json"
FRENCH_ORE_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_relations.json"
FRENCH_WIKIPEDIA_READING_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles.json"
FRENCH_PE_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_participations.json"
FRENCH_RELATION_MERGING_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_merged_relations.json"
FRENCH_PC_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_articles_properties.json"
FRENCH_PIPELINE_RUN_INFO_OUTPUT_PATH = FRENCH_LUIGI_DATA_PATH + "fr_info.json"
FRENCH_CORPUS_INPATH = FRENCH_CORPORA_PATH + "corpus_affairs_modern_french_in_france_sample.xml"

# Paths for french Stanford models
FRENCH_STANFORD_NER_MODEL_PATH = STANFORD_PATH + "ner-model-french.ser.gz"
FRENCH_CORENLP_STANFORD_NER_MODEL_PATH = "./" + "ner-model-french.ser.gz"
FRENCH_STANFORD_POS_MODEL_PATH = STANFORD_PATH + "french.tagger"
FRENCH_STANFORD_MODELS_PATH = STANFORD_PATH + "french.jar"
FRENCH_STANFORD_DEPENDENCY_MODEL_PATH = STANFORD_PATH + "UD_French.gz"

# Misc
FRENCH_PARTICIPATION_PHRASES = {
    "I-PER": "participé à",
    "I-LOC": "est la scène de",
    "I-ORG": "est impliqué dans",
    "I-MISC": "est lié à",
    "DATE": "était au moment de",
    "DEFAULT": "participé à"
}
FRENCH_LANGUAGE_ABBREVIATION = "fr"
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
FRENCH_WIKIDATA_PROPERTIES_IMPLYING_RELATIONS = {
    "P463": "Organization",
    "P108": "Company",
    "P102": "Party",
    "P1416": "Party",
    "P335": "Company"
}

FRENCH_DATABASE_CATEGORIES = {
    "Entity": 0,
    "Organization": 2,
    "Company": 3,
    "Party": 3,
    "Miscellaneous": 1,
    "Affair": 6,
    "Politician": 3,
    "Person": 2,
    "Businessperson": 3,
    "Media": 4,
    "Location": 1
}
