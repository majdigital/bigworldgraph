# -*- coding: utf-8 -*-
"""
Create support for MongoDB.
"""

# EXT
import luigi


class MongoDBTarget(luigi.Target):
    """
    Additional luigi target to write a task's output into a MongoDB.
    """

    def exists(self):
        # TODO (Implement) [DU 19.04.17]
        pass
