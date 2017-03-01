# -*- coding: utf-8 -*-
"""
Module for simple helper functions.
"""

# STD
import types


def filter_dict(dictionary, keep_fields):
    """
    Filter a dictionary's entries.
    """
    return {
        key: value
        for key, value in dictionary.items()
        if key in keep_fields
    }


def get_config_from_py_file(config_path):
    """
    Load a configuration from a .py file.
    """
    config = types.ModuleType('config')
    config.__file__ = config_path
    try:
        with open(config_path) as config_file:
            exec(compile(config_file.read(), config_path, 'exec'),
                 config.__dict__)
    except IOError:
        pass
    return {
        key: getattr(config, key) for key in dir(config) if key.isupper()
    }
