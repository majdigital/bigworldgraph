bwg.corenlp_server_tasks
========================

Using ``CoreNLP Server`` tasks
------------------------------

To use ``CoreNLP Server`` tasks, appropriate `Stanford
NLP <https://stanfordnlp.github.io/CoreNLP/download.html>`__ models are
also required. Before running the pipeline, also make sure to run the
``StanfordCoreNLP`` server in case you are using a task from the module
``nlp/corenlp_server_tasks.py``, using the following command in the
directory with the appropriate Stanford models (in this case the
``-serverProperties`` argument is used to tell the Server the language
of incoming texts):

::

    java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000 -serverProperties StanfordCoreNLP-french.properties

For more information about the server itself, please consult the `official documentation <https://stanfordnlp.github.io/CoreNLP/corenlp-server.html>`__.

Finally, you also have to include at least this config parameter in your pipeline config file:

::

    STANFORD_CORENLP_SERVER_ADDRESS = "http://localhost:9000"



Module contents
---------------

.. automodule:: bwg.corenlp_server_tasks
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: output, requires, run, task_workflow, task_config, workflow_resources
