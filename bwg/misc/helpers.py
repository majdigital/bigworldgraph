# -*- coding: utf-8 -*-
"""
Module for simple helper functions.
"""


def filter_dict(dictionary, keep_fields):
    """
    Filter a dictionary's entries.
    """
    return {
        key: value
        for key, value in dictionary.items()
        if key in keep_fields
    }
