# -*- coding: utf-8 -*-
"""
Version info.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

__versioninfo__ = (0, 9, 0)
__version__ = '.'.join([str(num) for num in __versioninfo__])
