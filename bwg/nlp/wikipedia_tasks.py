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
from bwg.misc.helpers import is_collection, time_function
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

    @time_function(is_classmethod=True)
    def run(self):
        corpus_inpath = self.workflow_resources["corpus_inpath"]
        corpus_encoding = self.workflow_resources["corpus_encoding"]

        # Init "parsing" variables
        current_title = ""
        current_id = ""
        current_url = ""
        current_sentences = []
        skip_line = False

        # TODO (Documentation): Add documentation like in scripts.evaluation_toolkit.pys
        with codecs.open(corpus_inpath, "r", corpus_encoding) as input_file, self.output().open("w") as output_file:
            for line in input_file.readlines():
                line = line.strip()

                if skip_line:
                    skip_line = False
                    continue

                if line == current_title:
                    continue

                if re.match(self.workflow_resources["article_tag_pattern"], line):
                    current_id, current_url, current_title = self._extract_article_info(line)

                elif line.strip() == "</doc>":
                    self._output_article(
                        current_id, current_url, current_title, current_sentences, output_file, state="parsed",
                        pretty=self.workflow_resources["pretty_serialization"]
                    )
                    current_title, current_id, current_url, current_sentences = self._reset_vars()

                else:
                    if not line.strip():
                        continue
                    line = re.sub("</?.+?>", "", line)  # Remove other xml markup
                    formatted = self._additional_formatting(line.strip())

                    if is_collection(formatted):
                        for line_ in formatted:
                            current_sentences.append(line_)

                    else:
                        current_sentences.append(line)

    @property
    def workflow_resources(self):
        corpus_inpath = self.task_config["CORPUS_INPATH"]
        corpus_encoding = self.task_config["CORPUS_ENCODING"]
        article_tag_pattern = self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"]
        pretty_serialization = self.task_config["PRETTY_SERIALIZATION"]

        workflow_resources = {
            "corpus_inpath": corpus_inpath,
            "corpus_encoding": corpus_encoding,
            "article_tag_pattern": article_tag_pattern,
            "pretty_serialization": pretty_serialization
        }

        return workflow_resources

    def _output_article(self, id_, url, title, sentences, output_file, **additional):
        article_json = serialize_article(
            id_, url, title, sentences, state=additional["state"],
            pretty=additional["pretty"]
        )
        output_file.write("{}\n".format(article_json))

    def _additional_formatting(self, line):
        """
        Provide additional formatting for a line possible subclasses by overwriting this function.
        """
        return line

    @staticmethod
    def _reset_vars():
        return "", "", "", []

    def _extract_article_info(self, line):
        article_tag_pattern = self.task_config["WIKIPEDIA_ARTICLE_TAG_PATTERN"]
        groups = re.match(article_tag_pattern, line).groups()
        return groups
