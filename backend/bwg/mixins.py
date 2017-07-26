# -*- coding: utf-8 -*-
"""
Module for different mixins used for the NLP pipeline.
"""

# STD
import abc
import copy

# EXT
import luigi
import pycorenlp

# PROJECT
from bwg.utilities import serialize_article, just_dump, deserialize_line
from bwg.helpers import time_function, flatten_dictlist


class CoreNLPServerMixin:
    """
    Communicate with a Stanford CoreNLP server via the ``pycorenlp`` wrapper.
    """
    task_config = luigi.DictParameter()  # Dictionary with config parameters for all pipeline tasks
    _server = None

    def process_sentence_with_corenlp_server(self, sentence_data, action, postprocessing_func=None):
        """
        Annotate a sentence using a CoreNLP server.
        
        :param sentence_data: Sentence data to be processed.
        :type sentence_data: dict, list
        :param action: Action that should be performed on the data.
        :type action: str
        :param postprocessing_func: Function that is applied to output afterwards (None means that there won't be any 
            function applied to the output).
        :type postprocessing_func: func, None
        """
        language_abbreviation = self.task_config["LANGUAGE_ABBREVIATION"]
        properties = {
            "annotators": action,
            "outputFormat": "json",
            "tokenize.language": language_abbreviation,
            "lemma.language": language_abbreviation,
            "pipelineLanguage": language_abbreviation,
        }
        properties.update(self._corenlp_server_overriding_properties)

        result_json = self.server.annotate(
            sentence_data,
            properties=properties
        )

        if postprocessing_func is None:
            return result_json
        return postprocessing_func(result_json)

    @property
    def _corenlp_server_overriding_properties(self):
        """
        Define (e.g. language specific) properties for the annotation function of the CoreNLP server.
        """
        return {}

    @property
    def server(self):
        """
        Get an instance of the Stanford CoreNLP server.
        
        :return: Stanford CoreNLP server object.
        :rtype: pycorenlp.StanfordCoreNLP
        """
        if self._server is None:
            self._server = pycorenlp.StanfordCoreNLP(self.task_config["STANFORD_CORENLP_SERVER_ADDRESS"])
        return self._server


class ArticleProcessingMixin:
    """
    Enable Luigi tasks to process single lines as well as articles or other input types.
    
    ``Luigi`` tasks inheriting from this Mixin will work the following way:
    In ``run()`` you usually only define the inputs and outputs of the task and pass them along with some other 
    arguments to the main function, ``task_workflow()``:
    ::
    
        def run(self):
            with self.input()[0].open("r") as first_file, self.input()[1].open("r") as second_file:
                with self.output().open("w") as output_file:
                for line1, line2 in zip(first_file, second_file):
                    self.process_articles(
                        (line1, line2), new_state="done stuff",
                        serializing_function=serialize_output, output_file=output_file
                    )
                    
    whereby the ``new_state`` denotes a description of the current task which will be included in the results meta data
    and the ``serializing_function`` being the function used to transform the task's output into a form corresponding to 
    ``JSON``.
    
    Furthermore you can overwrite the ``workflow_resources`` property to initialize any resources before the task starts.

    In ``task_workflow``, you then define the core functionality of the task. This function gets called for every 
    article in the input and you then iterate trough every sentence in the article in the function. The expected output
    is a dictionary of key word arguments for the serializing function.
    
    You can overwrite ``is_relevant_article`` and ``is_relevant_sentence`` to only include specific tasks results in your
    output (this however only makes sense (for now) to do on your last tasks, as it might lead to misalignments of 
    inputs for following tasks). Make sure to also set ``ONLY_INCLUDE_RELEVANT_SENTENCES`` and 
    ``ONLY_INCLUDE_RELEVANT_ARTICLES`` to ``True`` in your pipeline's config file, correspondingly.
    """
    task_config = luigi.DictParameter()  # Dictionary with config parameters for all pipeline tasks

    @abc.abstractmethod
    def task_workflow(self, article, **workflow_kwargs):
        """
        Define the tasks workflow here - it usually includes extracting necessary resources from workflow_kwargs,
        performing the actual task on the sentence and wrapping all the arguments for the serializing function in a
        dictionary, returning it in the end.

        The input is considered an article, e.g. some text that consists of a variable number of sentences. Here's a
        proposal how to fit real world media types to this requirement:
        
        * Wikipedia article: Intuitive. If you want want to work with the articles subsection, treat them as small articles themselves.
        * Newspaper article: Same intuition as above.
        * Books: Treat chapters as articles.
        * Single paragraphs of text: Treat as articles that may not contain a headline.
        * Single sentence: Treat as single paragraph with only one "data" entry.
        * Pictures, tables, movies: Implement another workflow and also another Pipeline? This one is only for (written) natural language.
                                        
        :param article: Current article as a dictionary, with the "meta" field providing meta data and the "data" field
            providing the actual sentence data.
        :type article: dict
        :param workflow_kwargs: Additional key word arguments for this tasks workflow, e.g. additional resources.
        :type workflow_kwargs: dict
        :return: Yielding all named arguments to serialize this article after processing.
        :rtype: dict
        """
        # Do main work here, e.g. iterating through every sentence in an articles "data" dict, performing a specific
        # task.
        for sentence_id, sentence in article["data"]:
            # Do the https://www.youtube.com/watch?v=HL1UzIK-flA
            pass

            # Afterwards, put all the arguments for the corresponding serializing function into a dict and yield it.
            serializing_kwargs = {}

            yield serializing_kwargs

    @property
    def workflow_resources(self):
        """
        Property that provides resources necessary to complete the task's workflow.
        """
        # some_complicated_object = initialize_complicated_object(self.task_config["init_parameter"])

        workflow_resources = {
            # "complicated_object": some_complicated_object
        }

        return workflow_resources

    @time_function(out=None, return_time=True)
    def process_articles(self, raw_articles, new_state, serializing_function, output_file, pretty=False):
        """
        Process line from the input and apply this task's workflow. Serialize the result afterwards and finally write
        it to the output file.
        
        :param raw_articles: Raw articles (referring to the same article but carrying different kinds of data for their 
            sentences) read from input file.
        :type raw_articles: list, tuple
        :param new_state: State that describes the kind of processing that is applied to the data in this step. It's 
            included in the metadata of each article.
        :type new_state: str
        :param serializing_function: Function that is used afterwards to serialize the data again.
        :type serializing_function: func
        :param output_file: Output file the serialized results should be written to.
        :type output_file: _io.TextWrapper
        :param pretty: Flag to indicate whether the output should be pretty-printed.
        :type pretty: bool
        """
        debug = self.task_config.get("PIPELINE_DEBUG", False)
        article = self._combine_articles(raw_articles)
        sentences = []

        # Main processing
        if debug:
            print("{} processing article '{}'...".format(self.__class__.__name__, article["meta"]["title"]))

        for serializing_kwargs in self.task_workflow(article, **self.workflow_resources):
            if debug:
                print("{} finished sentence #{}.".format(self.__class__.__name__, serializing_kwargs["sentence_id"]))

            serialized_sentence = serializing_function(state=new_state, dump=False, **serializing_kwargs)

            if self.is_relevant_sentence(serialized_sentence):
                sentences.append(serialized_sentence)

        sentences = flatten_dictlist(sentences)
        meta = article["meta"]
        article_id, article_url, article_title = meta["id"], meta["url"], meta["title"]
        serialized_article = serialize_article(
            article_id, article_url, article_title, sentences, state=new_state, from_scratch=False, dump=False,
            pretty=pretty
        )

        # Output
        if self.is_relevant_article(serialized_article):
            output_file.write("{}\n".format(just_dump(serialized_article, pretty=pretty)))

    def _combine_articles(self, raw_articles):
        """
        Combine multiple articles into one data structure, if necessary.
        
        :param raw_articles: Raw articles (referring to the same article but carrying different kinds of data for their 
            sentences) read from input file.
        :type raw_articles: list
        :return: New article with combined data.
        :rtype: dict
        
        :Example:
        
        >>> article1 = {
        ...     "meta": {
        ...         "id": "0001",
        ...         "type:": "article",
        ...         "state": "pos_tagged",
        ...         ...
        ...     },
        ...     "data": {
        ...         "0001/0001": {
        ...         "meta": {...},
        ...         "data": {...}
        ...     },
        ...     ...
        ...     }
        ... }
        >>> article2 = {
        ...     "meta": {
        ...         "id": "0001",
        ...         "type": "article",
        ...         "state": "dependency_parsed",
        ...         ...
        ...     },
        ...     "data": {...}
        ... }
        >>> _combine_articles([article1, article2])
        ... {
        ...     "meta": {
        ...         "id": "0001",
        ...         "type": "article",
        ...         "state": "pos_tagged | dependency_parsed",
        ...         ...
        ...     },
        ...     "data": {
        ...         "0001/0001": {
        ...             "meta": {...},
        ...             "data": {
        ...                 "data_pos_tagged": {...},
        ...                 "data_dependency_parsed": {...}
        ...             }
        ...         },
        ...         ...
        ...         }
        ... }
        """
        corpus_encoding = self.task_config["CORPUS_ENCODING"]

        # Standardize input
        if type(raw_articles) == str:
            raw_articles = (raw_articles, )

        if len(raw_articles) == 0:
            raise AssertionError("No input detected.")

        elif len(raw_articles) == 1:
            return deserialize_line(raw_articles[0], corpus_encoding)

        else:
            # Multiple versions of an article detected (for example all sentences of an article PoS tagged, NE tagged,
            # dependency parsed)- merge them!

            # Get articles as json
            article_jsons = [deserialize_line(raw_article, corpus_encoding) for raw_article in raw_articles]

            # Check integrity of inputs
            article_ids = [article_json["meta"]["id"] for article_json in article_jsons]
            article_types = [article_json["meta"]["type"] for article_json in article_jsons]

            if len(set(article_ids)) != 1 or len(set(article_types)) != 1:
                raise AssertionError(
                    "Combining input objects requires them to have the same id and same type: {} and {} found.".format(
                        ", ".join(article_ids), ", ".join(article_types)
                    )
                )

            # Combine inputs
            sample_article = copy.deepcopy(article_jsons[0])
            # Combine meta dates
            new_article = dict(meta=sample_article["meta"])
            new_article["meta"]["state"] = " | ".join(
                [article_json["meta"]["state"] for article_json in article_jsons]
            )

            # Combine dates
            new_article["data"] = {}
            for sentence_id, sentence_json in sample_article["data"].items():
                sentence_meta = sentence_json["meta"]
                sentence_meta["state"] = " | ".join(
                    [article_json["meta"]["state"] for article_json in article_jsons]
                )

                new_article["data"].update(
                    {
                        sentence_id: {
                            "meta": sentence_meta,
                            "data": {
                                "data_{}".format(article_json["meta"]["state"]): article_json["data"][sentence_id]
                                for article_json in article_jsons
                            }
                        }
                    }
                )

            return new_article

    def is_relevant_article(self, article):
        """
        Filter articles in the output by a relevance criterion that subclasses can define in this function.

        All articles are relevant if the flag is not set; only relevant ones are relevant if the flag is set (duh).
        
        :param article: Article.
        :type article: dict
        :return: Result of check.
        :rtype: bool
        """
        relevance_flag_set = self.task_config.get("ONLY_INCLUDE_RELEVANT_ARTICLES", False)
        return not relevance_flag_set or self._is_relevant_article(article)

    def is_relevant_sentence(self, sentence):
        """
        Filter sentences of an article in the output by a relevance criterion that subclasses can define in this
        function.

        All sentences are relevant if the flag is not set; only relevant ones are relevant if the flag is set (duh).
        
        :param sentence: Sentence
        :type sentence: list or dict
        :return: Result of check.
        :rtype: bool
        """
        relevance_flag_set = self.task_config.get("ONLY_INCLUDE_RELEVANT_SENTENCES", False)
        return not relevance_flag_set or self._is_relevant_sentence(sentence)

    def _is_relevant_article(self, article):
        """
        Filter articles in the output by a relevance criterion that subclasses can define in this function.
        
        :param article: Article.
        :type article: dict
        :return: Result of check.
        :rtype: bool
        """
        return True

    def _is_relevant_sentence(self, sentence):
        """
        Filter sentences of an article in the output by a relevance criterion that subclasses can define in this
        function.
        
        :param sentence: Sentence
        :type sentence: list or dict
        :return: Result of check.
        :rtype: bool
        """
        return True
