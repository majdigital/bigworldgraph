bwg.demo.demo_pipeline
======================

This module illustrates how pipelines in the context of this project are used. For this purpose, the pipeline in this
module comprises three very simple tasks:

* ``DemoTask1`` simply replaces characters defined in ``demo_pipeline_config.py`` with "x".
* ``DemoTask2`` duplicates characters defined in ``demo_pipeline_config.py``.
* ``DemoTask3`` removes characters defined in ``demo_pipeline_config.py``.

Therefore, the original corpus, that should look like this (see ``data/corpora_demo/demo_corpus.xml``):
::

   <doc id="12345" url="https://github.com/majdigital/bigworldgraph" title="Demo corpus">
   Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
   Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
   Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
   Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

   </doc>

Should result in ``data/pipeline_demo/demo_corpus_removed.json`` looking like this
::

   {
       "meta": {
           "id": "12345",
           "url": "https://github.com/majdigital/bigworldgraph",
           "title": "Demo corpus",
           "type": "article",
           "state": "removed"
       },
       "data": {
           "12345/00001": {
               "meta": {
                   "id": "12345/00001",
                   "state": "removed",
                   "type": "sentence"
               },
               "data": "Looex isux doooo sit xxet, coonnsectetu xdiiscinng eit, sed doo eiusxood texoo inncididunnt ut xbbooe et dooooe xxgnnx xiqux."
           },
           "12345/00002": {
               "meta": {
                   "id": "12345/00002",
                   "state": "removed",
                   "type": "sentence"
               },
               "data": "Ut ennix xd xinnix vennixx, quis nnoostud execitxtioonn uxxcoo xbboois nnisi ut xiqui ex ex cooxxoodoo coonnsequxt."
           },
           "12345/00003": {
               "meta": {
                   "id": "12345/00003",
                   "state": "removed",
                   "type": "sentence"
               },
               "data": "Duis xute iue doooo inn eehenndeit inn vooutxte veit esse ciux dooooe eu fugixt nnux xixtu."
           },
           "12345/00004": {
               "meta": {
                   "id": "12345/00004",
                   "state": "removed",
                   "type": "sentence"
               },
               "data": "Exceteu sinnt ooccxecxt cuidxtxt nnoonn ooidennt, sunnt inn cux qui oofficix deseunnt xooit xnnix id est xbbooux."
           }
       }
   }

The pipeline is simply run by running the module:
::

      python3 bwg/demo/demo_pipeline.py

Adjusting your pipeline configuration
-------------------------------------

If you add a new kind of task to the pipeline, make sure to include a
description of its necessary parameters in your pipeline configuration
file. You can use ``bwg/raw_pipeline_config.py`` as a template, which
provides a minimal example.

::

    CONFIG_DEPENDENCIES = {
        ...
        # Your task
        "my_new_task": [
             "{language}_SPECIFIC_PARAMETER",
             "LANGUAGE_INDEPENDENT_PARAMETER"
        ],
        ...
    }

Then you have to include those declared parameters somewhere in your
config file:

::

    # My config parameters
    ENGLISH_SPECIFIC_PARAMETER = 42
    LANGUAGE_INDPENENDENT_PARAMETER = "yada yada"

If you implement tasks that extend the pipeline to support other
language, please add it to the following list:

::

    SUPPORTED_LANGUAGES = ["FRENCH", "ENGLISH"]

Finally, create a module for your own pipeline (e.g.
``bwg/my_pipeline.py``) and build the configuration before running the
pipeline, using the pre-defined task names in your pipeline file:
::

    import luigi
    from bwg.nlp.config_management import build_task_config_for_language

    class MyNewTask(luigi.Task):
        def requires():
            # Define task input here

        def output():
            # Define task output here

        def run():
            # Define what to do during the task here


    if __name__ == "__main__":
        task_config = build_task_config_for_language(
            tasks=[
                "my_new_task"
            ],
            language="english",
            config_file_path="path/to/pipeline_config.py"
        )

        # MyNewTask is the last task of the pipeline
        luigi.build(
            [MyNewTask(task_config=task_config)],
            local_scheduler=True, workers=1, log_level="INFO"
        )

Module contents
---------------

.. automodule:: bwg.demo.demo_pipeline
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: output, requires, run, task_workflow, task_config, workflow_resources
