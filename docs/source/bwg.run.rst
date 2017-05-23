bwg.run
=======

Usage
-----

This module contains the API. To run the API, just run this module:
::

   python3 bwg/run.py

Features
--------

So far, you can use the API to do the following things:

Get the current version of the API by using the ``/version/` endpoint:
::

   curl -gX GET http://127.0.0.1:5000/version/

will return
::

   {"version": "0.7.0", "license": "Copyright (c) 2017 Malabaristalicious Unipessoal, Lda.\nFor more information read LICENSE.md on https://github.com/majdigital/bigworldgraph"}

You can also query for entities and their relationships in the database using the ``/entities/`` endpoints
(not recommended because the result will probably be very big):
::

    curl -gX GET http://127.0.0.1:5000/entities/

which returns
::

   {"_items": [{"nodes": [{"uid": "42904ca7f582449eafb98c1e94cd8b0d", "category": "Person", "label": "Dreyfus", "data": {"wikidata_last_modified": "2015-12-31T03:11:20Z", "wikidata_id": "Q3039421", "label": "Dreyfus", "description": "pi\u00e8ce de th\u00e9\u00e2tre de Jean-Claude Grumberg", "type": "I-PER", "claims": {}}, "id": 0}, ...}

To be more specific, you can query special kinds of entities like ``/people/``, ``/locations/``, ``/organizations/`` or
``/misc/``.

To make responses more readable for humans, use the ``?pretty`` query parameter:
::

    curl -gX GET http://127.0.0.1:5000/people?pretty

which in turn returns
::

   {
       "_items": [
           {
               "nodes": [
                  {
                     "uid": "42904ca7f582449eafb98c1e94cd8b0d",
                     "category": "Person",
                     "label": "Dreyfus",
                     "data": {
                        "wikidata_last_modified": "2015-12-31T03:11:20Z",
                        "wikidata_id": "Q3039421",
                        "label": "Dreyfus",
                        "description": "pi\u00e8ce de th\u00e9\u00e2tre de Jean-Claude Grumberg",
                        "type": "I-PER",
                        "claims": {}
                     },
                     "id": 0
                  },
                  ...
               ],
               "links": [
                  ...
               ]
           }
       ],
       ...
   }

.. WARNING::
   As of version 0.7.0, ``BigWorldGraph`` only comprises the following query parameters:
      * ``?pretty``
      * Filtering like ``/entities?uid=42904ca7f582449eafb98c1e94cd8b0d``

   Any other functionalities presented by ``Eve`` in `its documentation <http://python-eve.org/features.html>`__ are not
   implemented yet.

To only get a subset of a graph, specify an identifier in for the target node in the request:
::

   curl -gX GET http://127.0.0.1:5000/people?uid=42904ca7f582449eafb98c1e94cd8b0d

This will return the target node as well as its **friends** and its **friends of friends**.


Module contents
---------------

.. automodule:: bwg.run
   :members:
   :undoc-members:
   :show-inheritance:
