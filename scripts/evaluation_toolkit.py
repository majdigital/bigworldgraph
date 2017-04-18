# -*- coding: utf-8 -*-
"""
Toolkit for script used for this project.
"""

# STD
import argparse
import codecs
from collections import namedtuple, OrderedDict, defaultdict
import json
import random
import re
import sys

# CONST
ARTICLE_OPENING_TAG_PATTERN = '<doc id="(\d+)" url="(.+?)" title="(.+?)">'
ARTICLE_CLOSING_TAG = '</doc>'
RELATIONS_OPENING_TAG_PATTERN = '<relations id="(\d+)" title="(.+?)">'
RELATIONS_CLOSING_TAG = '</relations>'

# TYPES
Article = namedtuple("Article", ["id", "title", "url", "contents"])
Relations = namedtuple("Relations", ["id", "title", "contents"])


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
    """
    Parse arguments for the NamedEntityEvaluator and run it.
    """
    argument_parser = _init_ne_eval_argument_parser()
    args = argument_parser.parse_args()
    ne_evaluator = NamedEntityEvaluator(**vars(args))
    ne_evaluator.evaluate_named_entities()


def _start_relations_eval():
    """
    Parse arguments for the RelationsEvaluator and run it.
    """
    argument_parser = _init_relations_eval_argument_parser()
    args = argument_parser.parse_args()
    relations_evaluator = RelationsEvaluator(**vars(args))
    relations_evaluator.evaluate_relations()


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
        self.ne_inpath = creation_kwargs["ne_inpath"]
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
        sys.stdout.write("Reading articles...")
        articles = read_articles_file(self.ne_inpath, self.corpus_encoding)
        print("\rReading articles... Done!", flush=True)

        sampled_articles = self._sample_articles(articles)
        sys.stdout.flush()
        print("\rSampling articles... Done!", flush=True)
        self._write_articles(sampled_articles)

    def _write_articles(self, articles):
        """
        Write articles into the evaluation set file.
        """
        named_entities_path = self.evaluation_set_outpath.replace(".xml", "_nes.xml")
        raw_relations_path = self.evaluation_set_outpath.replace(".xml", "_relations.xml")

        with codecs.open(self.evaluation_set_outpath, "wb", self.corpus_encoding) as outfile:
            with codecs.open(named_entities_path, "wb", self.corpus_encoding) as nes_file:
                with codecs.open(raw_relations_path, "wb", self.corpus_encoding) as relations_file:
                    # Write comments to help user
                    nes_file.write(
                        "<!--\nIn this version of the evaluation corpus, annotate named entities in the following "
                        "way:\n'"
                        "Hours later , <ne type='I-Pers'>Trump</ne> decried <ne type='I_ORG'>North Korea ’s</ne> "
                        "defiance "
                        "and also took aim at <ne type='I-ORG'>China</ne> , the North 's main patron . '\n(The tags "
                        "can "
                        "vary depending on the tag set used by the pipelines named entity tagger.)\nPlease maintain "
                        "line "
                        "breaks. Also be careful not to add or remove whitespaces by accident.\n-->\n\n"
                    )
                    relations_file.write(
                        "<!--\nAdd the relations that are expected to be found by the NLP pipeline here.\n\nTry to "
                        "follow these"
                        " two steps:\n\t1. Add all Named Entities within the article to a relation that is called "
                        "'participated"
                        " in' and has the title of the\n\t   article as its object.\n\t2. Add all 'normal' relation "
                        "within the"
                        " text as subject - verb - object divided by tabs. Follow your intuition to\n\t   define the "
                        "scope of "
                        "subject and object (phrase).\n\t3. Delete the original article (everything inside the <doc> "
                        "tag)\n\t"
                        "4. Delete this comment (optional)\n\nExample:\n\n<doc id='12345' url='www.great-news.com' "
                        "title="
                        "'North Korea missile crisis'>\nHours later, Trump decried North Korea’s defiance and also "
                        "took aim at "
                        "China, the North's main patron.\n</doc>\n<relations id='12345' title='North Korea missile "
                        "crisis'>\n"
                        "Trump\tparticipated in\tNorth Korea missile crisis\nNorth Korea\tparticipated in\tNorth "
                        "Korea missile "
                        " crisis\nChina\tparticipated in\tNorth Korea missile crisis\nTrump\tdecried\tNorth Korea’s "
                        "defiance\n"
                        "Trump\ttook aim at\tChina\nChina\tmain patron\tthe North's\n</relations>\n\n(Don't include "
                        "headers "
                        " like 'Example'here. Just a plain file with all the relations, enclosed by a "
                        "<relations>\ntag"
                        " for all relations of a specific article. If you're handling multiple articles, "
                        "just use different "
                        "<relations>\nblocks, each for one article.)\n-->\n\n"
                    )

                    i = 0
                    for article in articles:
                        i += 1
                        sys.stdout.write(
                            "\rWriting article {} of {}... ({:.2f} % complete)".format(
                                i, len(articles), (i-1) / len(articles) * 100.0
                            )
                        )

                        # Write header
                        meta = article["meta"]
                        header = '<doc id="{id}" url="{url}" title="{title}">\n'.format(
                            id=meta["id"], url=meta["url"], title=meta["title"]
                        )
                        outfile.write(header)
                        nes_file.write(header)
                        relations_file.write(header)

                        # Write sentences
                        for sentence_id, sentence_json in get_sorted_dict_items(article["data"]):
                            sentence = self._get_sentence(sentence_json)
                            outfile.write("{}\n".format(sentence))
                            nes_file.write("{}\n".format(sentence))
                            relations_file.write("{}\n".format(sentence))

                        # Write footer
                        outfile.write('</doc>\n')
                        nes_file.write('</doc>\n')
                        relations_file.write('</doc>\n')

                        # Write relations tag
                        relations_file.write(
                            '<relations id="{id}" title="{title}">\n</relations>\n'.format(
                                id=meta["id"], title=meta["title"]
                            )
                        )
                        sys.stdout.flush()

                print("\rWriting articles... Done!", flush=True)

    @staticmethod
    def _get_sentence(sentence_json):
        return " ".join([token for token, ne_tag in sentence_json["data"]])

    def _sample_articles(self, articles):
        if self.keep_number is None:
            return random.sample(articles, int(len(articles) * self.keep_percentage))
        elif self.keep_percentage is None:
            return random.sample(articles, self.keep_number)

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
        self.default_tag = 'O'

    def evaluate_named_entities(self):
        print("Reading in data...")
        manually_annotated, ne_tagged = self._prepare_eval_data()
        print("\rReading in data... Done!", flush=True)
        confusion_matrices = defaultdict(lambda: ConfusionMatrix())

        print("Starting evaluating...")
        i = 0
        for (manually_id, manually_article), (tagged_id, tagged_article) \
            in zip(manually_annotated.items(), ne_tagged.items()):
            i += 1
            print(
                "\rEvaluating article {} of {}... ({:.2f} % complete))".format(
                    i, len(manually_annotated), (i-1) / len(manually_annotated) * 100
                ),
                flush=True
            )
            assert manually_id == tagged_id  # Assure data sets are aligned

            # Get sentences from articles
            manually_sentences = manually_article.contents
            tagged_sentences = self._get_sentences_from_article_json(tagged_article)
            assert len(manually_sentences) == len(tagged_sentences)

            for manually_sentence, tagged_sentence in zip(manually_sentences, tagged_sentences):
                manually_sentence = self.convert_manually_tagged_sentence(manually_sentence)

                for ne_tuple1, ne_tuple2 in zip(manually_sentence, tagged_sentence):
                    token1, gold_ne_tag = ne_tuple1
                    token2, ne_tag = ne_tuple2
                    assert token1 == token2

                    confusion_matrices = self._fill_confusion_matrix(ne_tag, gold_ne_tag, confusion_matrices)

        print("\rEvaluating articles... Done!", flush=True)
        print("")
        for tag, confusion_matrix in confusion_matrices.items():
            confusion_matrix.prettyprint("Confusion matrix for " + tag)

    def _fill_confusion_matrix(self, ne_tag, gold_ne_tag, confusion_matrices):
        """
        Fill the corresponding confusion matrix based on the current tag and gold tag.
        """
        # True Positive
        # Named entity was rightfully tagged
        if ne_tag == gold_ne_tag and ne_tag != self.default_tag:
            confusion_matrices["all"].increment_cell("tp")
            confusion_matrices[gold_ne_tag].increment_cell("tp")

        # True Negative
        # A normal token was rightfully _not_ tagged
        elif ne_tag == gold_ne_tag and ne_tag == self.default_tag:
            confusion_matrices["all"].increment_cell("tn")
            confusion_matrices[gold_ne_tag].increment_cell("tn")

        # False Positive
        # A normal token was wrongfully tagged as a named entity
        elif ne_tag != gold_ne_tag and ne_tag != self.default_tag and gold_ne_tag == self.default_tag:
            confusion_matrices["all"].increment_cell("fp")
            confusion_matrices[gold_ne_tag].increment_cell("fp")

        # False Negative
        # A named entity was not identified and therefore wrongfully not tagged as one
        elif ne_tag != gold_ne_tag and ne_tag == self.default_tag and gold_ne_tag != self.default_tag:
            confusion_matrices["all"].increment_cell("fn")
            confusion_matrices[gold_ne_tag].increment_cell("fn")

        # Special case: There was named entity tag assigned, but it was the wrong one
        elif ne_tag != gold_ne_tag and ne_tag != self.default_tag and gold_ne_tag != self.default_tag:
            # Cannot be added to the global matrix -> is not possible to visualize in a binary one
            confusion_matrices[gold_ne_tag].increment_cell("fn")

        return confusion_matrices

    @staticmethod
    def _get_sentences_from_article_json(article_json):
        """
        Get sentence data from all sentences from an article json object.
        """
        return [
            sentence_json["data"]
            for sentence_id, sentence_json in get_sorted_dict_items(article_json["data"])
        ]

    def _prepare_eval_data(self):
        """
        Read, filter and convert evaluation data into an appropriate data structure.
        """
        articles = self._read_manually_annotated_file()
        tagged_articles = read_articles_file(self.ne_inpath, self.corpus_encoding)
        filtered_tagged_articles = filter_tagged_articles(articles, tagged_articles)
        del tagged_articles  # Big data structure

        # Convert data structures
        articles_dict = id_collection_to_dict(articles, lambda item: getattr(item, "id"))
        tagged_articles_dict = id_collection_to_dict(filtered_tagged_articles, lambda item: item["meta"]["id"])
        sorted_articles_dict = OrderedDict(sorted(articles_dict.items()))
        sorted_tagged_articles_dict = OrderedDict(sorted(tagged_articles_dict.items()))

        return sorted_articles_dict, sorted_tagged_articles_dict

    def _read_manually_annotated_file(self):
        """
        Read file with manually annotated name entities.
        """
        global ARTICLE_OPENING_TAG_PATTERN, ARTICLE_CLOSING_TAG
        target_variables = {
            "id": "",
            "url": "",
            "title": "",
        }

        return read_targets(
            self.eval_inpath, ARTICLE_OPENING_TAG_PATTERN, ARTICLE_CLOSING_TAG, target_class=Article,
            target_variables=target_variables, extraction_function=_extract_article_info,
            corpus_encoding=self.corpus_encoding
        )

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
            ne_tag = re.findall("type=[\\'\"](.+?)[\\'\"]", match)[0]  # Extract NE tag
            tokens = re.findall("<ne .+?>(.+?)<\/ne>", match)[0].split(" ")  # Get tokens enclosed by NE tag
            # Map NE tags onto every token within the tag
            tokens_string = re.sub(
                match,
                " ".join(["{}|{}".format(token, ne_tag) for token in tokens]),
                tokens_string
            )

        ne_tagged_tokens = [
            token.split("|")
            if "|" in token else [token, default_tag]
            for token in tokens_string.split(" ")
        ]

        return ne_tagged_tokens

# ----------------------------------------- Evaluate relations ---------------------------------------------------------


class RelationsEvaluator:
    """
    Tool that evaluates found named entities. To work, please provide two files: A *_relations.xml file, where named
    entities are manually extracted from a text and enclosed in in a <relations> tag (for more details, see the actual
    *_relations.xml file).

    The other file necessary is the one produced by the NLP pipeline, specifically from
    nlp.standard_tasks.OpenRelationExtractionTask. It's a JSON file. Please make sure that the articles in the
    evaluation set are included in the original corpus that was processed by the NERTask.
    """
    def __init__(self, **creation_kwargs):
        self.eval_inpath = creation_kwargs["eval_inpath"]
        self.relations_inpath = creation_kwargs["relations_inpath"]
        self.corpus_encoding = creation_kwargs["corpus_encoding"]

    def evaluate_relations(self):
        confusion_matrix = RelationExtractionConfusionMatrix()

        sorted_relations_dict, sorted_extracted_relations_dict = self._prepare_eval_data()

        for (manually_id, manually_article), (extracted_id, extracted_article) in \
                zip(sorted_relations_dict.items(), sorted_extracted_relations_dict.items()):

            manual_relations = self._convert_manual_relations(manually_article.contents)
            extracted_relations = self._convert_extracted_relations(extracted_article)
            confusion_matrix.extractions += len(extracted_relations)

            correct_extractions = 0
            for manuel_relation in manual_relations:
                for extracted_relation in extracted_relations:
                    if manuel_relation == extracted_relation:
                        correct_extractions += 1
                        confusion_matrix.increment_cell("correct")
                        break

            # Number of relations is number of extracted relations + gold relations - intersection
            confusion_matrix.relations += (len(manual_relations) + len(extracted_relations) - 2 * correct_extractions)

        confusion_matrix.prettyprint()

    def _read_manually_annotated_file(self):
        """
        Read file with manually extracted relations.
        """
        global RELATIONS_OPENING_TAG_PATTERN, RELATIONS_CLOSING_TAG
        target_variables = {
            "id": "",
            "title": ""
        }

        targets = read_targets(
            self.eval_inpath, RELATIONS_OPENING_TAG_PATTERN, RELATIONS_CLOSING_TAG, target_class=Relations,
            target_variables=target_variables, extraction_function=self._extract_relations_info,
            corpus_encoding=self.corpus_encoding
        )
        return targets

    @staticmethod
    def _convert_manual_relations(manual_relations):
        return [
            Relation(*manual_relation_string.split("\t"))
            for manual_relation_string in manual_relations
        ]

    @staticmethod
    def _convert_extracted_relations(extracted_article):
        relations = []

        for sentence_id, sentence in extracted_article["data"].items():
            relations.extend(
                [
                    Relation(**extracted_relation["data"])
                    for extracted_relation_id, extracted_relation in sentence["data"]["relations"]
                ]
            )

        return relations

    def _prepare_eval_data(self):
        """
        Read, filter and convert evaluation data into an appropriate data structure.
        """
        manual_relations = self._read_manually_annotated_file()
        extracted_relations = read_articles_file(self.relations_inpath, self.corpus_encoding)
        filtered_extracted_relations = filter_tagged_articles(manual_relations, extracted_relations)
        del extracted_relations  # Big data structure

        # Convert data structures
        relations_dict = id_collection_to_dict(manual_relations, lambda item: getattr(item, "id"))
        filtered_extracted_relations_dict = id_collection_to_dict(
            filtered_extracted_relations, lambda item: item["meta"]["id"]
        )
        sorted_relations_dict = OrderedDict(sorted(relations_dict.items()))
        sorted_extracted_relations_dict = OrderedDict(sorted(filtered_extracted_relations_dict.items()))

        return sorted_relations_dict, sorted_extracted_relations_dict

    @staticmethod
    def _extract_relations_info(line, target_opening_tag_pattern):
        """
        Extract relevant dates from articles.
        """
        groups = re.match(target_opening_tag_pattern, line).groups()
        return {
            "id": groups[0],
            "title": groups[1]
        }


# --------------------------------------- Helper functions / classes ---------------------------------------------------


class ConfusionMatrix:
    """
    Simple class for a confusion matrix.
    """
    def __init__(self):
        self.tp = 0  # True positives
        self.tn = 0  # True negatives
        self.fp = 0  # False positives
        self.fn = 0  # False negatives
        self.epsilon = 1e-20  # Add to avoid division by zero

        self.defined_metrics = {"accuracy", "precision", "recall", "f1_score"}

    def increment_cell(self, cell, incrementation=1):
        """
        Increment a cell in the confusion matrix.
        """
        observations = getattr(self, cell)
        observations += incrementation
        setattr(self, cell, observations)

    @property
    def accuracy(self):
        """
        What's the proportion of correctly classified results (both positive and negative)?
        """
        return (self.tp + self.tn) / (self.tp + self.tn + self.fp + self.fn + self.epsilon)

    @property
    def precision(self):
        """
        How many of the selected items are relevant?
        """
        return self.tp / (self.tp + self.fp + self.epsilon)

    @property
    def recall(self):
        """
        How many relevant items are selected?
        """
        return self.tp / (self.tp + self.fn + self.epsilon)

    @property
    def f1_score(self):
        """
        Harmonic mean of precision and recall.
        """
        return (2 * self.precision * self.recall) / (self.precision + self.recall + self.epsilon)

    def prettyprint(self, header=""):
        """
        Print all information in a confusion matrix to the terminal (including the value of various evaluation metrics).
        """
        if header:
            print("{:>40}".format(header))
            print("{:>40}\n".format(len(header)*"-"))

        self._print_confusion_matrix()
        self._print_metrics()

    def _print_metrics(self):
        metric_format = "{:>34}: {:.2f}"

        for metric in self.defined_metrics:
            print(metric_format.format(metric.title(), getattr(self, metric)))
        print("")

    def _print_confusion_matrix(self):
        row_format = "{:>10}" * 4

        # Print table
        print("{:>40}\n".format("Gold standard"))
        print(row_format.format("", "", "Positive", "Negative"))
        print(row_format.format("System", "True", self.tp, self.tn))
        print(row_format.format("", "False", self.fp, self.fn))
        print("")


class RelationExtractionConfusionMatrix(ConfusionMatrix):
    """
    Confusion matrix for relations extraction. It's hard to follow the TP / TN / FP / FN procedure here, so some of the
    evaluation metrics will be redefined.
    """
    def __init__(self):
        super().__init__()

        self.correct = 0
        self.extractions = 0
        self.relations = 0
        self.defined_metrics.remove("accuracy")  # TN are not defined for this task (you can't count non-relations)

    @property
    def precision(self):
        return self.correct / (self.extractions + self.epsilon)

    @property
    def recall(self):
        return self.correct / (self.relations + self.epsilon)

    def _print_confusion_matrix(self):
        row_format = "{:>20}" * 2

        # Print table
        print(row_format.format("", "Relations"))
        print(row_format.format("Correct", self.correct))
        print(row_format.format("Extracted", self.extractions))
        print(row_format.format("Relations", self.relations))
        print("")


class Relation:
    """
    Relation classed used in RelationsEvaluator. Useful to compare relations and check for equality.
    """
    subject = None
    verb = None
    object = None
    equality = "strict"
    possible_equalities = {
        "strict",  # All parts of the relation have to match exactly
        "disjunctive",  # At least one of the parts has to match exactly
        "strict_substring",  # All of the of the parts have to be at least substrings
        "substring_disjunctive"  # At least of the parts has to be a substring
    }

    def __init__(self, *args, **kwargs):
        if "equality" in kwargs:
            custom_equality = kwargs["equality"]
            if custom_equality not in self.possible_equalities:
                raise NotImplementedError(
                    "'{}' isn't a defined equality for this class. Did you maybe mean {}?".format(
                        custom_equality, " / ".join(list(self.possible_equalities))
                    )
                )

            self.equality = custom_equality

        if len(args) == 3:
            self.subject = args[0]
            self.verb = args[1]
            self.object = args[2]

        elif "subject_phrase" in kwargs and "verb" in kwargs and "object_phrase" in kwargs:
            self.subject = kwargs["subject_phrase"]
            self.verb = kwargs["verb"]
            self.object = kwargs["object_phrase"]

        else:
            raise AssertionError("Initialization for Relation class failed")

    def __eq__(self, other):
        equality_functions = {
            "strict": self._strict,
            "disjunctive": self._disjunctive,
            "strict_substring": self._strict_substring,
            "substring_disjunctive": self._substring_disjunctive
        }

        if not isinstance(other, Relation):
            raise AssertionError("You can only compare a Relation to another Relation.")

        return equality_functions[self.equality](self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    # TODO (Feature): Make this a command line parameter [DU 18.04.17]
    @staticmethod
    def _strict(relation1, relation2):
        return (
            relation1.subject == relation1.subject and
            relation1.verb == relation2.verb and
            relation1.object == relation2.object
        )

    @staticmethod
    def _disjunctive(relation1, relation2):
        return (
            relation1.subject == relation2.subject or
            relation1.verb == relation2.verb or
            relation1.object == relation2.object
        )

    @staticmethod
    def _strict_substring(relation1, relation2):
        return (
            (relation1.subject in relation2.subject or relation2.subject in relation1.subject) and
            (relation1.verb in relation2.verb or relation2.verb in relation1.verb) and
            (relation1.object in relation2.object or relation2.object in relation1.object)
        )

    @staticmethod
    def _substring_disjunctive(relation1, relation2):
        return (
            (relation1.subject in relation2.subject or relation2.subject in relation1.subject) or
            (relation1.verb in relation2.verb or relation2.verb in relation1.verb) or
            (relation1.object in relation2.object or relation2.object in relation1.object)
        )


def read_targets(corpus_inpath, target_opening_tag_pattern, target_closing_tag, target_class, target_variables,
                 extraction_function, corpus_encoding="utf-8", formatting_function=None):
    """
    Read articles from corpus.
    """
    targets = set()

    # Init "parsing" variables
    contents = []
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

            # Skip line if line is the title (title is already given in the <doc> tag)
            if "title" in target_variables:
                if line == target_variables["title"]:
                    continue

            # Identify xml/html comments
            if "<!--" in line:
                if "-->" not in line:
                    skip_line = True
                    comment = True
                continue

            # Identify beginning of new article
            if re.match(target_opening_tag_pattern, line):
                target_variables = extraction_function(line, target_opening_tag_pattern)

            # Identify end of article
            elif line.strip() == target_closing_tag:
                targets.add(target_class(**target_variables, contents=tuple(contents)))
                target_variables, contents = _reset_vars(target_variables)

            # Just add a new line to ongoing article
            else:
                if not line.strip():
                    continue

                # Apply additional formatting to line if an appropriate function is given
                formatted = None
                if formatting_function is not None:
                    formatted = formatting_function(line)

                # Add line
                if formatted is not None:
                    if is_collection(formatted):
                        for line_ in formatted:
                            contents.append(line_)
                    else:
                        contents.append(formatted)
                else:
                    contents.append(line)

    return targets


def _reset_vars(target_variables):
    """
    Reset variables for a new target.
    """
    reset_types = {
        str: "",
        list: [],
        dict: {},
        int: 0,
        float: 0.0,
        set: set()
    }

    return {
        key: reset_types[type(value)]
        for key, value in target_variables.items()
    }, []


def _extract_article_info(line, target_opening_tag_pattern):
    """
    Extract relevant dates from articles.
    """
    groups = re.match(target_opening_tag_pattern, line).groups()
    return {
        "id": groups[0],
        "url": groups[1],
        "title": groups[2]
    }


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


def read_articles_file(articles_inpath, corpus_encoding):
    """
    Read an article file from NLP pipeline.
    """
    tagged_articles = []

    with codecs.open(articles_inpath, "rb", corpus_encoding) as ne_file:
        for line in ne_file.readlines():
            deserialized_line = deserialize_line(line, corpus_encoding)
            tagged_articles.append(deserialized_line)

    return tagged_articles


def filter_tagged_articles(articles, tagged_articles):
    """
    Filter out those named entity tagged articles from the NLP pipeline which also appear in the evaluation set.
    """
    article_ids = set([article.id for article in articles])

    return [
        tagged_article
        for tagged_article in tagged_articles
        if tagged_article["meta"]["id"] in article_ids
    ]


def deserialize_line(line, encoding="utf-8"):
    """
    Transform a line in a file that was created as a result from a Luigi task into its metadata and main data.
    """
    return json.loads(line, encoding=encoding)


def get_sorted_dict_items(dictionary):
    return OrderedDict(sorted(dictionary.items())).items()


# ------------------------------------------ Argument parsing ----------------------------------------------------------

def _init_evalset_argument_parser():
    """
    Initialize the argument parser for the evaluation set creator.
    """
    argument_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    argument_parser.add_argument(
        "-ce", "--create-evalset",
        required=True,
        action='store_true',
        help="Flag that will create an evaluation set from an existing corpus (comprised of articles)."
    )
    argument_parser.add_argument(
        "-ni", "--ne-inpath",
        type=str,
        required=True,
        help="Input path to named entity tagged file from NLP-Pipeline (json)."
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
    argument_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

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


def _init_relations_eval_argument_parser():
    """
    Initialize the argument parser for the relation evaluator.
    """
    argument_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    argument_parser.add_argument(
        "-erl", "--eval-relations",
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
        "-ri", "--relations-inpath",
        type=str,
        required=True,
        help="Input path to relations file from NLP-Pipeline (json)."
    )
    argument_parser.add_argument(
        "-enc", "--corpus-encoding",
        type=str,
        default="utf-8",
        help="Encoding of input corpus."
    )
    argument_parser.add_argument(
        "-eq", "--equality",
        type=str,
        default="strict",
        choices=["strict", "disjunctive", "strict_substring", "substring_disjunctive"],
        help="Define the circumstances under which two relations are equal:\n\t"
        "strict: All parts of the relation have to match exactly\n\t"
        "disjunctive: At least one of the parts has to match exactly\n\t"
        "strict_substring: All of the of the parts have to be at least substrings\n\t"
        "substring_disjunctive: At least of the parts has to be a substring"
    )

    return argument_parser


def parse_and_start():
    flags_to_parser = {
        "-ce": _start_evalset_creator,
        "--create-evalset": _start_evalset_creator,
        "-ene": _start_ne_eval,
        "--eval-nes": _start_ne_eval,
        "-erl": _start_relations_eval,
        "--eval-relations": _start_relations_eval
    }

    for arg in sys.argv:
        if arg in flags_to_parser:
            return flags_to_parser[arg]()

    raise Exception(
        "No suitable command line arguments found for this script. Maybe you meant {}? (Use one of these plus -h flag "
        "for more help).".format(
            " / ".join(list(flags_to_parser.keys()))
        )
    )

# See main() at the top of the script.
if __name__ == "__main__":
    main()
