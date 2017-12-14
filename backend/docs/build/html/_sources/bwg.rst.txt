Main project contents
=====================

The project contains the following modules:

* `bwg.config_management`: Functions used to create the configuration for the pipeline.
* `bwg.corenlp_server_tasks`: NLP pipeline tasks that use the ``Stanford CoreNLP Server``.
* `bwg.helpers`: Helper functions used throughout the project.
* `bwg.mixins`: Mixin classes used in the projects.
* `neo4j_extensions`: Extensions to the ``Neo4j`` database, to make it compatible to ``Luigi`` and ``Eve``.
* `bwg.utilities`: Mostly serializing functions used in pipeline tasks.
* `bwg.wikidata_mixins`: Wrappers for Wikidata, using ``pywikibot``.

It also includes the following packages with their own modules:

* `bwg.api`
    * `bwg.api.run_api`: Module used to run the API.
* `bwg.demo`
    * `bwg.demo.demo_pipeline.py`: Simple example pipeline to process a minimal corpus.
* `bwg.french_wikipedia`
    * `bwg.french_wikipedia.rench_wikipedia_pipeline`: Example pipeline tasks to specifically process the french wikipedia.
* `bwg.tasks`
    * `bwg.tasks.corenlp_server_tasks.py`: Extending NLP tasks using the `Stanford CoreNLP Server``.
    * `bwg.tasks.dependency_parsing.py`: Performing dependency parsing.
    * `bwg.tasks.naive_ore.py`: Performing a naive version of open relation extraction.
    * `bwg.tasks.ner.py`: Performing named entity recognition.
    * `bwg.tasks.participation_extraction.py`: Linking named entities in an article to its headline.
    * `bwg.tasks.pipeline_run_info_generation.py`: Generating information about the current run.
    * `bwg.tasks.pos_tagging.py`: Performing Part-of-Speech tagging.
    * `bwg.tasks.properties_completion.py`: Enriching named entities with information from Wikidata.
    * `bwg.tasks.reading_tasks.py`: Tasks in order to read in corpora.
    * `bwg.tasks.relation_merging.py`: Mergig extracted relations from various other tasks.
    * `bwg.tasks.relations_database_writing.py`: Writing relations into a ``Neo4j`` graph database.

