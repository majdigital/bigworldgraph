# -*- coding: utf-8 -*-
"""
Version info.
"""
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

__versioninfo__ = (0, 7, 0)
__version__ = '.'.join([str(num) for num in __versioninfo__])
