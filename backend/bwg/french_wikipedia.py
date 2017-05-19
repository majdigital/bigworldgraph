# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

# EXT
import luigi.format
import nltk

# PROJECT
from bwg.standard_tasks import (
    NERTask,
    DependencyParseTask,
    NaiveOpenRelationExtractionTask,
    PoSTaggingTask,
    ParticipationExtractionTask
)
from bwg.additional_tasks import RelationMergingTask, PipelineRunInfoGenerationTask, RelationsDatabaseWritingTask
from bwg.corenlp_server_tasks import (
    ServerNERTask,
    ServerDependencyParseTask,
    ServerPoSTaggingTask,
    ServerNaiveOpenRelationExtractionTask
)
from bwg.wikipedia_tasks import WikipediaReadingTask, PropertiesCompletionTask
from bwg.config_management import build_task_config_for_language
from bwg.helpers import download_nltk_resource_if_missing, get_if_exists


# ---------------------------- Default tasks for french ---------------------------------
# TODO (Refactor): Could this be simplified with a Meta-programming approach? [DU 18.04.17]

class FrenchWikipediaReadingTask(WikipediaReadingTask):
    """
    A luigi task for reading a Wikipedia corpus, but sentences are split in a way that's appropriate for french.
    """
    def _additional_formatting(self, line):
        """
        Provide additional formatting for a line in French.

        :param line: Line to be formatted.
        :type line: str
        :return: Formatted line.
        :rtype: str
        """
        french_sentence_tokenizer_path = self.task_config["SENTENCE_TOKENIZER_PATH"]
        download_nltk_resource_if_missing(french_sentence_tokenizer_path, "punkt")

        tokenizer = nltk.data.load(french_sentence_tokenizer_path)
        sentences = tokenizer.tokenize(line)
        return sentences


class FrenchPipelineRunInfoGenerationTask(PipelineRunInfoGenerationTask):
    """
    Generates information about the current run of the pipeline, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)


class FrenchRelationsDatabaseWritingTask(RelationsDatabaseWritingTask):
    """
    Writes relations extracted via (naive) Open Relation Extraction and Participation Extraction into a graph database, 
    but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchServerRelationMergingTask(task_config=self.task_config),\
               FrenchServerPropertiesCompletionTask(task_config=self.task_config),\
               FrenchPipelineRunInfoGenerationTask(task_config=self.task_config)

    def is_relevant_node(self, label, node_data):
        """
        Determine whether a node is relevant and should be written to the database. Overwritten from superclass to
        exactly suit this project.

        :param label: Node label
        :tyoe label: str
        :param node_data: Node's data.
        :type node_data: dict
        :return: Result of check.
        :rtype: bool
        """
        if "senses" not in node_data:
            return False

        # Include affairs
        if "affair" in label or "Affair" in label:
            return True

        # Include politicians
        if any([
            "personnalité politique" in get_if_exists(sense, "claims", "occupation", "target", default="")
            for sense in node_data["senses"]
        ]):
            return True

        # Include business people
        if any([
            "d'affaires" in get_if_exists(sense, "claims", "occupation", "target", default="")
            for sense in node_data["senses"]
        ]):
            return True

        # Include companies
        if any([
            "enterprise" in get_if_exists(sense, "description", default="")
            for sense in node_data["senses"]
        ]):
            return True

        # Include media
        if any([
            any([
                media_term in get_if_exists(sense, "description", default="")
                for media_term in ["radio", "blog", "télévision", "journal", "magazine", "radiodiffuseur"]
            ])
            for sense in node_data["senses"]
        ]):
            return True

        return False

    def categorize_node(self, label, node_data):
        """
        Assign a node a category out of a pre-defined set of categories. Overwritten from superclass to exactly suit
        this project.

        :param label: Node label
        :tyoe label: str
        :param node_data: Node's data.
        :type node_data: dict
        :return: Category for node.
        :rtype: str
        """
        if "senses" not in node_data:
            return "Miscellaneous"

        # Assign affair category
        if "affair" in label or "Affair" in label:
            return "Affair"

        # Assign politician category
        if any([
            "personnalité politique" in get_if_exists(sense, "claims", "occupation", "target", default="")
            for sense in node_data["senses"]
        ]):
            return "Politician"

        # Assign businessperson category
        if any([
            "d'affaires" in get_if_exists(sense, "claims", "occupation", "target", default="")
            for sense in node_data["senses"]
        ]):
            return "Businessperson"

        # Assign media category
        if any([
            any([
                media_term in get_if_exists(sense, "description", default="")
                for media_term in ["radio", "blog", "télévision", "journal", "magazine", "radiodiffuseur"]
            ])
            for sense in node_data["senses"]
        ]):
            return "Media"

        return super().categorize_node(label, node_data)


class FrenchNERTask(NERTask):
    """
    A luigi task tagging Named Entities in a sentence, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)


class FrenchPoSTaggingTask(PoSTaggingTask):
    """
    A luigi task tagging a sentence with PoS tags, but it's specifically to the french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)


class FrenchDependencyParseTask(DependencyParseTask):
    """
    A luigi task dependency-parsing a sentence, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)


class FrenchNaiveOpenRelationExtractionTask(NaiveOpenRelationExtractionTask):
    """
    A luigi task performing a naive version of Open Relation Extraction on a sentence, but it's specifically for the french
    Wikipedia.
    """
    def requires(self):
        return FrenchNERTask(task_config=self.task_config),\
               FrenchDependencyParseTask(task_config=self.task_config),\
               FrenchPoSTaggingTask(task_config=self.task_config)


class FrenchParticipationExtractionTask(ParticipationExtractionTask):
    """
    A luigi Task performing participation extraction, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchNERTask(task_config=self.task_config)


class FrenchRelationMergingTask(RelationMergingTask):
    """
    A luigi Task that merges extracted relations from other tasks, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchParticipationExtractionTask(task_config=self.task_config),\
               FrenchNaiveOpenRelationExtractionTask(task_config=self.task_config)


class FrenchPropertiesCompletionTask(PropertiesCompletionTask):
    """
    A luigi Task that  adds attributes from Wikidata to Named Entities, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchNERTask(task_config=self.task_config)


# -------------------- Tasks for french using Stanford CoreNLP server --------------------

class FrenchServerNERTask(ServerNERTask):
    """
    A luigi task tagging Named Entities in a sentence using a Stanford CoreNLP server, but it's specifically for the
    french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)

    @property
    def _corenlp_server_overriding_properties(self):
        return {
            "ner.model": self.task_config["CORENLP_STANFORD_NER_MODEL_PATH"],
            "pos.model": "edu/stanford/nlp/models/pos-tagger/french/french.tagger"
        }


class FrenchServerPoSTaggingTask(ServerPoSTaggingTask):
    """
    A luigi task tagging a sentence with PoS tags using a Stanford CoreNLP server, but it's specifically to the french
    Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)

    @property
    def _corenlp_server_overriding_properties(self):
        return {"pos.model": "edu/stanford/nlp/models/pos-tagger/french/french.tagger"}


class FrenchServerDependencyParseTask(ServerDependencyParseTask):
    """
    A luigi task dependency-parsing a sentence using a Stanford CoreNLP server, but it's specifically for the french
    Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaReadingTask(task_config=self.task_config)

    @property
    def _corenlp_server_overriding_properties(self):
        return {
            "parse.model": "edu/stanford/nlp/models/lexparser/frenchFactored.ser.gz",
            "pos.model": "edu/stanford/nlp/models/pos-tagger/french/french.tagger"
        }


class FrenchServerNaiveOpenRelationExtractionTask(ServerNaiveOpenRelationExtractionTask):
    """
    A luigi task performing a naive version of Open Relation Extraction on a sentence using a Stanford CoreNLP server,
    but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchServerNERTask(task_config=self.task_config),\
               FrenchServerDependencyParseTask(task_config=self.task_config),\
               FrenchServerPoSTaggingTask(task_config=self.task_config)


class FrenchServerParticipationExtractionTask(FrenchParticipationExtractionTask):
    """
    A luigi Task performing participation extraction, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchServerNERTask(task_config=self.task_config)


class FrenchServerRelationMergingTask(RelationMergingTask):
    """
    A luigi Task that merges extracted relations from other tasks, but it's specifically for the french Wikipedia.
    """

    def requires(self):
        return FrenchServerParticipationExtractionTask(task_config=self.task_config), \
               FrenchServerNaiveOpenRelationExtractionTask(task_config=self.task_config)


class FrenchServerPropertiesCompletionTask(FrenchPropertiesCompletionTask):
    """
    A luigi Task that  adds attributes from Wikidata to Named Entities, but it's specifically for the french Wikipedia.
    """
    def requires(self):
        return FrenchServerNERTask(task_config=self.task_config)


# --------------------------- Pipeline composition & starting ----------------------------

if __name__ == "__main__":
    # TODO (FEATURE): Use remote scheduler for server deployment [DU 18.04.17]
    french_task_config = build_task_config_for_language(
        tasks=[
            "wikipedia_reading",
            "named_entity_recognition",
            "pos_tagging",
            "dependency_parsing",
            "open_relation_extraction",
            "participation_extraction",
            "relation_merging",
            "properties_completion",
            "pipeline_run_info_generation",
            "relations_database_writing_task"
        ],
        language="french",
        config_file_path="./pipeline_config.py"
    )
    luigi.build(
        [FrenchRelationsDatabaseWritingTask(task_config=french_task_config)],
        local_scheduler=True, workers=1, log_level="INFO"
    )
