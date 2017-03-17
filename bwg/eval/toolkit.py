# -*- coding: utf-8 -*-
"""
Module with different tools that help the user to evaluate results produced by the NLP pipeline, e.g. by creating
a custom evaluation set.
"""

# STD
import argparse
import random

# EXT
import luigi
import luigi.format

# PROJECT
from bwg.nlp import wikipedia_tasks


def main():
    """
    Main function. This script is intended to be run from the command line.
    """
    argument_parser = initialize_argument_parser()
    args = argument_parser.parse_args()


class ModifiedWikipediaReadingTask(wikipedia_tasks.WikipediaReadingTask):
    """
    Slightly modifying the WikipediaReadingTask to work with the EvluationSetCreator.
    """
    # Don't pass a task_config dict - we're only dealing with a single task here, so luigi parameters piling up
    # throughout the pipeline isn't a problem for this one.
    corpus_inpath = luigi.Parameter()
    corpus_encoding = luigi.Parameter()
    keep_percentage = luigi.Parameter()
    evaluation_set_outpath = luigi.Parameter()
    article_tag_pattern = '<doc id="(\d+)" url="(.+?)" title="(.+?)">'

    def output(self):
        text_format = luigi.format.TextFormat(self.task_config["CORPUS_ENCODING"])
        output_path = self.evaluation_set_outpath
        return luigi.LocalTarget(output_path, format=text_format)

    @property
    def workflow_resources(self):
        workflow_resources = {
            "corpus_inpath": self.corpus_inpath,
            "corpus_encoding": self.corpus_encoding,
            "article_tag_pattern": self.article_tag_pattern,
            "pretty_serialization": False
        }

        return workflow_resources

    def _output_article(self, id_, url, title, sentences, output_file, **additional):
        """
        Overwrite function from WikipediaReadingTask in order to sample articles.
        """
        if self._should_be_written():
            # Write header
            output_file.write('<doc id="{id}" url="{link}" title="{title}">'.format(id=id_, link=url, title=title))

            # Write lines
            for sentence in sentences:
                output_file.write(sentence)

            # Write footer
            output_file.write("</doc>")

    def _should_be_written(self):
        """
        Determine by random if an article should be included in the evaluation set.
        """
        return random.randrange(100) < self.keep_percentage


class EvaluationSetCreator:
    """
    Tool to create a custom evaluation set comprised of article from a given corpus, given the corpus itself is divided
    in "articles" like this:

    <doc id="32181" url="https://fr.wikipedia.org/wiki?curid=32181" title="Affaire Elf">
        ...

    </doc>
    <doc id="45864" url="https://fr.wikipedia.org/wiki?curid=45864" title="Affaire des fiches (France)">
        ...

    </doc>
    ...
    """
    def __init__(self, corpus_inpath, evaluation_set_outpath, **creation_kwargs):
        pass


def initialize_argument_parser():
    argument_parser = argparse.ArgumentParser()

    # TODO (Feature): Implement appropriate command line argument

    return argument_parser


# See main() at the top of the script.
if __name__ == "__main__":
    pass
