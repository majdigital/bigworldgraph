bwg.neo4j_extensions
====================

Motivation
----------

This module was created for several reasons: First of all, :class:`~bwg.neo4j_extensions.Neo4jDatabase` was created to
provide a tailored wrapper to a ``Neo4j`` database with extended and only relevant functionalities, including
:class:`~bwg.neo4j_extensions.Entity` and :class:`~bwg.Relation`.

Other classes like :class:`~bwg.neo4j_extensions.EveCompabilityMixin`, :class:`~bwg.neo4j_extensions.Neo4jLayer`,
:class:`~bwg.neo4j_extensions.Neo4jLayer` were written to make the database work with the ``RESTful API``
`Eve <http://python-eve.org>`_. Although there is a library already bridging this gap, which is called
`eve-neo4j <https://github.com/Abraxas-Biosystems/eve-neo4j>`__, it was causing problems, namely
`this one <https://github.com/Abraxas-Biosystems/eve-neo4j/issues/19>`__. No viable solution could be found, thereby
these classes were created.

Finally, ``Luigi`` defines an interface for possible task targets (= output destinations). To write data directly into
a database within a ``Luigi`` task, :class:`~bwg.neo4j_extensions.Neo4jTarget` was created.

Module contents
---------------

.. automodule:: bwg.neo4j_extensions
   :members:
   :undoc-members:
   :show-inheritance:
