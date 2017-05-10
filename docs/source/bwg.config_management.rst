bwg.config_management
=====================

Creating your own pipeline configuration
----------------------------------------

Every pipeline requires a configuration file with certain parameters. It contains two parts:

1. A kind of "meta" configuration, specifying the parameters a task requires. This way is it secured that the pipeline
   is run with all necessary configuration parameters. Otherwise a special exception is thrown. Its is stored in a single
   parameter, called ``CONFIG_DEPENDENCIES``.
2. The "real" configuration, just how you know it - config parameters and their corresponding values.

If you add a new kind of task to the pipeline, make sure to include a
description of its necessary parameters in your config file's (e.g. ``my_pipeline_config.py``) meta config:

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
``my_pipeline.py``) and build the configuration before running the
pipeline, using the pre-defined task names in ``my_pipeline_config.py``:

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
            config_file_path="path/to/my_pipeline_config.py"
        )

        # MyNewTask is the last task of the pipeline
        luigi.build(
            [MyNewTask(task_config=task_config)],
            local_scheduler=True, workers=1, los


In case you are writing the data into a ``Neo4j`` database, make sure to
include the following parameters

::

    # Neo4j
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "neo4j"
    NEO4J_NETAG2MODEL = {
        "I-PER": "Person",
        "I-LOC": "Location",
        "I-ORG": "Organization",
        "DATE": "Date",
        "I-MISC": "Miscellaneous"
    }


Module contents
---------------

.. automodule:: bwg.config_management
   :members:
   :undoc-members:
   :show-inheritance:
