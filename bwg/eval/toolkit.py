# -*- coding: utf-8 -*-
"""
Module with different tools that help the user to evaluate results produced by the NLP pipeline, e.g. by creating
a custom evaluation set.
"""

# STD
import argparse


def main():
    """
    Main function. This script is intended to be run from the command line.
    """
    argument_parser = initialize_argument_parser()
    args = argument_parser.parse_args()


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
    def __init__(self, corpus_inpath, **creation_kwargs):
        pass


def initialize_argument_parser():
    argument_parser = argparse.ArgumentParser()

    # TODO (Feature): Implement appropriate command line argument

    return argument_parser


# See main() at the top of the script.
if __name__ == "__main__":
    pass
