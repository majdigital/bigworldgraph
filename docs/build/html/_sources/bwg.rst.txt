Main project contents
=====================

The project contains the following modules:

* `bwg.additional_tasks`: Tasks that can be helpful to include in the pipeline, but are not obligatory.
* `bwg.config_management`: Functions used to create the configuration for the pipeline.
* `bwg.corenlp_server_tasks`: NLP pipeline tasks that use the `Stanford CoreNLP Server``.
* `bwg.french_wikipedia`: Example pipeline tasks to specifically process the french wikipedia.
* `bwg.helpers`: Helper functions used throughout the project.
* `bwg.mixins`: Mixin classes used in the projects.
* `neo4j_extensions`: Extensions to the ``Neo4j`` database, to make it compatible to ``Luigi`` and ``Eve``.
* `bwg.standard_tasks`: Standard tasks often uses in pipelines.
* `bwg.utilities`: Mostly serializing functions used in pipeline tasks.
* `bwg.wikidata`: Wrappers for Wikidata, using ``pywikibot``.
* `bwg.wikipedia_tasks`: Tasks involving the Wikidata or processing a Wikipedia corpus.
* `bwg.run`: Module used to run the API.
* `bwg.demo_pipeline.py`: Simple example pipeline to process a minimal corpus.

Modules
-------

.. toctree::

    bwg.additional_tasks
    bwg.config_management
    bwg.corenlp_server_tasks
    bwg.demo_pipeline
    bwg.french_wikipedia
    bwg.helpers
    bwg.mixins
    bwg.neo4j_extensions
    bwg.run
    bwg.standard_tasks
    bwg.utilities
    bwg.wikidata
    bwg.wikipedia_tasks
