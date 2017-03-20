# -*- coding: utf-8 -*-
"""
Toolkit for script used for this project.
"""

# STD
import argparse
import codecs
from collections import namedtuple, OrderedDict
import json
import random
import re
import sys

# EXT
import nltk

# CONST
ARTICLE_TAG_PATTERN = '<doc id="(\d+)" url="(.+?)" title="(.+?)">'

# TYPES
Article = namedtuple("Article", ["id", "title", "url", "sentences"])
ConfusionMatrix = namedtuple("ConfusionMatrix", ["tp", "tn", "fp", "fn"])


def main():
    """
    Main function. This script is intended to be run from the command line.
    """
    parse_and_start()


def _start_evalset_creator():
    """
    Parse arguments for the EvaluationSetCreator and run it.
    """
    argument_parser = _init_evalset_argument_parser()
    args = argument_parser.parse_args()
    eval_set_creator = EvaluationSetCreator(**vars(args))
    eval_set_creator.create_test_set()


def _start_ne_eval():
    argument_parser = _init_ne_eval_argument_parser()
    args = argument_parser.parse_args()
    ne_evaluator = NamedEntityEvaluator(**vars(args))
    ne_evaluator.evaluate_named_entities()


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
        language_formatting = {
            "french": self._additional_formatting_french,
            "english": self._additional_formatting_english
        }

        articles = read_articles(
            self.corpus_inpath,
            self.corpus_encoding,
            formatting_function=language_formatting[self.current_language]
        )
        sampled_articles = self._sample_articles(articles)
        self._write_articles(sampled_articles)

    def _write_articles(self, articles):
        """
        Write articles into the evaluation set file.
        """
        named_entities_path = self.evaluation_set_outpath.replace(".xml", "_nes.xml")
        raw_relations_path = self.evaluation_set_outpath.replace(".xml", "_relations_raw.xml")

        with codecs.open(self.evaluation_set_outpath, "wb", self.corpus_encoding) as outfile:
            with codecs.open(named_entities_path, "wb", self.corpus_encoding) as nes_file:
                nes_file.write(
                    "<!--\nIn this version of the evaluation corpus, annotate named entities in the following way:\n'"
                    "Hours later, <ne type='I-Pers'>Trump</ne> decried <ne type='I_ORG'>North Korea’s</ne> defiance and"
                    " also took aim at <ne type='I-ORG'>China</ne>, the North’s main patron.'\n(The tags can vary "
                    "depending on the tagset used by the pipelines named entity tagger.)\nPlease maintain line breaks."
                    "\n-->\n\n"
                )

                for article in articles:
                    # Write header
                    header = '<doc id="{id}" url="{url}" title="{title}">\n'.format(
                        id=article.id, url=article.url, title=article.title
                    )
                    outfile.write(header)
                    nes_file.write(header)

                    # Write sentences
                    for sentence in article.sentences:
                        outfile.write("{}\n".format(sentence))
                        nes_file.write("{}\n".format(sentence))

                    # Write footer
                    outfile.write('</doc>\n')
                    nes_file.write('</doc>\n')

        with codecs.open(raw_relations_path, "wb", self.corpus_encoding) as raw_relations_file:
            # TODO (Feature): Find good easy format for humans to enter relations
            raw_relations_file.write(
                "<!--\nAdd the relations that are expected to be found by the NLP pipeline here in the following form:"
                "\n-->\n\n"
            )

    def _sample_articles(self, articles):
        if self.keep_number is None:
            return random.sample(articles, int(len(articles) * self.keep_percentage))
        elif self.keep_percentage is None:
            return random.sample(articles, self.keep_number)

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


# -------------------------------------- Evaluate named entities -------------------------------------------------------


class NamedEntityEvaluator:
    """
    Tool that evaluates found named entities. To work, please provide two files: A *_nes.xml file, where named entities
    are manually enclosed in .xml-tags like this: 'Hours later, <ne type='I-Pers'>Trump</ne> decried <ne type='I_ORG'>
    North Korea’s</ne> defiance and also took aim at <ne type='I-ORG'>China</ne>, the North’s main patron.'

    The other file necessary is the one produced by the NLP pipeline, specifically from nlp.standard_tasks.NERTask. It's
     a JSON file. Please make sure that the articles in the evaluation set are included in the original corpus that was
    processed by the NERTask.
    """
    ne_tag_pattern = "<ne type=[\\'\"].+?[\\'\"]>.+?<\/ne>"

    def __init__(self, **creation_kwargs):
        self.eval_inpath = creation_kwargs["eval_inpath"]
        self.ne_inpath = creation_kwargs["ne_inpath"]
        self.output_path = creation_kwargs["output_path"]
        self.corpus_encoding = creation_kwargs["corpus_encoding"]

    def evaluate_named_entities(self):
        manually_annotated, ne_tagged = self._prepare_eval_data()

        for (manually_id, manually_article), (tagged_id, tagged_article) \
            in zip(manually_annotated.items(), ne_tagged.items()):
            assert manually_id == tagged_id  # Assure data sets are aligned

            # Get sentences from articles
            manually_sentences = manually_article.sentences
            tagged_sentences = [sentence_json["data"] for sentence_id, sentence_json in tagged_article["data"].items()]
            assert len(manually_sentences) == len(tagged_sentences)

            for manually_sentence, tagged_sentence in zip(manually_sentences, tagged_sentences):
                mannually_sentence = self.convert_manually_tagged_sentence(manually_sentence)

                # TODO (Feature): Create confusion matrix

    def _prepare_eval_data(self):
        """
        Read, filter and convert evaluation data into an appropriate data structure.
        """
        articles = self._read_manually_annotated_file()
        tagged_articles = self._read_ne_tagged_file()
        filtered_tagged_articles = self._filter_tagged_articles(articles, tagged_articles)
        del tagged_articles  # Big data structure

        # Convert data structures
        articles_dict = id_collection_to_dict(articles, lambda item: getattr(item, "id"))
        tagged_articles_dict = id_collection_to_dict(filtered_tagged_articles, lambda item: item["meta"]["id"])
        sorted_articles_dict = OrderedDict(sorted(articles_dict.items()))
        sorted_tagged_articles_dict = OrderedDict(sorted(tagged_articles_dict.items()))

        return sorted_articles_dict, sorted_tagged_articles_dict

    def _read_ne_tagged_file(self):
        """
        Read named entity tagged file from NLP pipeline.
        """
        tagged_articles = []

        with codecs.open(self.ne_inpath, "rb", self.corpus_encoding) as ne_file:
            for line in ne_file.readlines():
                deserialized_line = self.deserialize_line(line)
                tagged_articles.append(deserialized_line)

        return tagged_articles

    def _read_manually_annotated_file(self):
        """
        Read file with manually annotated name entities.
        """
        return read_articles(self.eval_inpath, self.corpus_encoding)

    def convert_manually_tagged_sentence(self, manually_tagged_sentence, default_tag='O'):
        """
        Convert a manually tagged sentence into a data structure that fits the output of the Stanford Named Entity
        Tagger.

        Example:

        "Hours later, <ne type='I-Pers'>Trump</ne> decried <ne type='I_ORG'>North Korea’s</ne> defiance and also took
        aim at <ne type='I-ORG'>China</ne>, the North’s main patron."

        == is converted to ==>

        [('Hours', 'O'), ('later', 'O'), ('Trump', 'I-Pers'), ('decried', 'O'), ('North', 'I-ORG'), ('Korea', 'I-ORG'),
        ('’s', 'I-ORG'), ('defiance', 'O'), ('and', 'O'), ('also', 'O'), ('took', 'O'), ('aim', 'O'), ('at', 'O'),
        ('China', 'I-ORG'), ('the', 'O'), ('North', 'O'), ('’s', 'O'), ('main', 'O'), ('patron', 'O'), ('.', 'O')]
        """
        tokens_string = str(manually_tagged_sentence)

        for match in re.findall(self.ne_tag_pattern, manually_tagged_sentence):
            ne_tag = re.findall("type=[\\'\"](.+?)[\\'\"]", match)[0]
            tokens = re.findall("<ne .+?>(.+?)<\/ne>", match)[0].split(" ")
            tokens_string = re.sub(
                match,
                " ".join(["{}|{}".format(token, ne_tag) for token in tokens]),
                tokens_string
            )

        ne_tagged_tokens = [
            tuple(token.split("|"))
            if "|" in token else (token, default_tag)
            for token in tokens_string.split(" ")
        ]

        return ne_tagged_tokens


    @staticmethod
    def _filter_tagged_articles(articles, tagged_articles):
        """
        Filter out those named entity tagged articles from the NLP pipeline which also appear in the evaluation set.
        """
        article_ids = set([article.id for article in articles])

        return [
            tagged_article
            for tagged_article in tagged_articles
            if tagged_article["meta"]["id"] in article_ids
        ]

    def deserialize_line(self, line):
        """
        Transform a line in a file that was created as a result from a Luigi task into its metadata and main data.
        """
        return json.loads(line, encoding=self.corpus_encoding)


# ------------------------------------------ Helper functions ----------------------------------------------------------


def read_articles(corpus_inpath, corpus_encoding="utf-8", formatting_function=None):
    """
    Read articles from corpus.
    """
    global ARTICLE_TAG_PATTERN
    articles = set()

    # Init "parsing" variables
    current_title = ""
    current_id = ""
    current_url = ""
    current_sentences = []
    skip_line = False
    comment = False

    with codecs.open(corpus_inpath, "rb", corpus_encoding) as input_file:
        for line in input_file.readlines():
            line = line.strip()

            # Skip lines that should be ignored (article headers withing the article, xml comments, etc.)
            if skip_line:
                if not comment or "-->" in line:
                    comment = False
                    skip_line = False
                continue

            if line == current_title:
                continue

            # Identify xml/html comments
            if "<!--" in line:
                if "-->" not in line:
                    skip_line = True
                    comment = True
                continue

            # Identify beginning of new article
            if re.match(ARTICLE_TAG_PATTERN, line):
                current_id, current_url, current_title = _extract_article_info(line)

            # Identify end of article
            elif line.strip() == "</doc>":
                articles.add(
                    Article(id=current_id, title=current_title, url=current_url, sentences=tuple(current_sentences))
                )
                current_title, current_id, current_url, current_sentences = _reset_vars()

            # Just add a new line to ongoing article
            else:
                if not line.strip():
                    continue

                formatted = None
                if formatting_function is not None:
                    formatted = formatting_function(line)

                if formatted is not None:
                    if is_collection(formatted):
                        for line_ in formatted:
                            current_sentences.append(line_)
                    else:
                        current_sentences.append(formatted)
                else:
                    current_sentences.append(line)

    return articles


def _reset_vars():
    return "", "", "", []


def _extract_article_info(line):
    """
    Extract relevant dates from articles.
    """
    global ARTICLE_TAG_PATTERN
    groups = re.match(ARTICLE_TAG_PATTERN, line).groups()
    return groups


def is_collection(obj):
    """
    Check if a object is iterable.
    """
    return hasattr(obj, '__iter__') and not isinstance(obj, str)


def id_collection_to_dict(collection, id_getter):
    """
    Convert a collection of items that possess an id attribute to a dictionary which the same id as their key.
    """
    id_dict = {}

    for item in collection:
        item_id = id_getter(item)
        id_dict[item_id] = item

    return id_dict


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
        help="Input path to corpus file (comprised of articles)."
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


def _init_ne_eval_argument_parser():
    """
    Initialize the argument parser for the named entity evaluator.
    """
    argument_parser = argparse.ArgumentParser()

    argument_parser.add_argument(
        "-ene", "--eval-nes",
        required=True,
        action='store_true',
        help="Flag that will evaluate named entities found by the NLP pipeline with a manually annotated file."
    )
    argument_parser.add_argument(
        "-ei", "--eval-inpath",
        type=str,
        required=True,
        help="Input path to manually annotated evaluation set (xml)."
    )
    argument_parser.add_argument(
        "-ni", "--ne-inpath",
        type=str,
        required=True,
        help="Input path to named entity tagged file from NLP-Pipeline (json)."
    )
    argument_parser.add_argument(
        "-o", "--output-path",
        type=str,
        help="When flag is set, output of this script will also be written to an output file."
    )
    argument_parser.add_argument(
        "-enc", "--corpus-encoding",
        type=str,
        default="utf-8",
        help="Encoding of input corpus."
    )

    return argument_parser


def parse_and_start():
    flags_to_parser = {
        "-ce": _start_evalset_creator,
        "--create-evalset": _start_evalset_creator,
        "-ene": _start_ne_eval,
        "--eval-nes": _start_ne_eval
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
