bwg.corenlp_server_tasks
========================

Using ``CoreNLP Server`` tasks
------------------------------

To use ``CoreNLP Server`` tasks, appropriate `Stanford
NLP <https://stanfordnlp.github.io/CoreNLP/download.html>`__ models are
also required. For french, those are downloaded from a MAJ // Digital server when ``docker-compose.yml`` is called.

In case you are running the project on a non-french corpus, you can adjust the command that runs the server in its
corresponding dockerfile at ``backend/data/stanford/Dockerfile`` to fit the current language. Do this by adjusting the
``-serverProperties`` argument appropriately (consult the  `official documentation <https://stanfordnlp.github.io/CoreNLP/corenlp-server.html>`__
for more help).

Module contents
---------------

.. automodule:: bwg.corenlp_server_tasks
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: output, requires, run, task_workflow, task_config, workflow_resources
