# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks for french texts.
"""

# STD
import codecs
import re

# EXT
import luigi
import luigi.format
import nltk.tokenize
import nltk.data

# PROJECT
from bwg.nlp.standard_tasks import (
    IDTaggingTask,
    NERTask,
    DependencyParseTask,
    NaiveOpenRelationExtractionTask
)
from bwg.nlp.config_management import build_task_config_for_language


class FrenchWikipediaCorpusCleaningTask(luigi.Task):
    """
    A Luigi task that cleans the corpus of certain Wikipedia artifacts, like
        * Deleting references from words ("décolé21" -> "décolé" / "Kwan3,4" -> "Kwan")
        * Deleting leftover Wikipedia markup, like "[masquer]"
        * Change encoding
        * Removes empty lines
    """
    task_config = luigi.DictParameter()

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["WIKIPEDIA_CLEANING_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    def run(self):
        input_path = self.task_config["WIKIPEDIA_CLEANING_INPUT_PATH"]
        corpus_encoding = self.task_config["CORPUS_ENCODING"]

        with codecs.open(input_path, "r", corpus_encoding) as input_file, self.output().open("w") as output_file:
            for line in input_file.readlines():
                if not line.strip():
                    continue  # Skip empty lines

                line = self._clean_markup(line)
                line = self._clean_references(line)
                output_file.write("{}\n".format(line))

    @staticmethod
    def _clean_markup(line):
        """
        Cleans Wikipedia in Markup.
        """
        return re.sub("\[.+?\]", "", line)

    def _clean_references(self, line):
        """
        Cleans references from words.
        """
        whitespace_tokenizer = nltk.tokenize.WhitespaceTokenizer()
        wikipedia_reference_pattern = self.task_config["WIKIPEDIA_REFERENCE_PATTERN"]
        cleaned_words = []

        for word in whitespace_tokenizer.tokenize(line):
            if re.match(wikipedia_reference_pattern, word):
                word = re.sub("\d+((,\d+)+)?", "", word)
            cleaned_words.append(word)

        return " ".join(cleaned_words)


class FrenchWikipediaSentenceSplittingTask(luigi.Task):
    """
    A Luigi task that splits sentences in the Wikipedia corpus.
    """
    task_config = luigi.DictParameter()

    def requires(self):
        return FrenchWikipediaCorpusCleaningTask(task_config=self.task_config)

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["WIKIPEDIA_SPLITTING_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    def run(self):
        with self.input().open("r") as input_file, self.output().open("w") as output_file:
            for line in input_file.readlines():
                for sentence in self._split_into_sentences(line):
                    output_file.write("{}\n".format(sentence))

    @staticmethod
    def _split_into_sentences(line):
        """
        Split text in a corpus into single sentences.
        """
        french_sentence_tokenizer = "tokenizers/punkt/PY3/french.pickle"

        # Download resource if necessary
        try:
            nltk.data.find(french_sentence_tokenizer)
        except LookupError:
            nltk.download("punkt")

        tokenizer = nltk.data.load(french_sentence_tokenizer)
        sentences = tokenizer.tokenize(line)
        return sentences


class FrenchIDTaggingTask(IDTaggingTask):
    """
    A luigi task reading a corpus, but it's specific for the french Wikipedia.
    """
    def requires(self):
        return FrenchWikipediaSentenceSplittingTask(task_config=self.task_config)


class FrenchNERTask(NERTask):
    """
    A luigi task tagging Named Entities in a sentence, but it's specific for the french Wikipedia.
    """
    def requires(self):
        return FrenchIDTaggingTask(task_config=self.task_config)


class FrenchDependencyParseTask(DependencyParseTask):
    """
    A luigi task dependency-parsing a sentence, but it's specific for the french Wikipedia.
    """
    def requires(self):
        return FrenchIDTaggingTask(task_config=self.task_config)


class FrenchNaiveOpenRelationExtractionTask(NaiveOpenRelationExtractionTask):
    """
    A luigi task performing a naive version of Open Relation Extraciton on a sentence, but it's specific for the french
    Wikipedia.
    """
    def requires(self):
        return FrenchNERTask(task_config=self.task_config), FrenchDependencyParseTask(task_config=self.task_config)


if __name__ == "__main__":
    # TODO (FEATURE): Use remote scheduler for server deployment
    french_task_config = build_task_config_for_language(
        tasks=[
            "wikipedia_corpus_cleaning",
            "wikipedia_sentence_splitting",
            "id_tagging",
            "named_entity_recognition",
            "dependency_parsing",
            "open_relation_extraction"
        ],
        language="french",
        config_file_path="../../pipeline_config.py"
    )
    luigi.build(
        [FrenchNaiveOpenRelationExtractionTask(task_config=french_task_config)],
        local_scheduler=True
    )
