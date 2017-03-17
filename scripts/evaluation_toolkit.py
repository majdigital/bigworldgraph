# -*- coding: utf-8 -*-
"""
Toolkit for script used for this project.
"""

# STD
import argparse
import codecs
from collections import namedtuple
import random
import re
import sys

# EXT
import nltk

# TYPES
Article = namedtuple("Article", ["id", "title", "url", "sentences"])


def main():
    """
    Main function. This script is intended to be run from the command line.
    """
    parse_and_start()


def _start_evalset_creator():
    argument_parser = _init_evalset_argument_parser()
    args = argument_parser.parse_args()
    eval_set_creator = EvaluationSetCreator(**vars(args))
    eval_set_creator.create_test_set()


# --------------------------------------- Create an evaluation set -----------------------------------------------------

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
    languages = ["french", "english"]
    article_tag_pattern = '<doc id="(\d+)" url="(.+?)" title="(.+?)">'

    def __init__(self, **creation_kwargs):
        self.corpus_inpath = creation_kwargs["corpus_inpath"]
        self.evaluation_set_outpath = creation_kwargs["evalset_outpath"]
        self.corpus_encoding = creation_kwargs["corpus_encoding"]
        self.keep_percentage = creation_kwargs["keep_percentage"]
        self.keep_number = creation_kwargs["keep_number"]

        if self.keep_percentage is None and self.keep_number is None:
            self.keep_number = 10

        if self.keep_percentage is not None and self.keep_number is not None:
            raise AssertionError("You can't use both -kp -kn / --keep-percentage --keep-number at the same time!")

        # Figure out current language
        current_languages = [language for language in self.languages if creation_kwargs[language]]
        self.current_language = current_languages[0] if len(current_languages) != 0 else "english"

    def create_test_set(self):
        """
        Start a modified version of the WikipediaReadingTask to create an evaluation set from an already existing
        corpus.
        """
        articles = self._read_articles()
        sampled_articles = self._sample_articles(articles)
        self._write_articles(sampled_articles)

    def _read_articles(self):
        """
        Read articles from corpus.
        """
        articles = set()

        # Init "parsing" variables
        current_title = ""
        current_id = ""
        current_url = ""
        current_sentences = []
        skip_line = False

        with codecs.open(self.corpus_inpath, "rb", self.corpus_encoding) as input_file:
            for line in input_file.readlines():
                if skip_line:
                    skip_line = False
                    continue

                if re.match(self.article_tag_pattern, line):
                    current_id, current_url, current_title = self._extract_article_info(line)
                    skip_line = True

                elif line.strip() == "</doc>":
                    articles.add(
                        Article(id=current_id, title=current_title, url=current_url, sentences=tuple(current_sentences))
                    )
                    current_title, current_id, current_url, current_sentences = self._reset_vars()

                else:
                    if not line.strip():
                        continue
                    line = re.sub("</?.+?>", "", line)  # Remove other xml markup
                    formatted = getattr(self, "_additional_formatting_" + self.current_language)(line.strip())

                    if self.is_collection(formatted):
                        for line_ in formatted:
                            current_sentences.append(line_)

                    else:
                        current_sentences.append(line)

        return articles

    def _write_articles(self, articles):
        """
        Write articles into the evaluation set file.
        """
        with codecs.open(self.evaluation_set_outpath, "wb", self.corpus_encoding) as outfile:
            for article in articles:
                # Write header
                outfile.write(
                    '<doc id="{id}" url="{url}" title="{title}">\n'.format(
                        id=article.id, url=article.url, title=article.title
                    )
                )

                # Write sentences
                for sentence in article.sentences:
                    outfile.write(sentence)

                # Write footer
                outfile.write('</doc>\n')

    def _sample_articles(self, articles):
        if self.keep_number is None:
            return random.sample(articles, int(len(articles) * self.keep_percentage))
        elif self.keep_percentage is None:
            return random.sample(articles, self.keep_number)

    @staticmethod
    def _reset_vars():
        return "", "", "", []

    def _extract_article_info(self, line):
        """
        Extract relevant dates from articles.
        """
        article_tag_pattern = self.article_tag_pattern
        groups = re.match(article_tag_pattern, line).groups()
        return groups

    def _additional_formatting_french(self, line):
        french_sentence_tokenizer_path = "tokenizers/punkt/PY3/french.pickle"
        self.download_nltk_resource_if_missing(french_sentence_tokenizer_path, "punkt")

        tokenizer = nltk.data.load(french_sentence_tokenizer_path)
        sentences = tokenizer.tokenize(line)
        return sentences

    def _additional_formatting_english(self, line):
        return line

    @staticmethod
    def download_nltk_resource_if_missing(resource_path, resource):
        """
        Download a missing resource from the Natural Language Processing Toolkit.
        """
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(resource)

    @staticmethod
    def is_collection(obj):
        """
        Check if a object is iterable.
        """
        return hasattr(obj, '__iter__') and not isinstance(obj, str)


# ------------------------------------------ Argument parsing ----------------------------------------------------------

def _init_evalset_argument_parser():
    """
    Initialize the argument parser for the evaluation set creator.
    """
    argument_parser = argparse.ArgumentParser()

    argument_parser.add_argument(
        "-ce", "--create-evalset",
        required=True,
        action='store_true',
        help="Flag that will create an evaluation set from an existing corpus (comprised of articles)."
    )
    argument_parser.add_argument(
        "-i", "--corpus-inpath",
        type=str,
        required=True,
        help="Input path of corpus file (comprised of articles)."
    )
    argument_parser.add_argument(
        "-enc", "--corpus-encoding",
        type=str,
        default="utf-8",
        help="Encoding of input corpus."
    )
    argument_parser.add_argument(
        "-o", "--evalset-outpath",
        type=str,
        required=True,
        help="Output path of evaluation set."
    )
    argument_parser.add_argument(
        "-kp", "--keep-percentage",
        type=float,
        help="(Approximate) percentage of articles from the original corpus that make it into the evaluation set."
    )
    argument_parser.add_argument(
        "-kn", "--keep-number",
        type=int,
        help="Exact number of articles from the original corpus that make it into the evaluation set."
    )

    # Additional language support
    argument_parser.add_argument(
        "-en", "--english",
        action='store_true',
        help="Turn on additional language support for english."
    )
    argument_parser.add_argument(
        "-fr", "--french",
        action='store_true',
        help="Turn on additional language support for french."
    )

    return argument_parser


def parse_and_start():
    flags_to_parser = {
        "-ce": _start_evalset_creator,
        "--create-evalset": _start_evalset_creator
    }

    for arg in sys.argv:
        if arg in flags_to_parser:
            return flags_to_parser[arg]()

    raise Exception(
        "No suitable command line arguments found for this script. Maybe you meant {}?".format(
            " / ".join(list(flags_to_parser.keys()))
        )
    )

# See main() at the top of the script.
if __name__ == "__main__":
    main()
