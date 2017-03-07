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
from bwg.nlp.utilities import serialize_article


class WikipediaReadingTask(luigi.Task):
    """
    A luigi task that reads an extracted Wikipedia corpus (see README).
    """
    task_config = luigi.DictParameter()

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["WIKIPEDIA_READING_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    def run(self):
        # Init necessary resources
        corpus_inpath = self.task_config["CORPUS_INPATH"]
        corpus_encoding = self.task_config["CORPUS_ENCODING"]
        article_tag_pattern = self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"]
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]

        # Init "parsing" variables
        current_title = ""
        current_id = ""
        current_url = ""
        current_sentences = []
        skip_line = False

        with codecs.open(corpus_inpath, "r", corpus_encoding) as input_file, self.output().open("w") as output_file:
            for line in input_file.readlines():
                if skip_line:
                    skip_line = False
                    continue

                if re.match(article_tag_pattern, line):
                    current_id, current_url, current_title = self._extract_article_info(line)
                    skip_line = True
                elif line.strip() == "</doc>":
                    article_json = serialize_article(
                        current_id, current_url, current_title, current_sentences, article_state="parsed",
                        pretty=True
                    )
                    output_file.write("{}\n".format(article_json))
                    current_title, current_id, current_url, current_sentences = self._reset_vars()
                else:
                    if not line.strip():
                        continue
                    line = re.sub("</?.+?>", "", line)  # Remove other xml markup
                    current_sentences.append(line.strip())

    @staticmethod
    def _reset_vars():
        return "", "", "", []

    def _extract_article_info(self, line):
        article_tag_pattern = self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"]
        groups = re.match(article_tag_pattern, line).groups()
        return groups


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
        # Init necessary resources
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
