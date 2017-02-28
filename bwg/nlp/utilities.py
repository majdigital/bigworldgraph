# -*- coding: utf-8 -*-
"""
Utilities for the NLP pipeline.
"""

# EXT
import luigi


class NamedEntityTarget(luigi.Target):
	"""
	Special target for Named Entity tagged sentences.
	"""
	pass


class DependencyParseTarget(luigi.Target):
	pass




