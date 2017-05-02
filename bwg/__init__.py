# -*- coding: utf-8 -*-
"""
Version info.
"""
import sys
import os

PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import sys
from pathlib import Path # if you haven't already done so
root = str(Path(__file__).resolve().parents[1])
# Or
#   from os.path import dirname, abspath
#   root = dirname(dirname(abspath(__file__)))
sys.path.append(root)

__versioninfo__ = (0, 6, 0)
__version__ = '.'.join([str(num) for num in __versioninfo__])

# TODO (Improve): Include demo pipeline [DU 02.05.17]
