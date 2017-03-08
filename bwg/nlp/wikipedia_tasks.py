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

# PROJECT
from bwg.nlp.utilities import serialize_article, TaskWorkflowMixin


class WikipediaReadingTask(luigi.Task, TaskWorkflowMixin):
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
                        current_id, current_url, current_title, current_sentences, state="parsed",
                        pretty=pretty_serialization
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
