The Pipeline
============

This site is trying to help you explain how the pipeline in this project works and you can adjust it or even write
your own pipeline.


Writing your own pipeline tasks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to modify existing pipeline tasks or write new ones, it is
recommended to add a new module to the ``bwg`` package, see e.g.
``bwg/french_wikipedia.py`` as reference. You can inherit tasks from
other modules to solve common problems:

-  ``bwg/standard_tasks.py``: Standard NLP tasks like PoS tagging,
   Dependency Parsing etc.
-  ``bwg/corenlp_server_tasks.py``: Same standard NLP tasks, but using
   the ``Stanford CoreNLP server`` instead to speed up cumbersome and
   slow tasks.
-  ``bwg/wikipedia_tasks.py``: Reading an input file in the shallow
   ``MW-Dumper`` XML format; extracting addtional information from
   Wikidata.
-  ``bwg/additional_tasks.py``: Creating a file with information about
   the current pipeline run, writing relationships into a graph database
   and more.

With its standard configuration, the pipeline comprises the following
tasks:

.. figure:: ./img/flowchart.png
   :alt:

Adjusting your pipeline configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Running the pipeline
~~~~~~~~~~~~~~~~~~~~

If you're sticking to the *Docker* setup, complete the following steps to run the pipeline:

::

    docker-compose build && docker-compose up

The building of the docker images in this project might take a while,
especially during the first time you're using this project. After all
containers are running, you can run the pipeline by executing the
following:

::

    cd ./pipeline/
    docker build . -t pipeline
    docker run -v /var/run/docker.sock:/var/run/docker.sock -v `pwd`/stanford/models/:/stanford_models/ --name pipeline pipeline

If you are on a Windows system, replace ``pwd`` inside the ``-v`` flag
with the **absolute** path to the ``stanford/models`` directory.
Afterwards, you can make requests to the API using port ``6050`` by
default (see the documentation for ``bwg/run_api.py`` for more
information).

In case you're running it without *Docker*, just run the the *Python* script containing *Luigi*'s `luigi.build()` function:

::

    python3 /path/to/pipeline/my_pipeline.py

Make sure to have other dependencies running in the background while doing this (e.g. a database to write the final results
into).