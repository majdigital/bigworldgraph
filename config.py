# General config
STANFORD_CORENLP_MODELS_PATH = "../../data/stanford/models/stanford-corenlp-3.7.0-models.jar"
PRETTY_SERIALIZATION = False

# ------------------------------- French configurations ---------------------------------
# Paths for Luigi task outputs
FRENCH_LUIGI_DATA_PATH = "../../data/pipeline_french/"
FRENCH_CORPUS_FILE_PATH = FRENCH_LUIGI_DATA_PATH + "corpus_fr.txt"
FRENCH_SENTENCES_FILE_PATH = FRENCH_LUIGI_DATA_PATH + "sentences_fr.txt"
FRENCH_NES_FILE_PATH = FRENCH_LUIGI_DATA_PATH + "nes_fr.txt"
FRENCH_DEPENDENCY_FILE_PATH = FRENCH_LUIGI_DATA_PATH + "dependency_fr.txt"
FRENCH_RELATIONS_FILE_PATH = FRENCH_LUIGI_DATA_PATH + "relations_fr.txt"

# Paths for french Stanford models
FRENCH_STANFORD_NER_MODEL_PATH = "../../data/stanford/models//ner-model-french.ser.gz"
FRENCH_STANFORD_MODELS_PATH = "../../data/stanford/models/french.jar"
FRENCH_STANFORD_DEPENDENCY_MODEL_PATH = "../../data/stanford/models/UD_French.gz"
