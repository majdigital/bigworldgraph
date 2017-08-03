# -*- coding: utf-8 -*-
"""
NLP Pipeline tasks connected to resources of the Wikimedia Foundation.
"""

# STD
import codecs
import re

# EXT
import luigi
import luigi.format

# PROJECT
from bwg.decorators import time_function
from bwg.helpers import is_collection
from bwg.serializing import (
    serialize_article
)


class WikipediaReadingTask(luigi.Task):
    """
    A luigi task that reads an extracted Wikipedia corpus (see README).
    """
    task_config = luigi.DictParameter()

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["WIKIPEDIA_READING_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        corpus_inpath = self.task_config["CORPUS_INPATH"]
        corpus_encoding = self.task_config["CORPUS_ENCODING"]

        # Init "parsing" variables
        current_title = ""
        current_id = ""
        current_url = ""
        current_sentences = []
        skip_line = False
        comment = False

        with codecs.open(corpus_inpath, "r", corpus_encoding) as input_file, self.output().open("w") as output_file:
            for line in input_file.readlines():
                line = line.strip()

                # Skip lines that should be ignored (article headers withing the article, xml comments, etc.)
                if skip_line:
                    if not comment or "-->" in line:
                        comment = False
                        skip_line = False
                    continue

                # Skip line if line is the title (title is already given in the <doc> tag)
                if line == current_title:
                    continue

                # Identify xml/html comments
                if "<!--" in line:
                    if "-->" not in line:
                        skip_line = True
                        comment = True
                    continue

                # Identify beginning of new article
                if re.match(self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"], line):
                    current_id, current_url, current_title = self._extract_article_info(line)

                # Identify end of article
                elif line.strip() == "</doc>":
                    self._output_article(
                        current_id, current_url, current_title, current_sentences, output_file, state="parsed"
                    )
                    current_title, current_id, current_url, current_sentences = self._reset_vars()

                # Just add a new line to ongoing article
                else:
                    if not line.strip():
                        continue

                    # Apply additional formatting to line if an appropriate function is given
                    line = re.sub("</?.+?>", "", line)  # Remove other xml markup
                    formatted = self._additional_formatting(line.strip())

                    # Add line
                    if is_collection(formatted):
                        for line_ in formatted:
                            current_sentences.append(line_)

                    else:
                        current_sentences.append(line)

    def _output_article(self, id_, url, title, sentences, output_file, **additional):
        """
        Write read article to file.
        
        :param id_: Article ID.
        :type id_: int
        :param url: URL of current article.
        :type url: str
        :param title: Title of current article.
        :type title: str
        :param sentences: Article sentences. 
        :type sentences: list
        :param output_file: Output file the article is written to.
        :type output_file: _io.TextWrapper
        :param additional: Additional parameters for serialization.
        :type additional: dict
        """
        article_json = serialize_article(
            id_, url, title, sentences, **additional
        )
        output_file.write("{}\n".format(article_json))

    def _additional_formatting(self, line):
        """
        Provide additional formatting for a line possible subclasses by overwriting this function.
        
        :param line: Line to be formatted.
        :type line: str
        :return: Formatted line.
        :rtype: str
        """
        return line

    @staticmethod
    def _reset_vars():
        """
        Reset temporary variables used while reading the input corpus.
        
        :return: Reset variables.
        :rtype: tuple
        """
        return "", "", "", []

    def _extract_article_info(self, line):
        """
        Extract important information from the opening article XML tag.
        
        :param line: Line with article information.
        :type line: str
        :return: Information about article.
        :rtype: tuple
        """
        article_tag_pattern = self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"]
        groups = re.match(article_tag_pattern, line).groups()
        return groups


class SimpleReadingTask(luigi.Task):
    """
    A luigi task that reads an extracted Wikipedia corpus (see README).
    """
    task_config = luigi.DictParameter()

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.task_config["SIMPLE_READING_OUTPUT_PATH"]
        return luigi.LocalTarget(output_path, format=text_format)

    @time_function(is_classmethod=True)
    def run(self):
        corpus_inpath = self.task_config["CORPUS_INPATH"]
        corpus_encoding = self.task_config["CORPUS_ENCODING"]

        # Init "parsing" variables
        current_title = ""
        current_id = ""
        current_url = ""
        current_sentences = []
        skip_line = False
        comment = False

        with codecs.open(corpus_inpath, "r", corpus_encoding) as input_file, self.output().open("w") as output_file:
            for line in input_file.readlines():
                line = line.strip()

                # Skip lines that should be ignored (article headers withing the article, xml comments, etc.)
                if skip_line:
                    if not comment or "-->" in line:
                        comment = False
                        skip_line = False
                    continue

                # Skip line if line is the title (title is already given in the <doc> tag)
                if line == current_title:
                    continue

                # Identify xml/html comments
                if "<!--" in line:
                    if "-->" not in line:
                        skip_line = True
                        comment = True
                    continue

                # Identify beginning of new article
                if re.match(self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"], line):
                    current_id, current_url, current_title = self._extract_article_info(line)

                # Identify end of article
                elif line.strip() == "</doc>":
                    self._output_article(
                        current_id, current_url, current_title, current_sentences, output_file, state="parsed"
                    )
                    current_title, current_id, current_url, current_sentences = self._reset_vars()

                # Just add a new line to ongoing article
                else:
                    if not line.strip():
                        continue

                    # Apply additional formatting to line if an appropriate function is given
                    line = re.sub("</?.+?>", "", line)  # Remove other xml markup
                    current_sentences.append(line)

    def _output_article(self, id_, url, title, sentences, output_file, **additional):
        """
        Write read article to file.

        :param id_: Article ID.
        :type id_: int
        :param url: URL of current article.
        :type url: str
        :param title: Title of current article.
        :type title: str
        :param sentences: Article sentences.
        :type sentences: list
        :param output_file: Output file the article is written to.
        :type output_file: _io.TextWrapper
        :param additional: Additional parameters for serialization.
        :type additional: dict
        """
        article_json = serialize_article(
            id_, url, title, sentences, **additional
        )
        output_file.write("{}\n".format(article_json))

    @staticmethod
    def _reset_vars():
        """
        Reset temporary variables used while reading the input corpus.

        :return: Reset variables.
        :rtype: tuple
        """
        return "", "", "", []

    def _extract_article_info(self, line):
        """
        Extract important information from the opening article XML tag.

        :param line: Line with article information.
        :type line: str
        :return: Information about article.
        :rtype: tuple
        """
        article_tag_pattern = self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"]
        groups = re.match(article_tag_pattern, line).groups()
        return groups