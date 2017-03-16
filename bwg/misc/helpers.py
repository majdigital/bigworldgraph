# -*- coding: utf-8 -*-
"""
Module for simple helper functions.
"""

# STD
import codecs
import functools
import nltk
import sys
import time
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


def flatten_dictlist(dictlist):
    """
    Turns a list of dictionaries into a single dictionary.

    Example:
        [{"a": 1}, {"b": 2, "a": 3}, {"c": 4}] -> {"a": 3, "b": 2, "c": 4}
    """
    new_dict = {}

    for dict_ in dictlist:
        new_dict.update(dict_)

    return new_dict


def download_nltk_resource_if_missing(resource_path, resource):
    """
    Download a missing resource from the Natural Language Processing Toolkit.
    """
    try:
        nltk.data.find(resource_path)
    except LookupError:
        nltk.download(resource)


def is_collection(obj):
    """
    Check if a object is iterable.
    """
    return hasattr(obj, '__iter__') and not isinstance(obj, str)


def seconds_to_hms(seconds):
    """
    Convert seconds to hours, minutes and seconds.
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return h, m, s


def time_function(out=sys.stdout, is_classmethod=False, return_time=False, give_report=False):
    """
    Time run time of a function and write to stdout or a log file. Also has some extra functions in case you want to
    apply it to a ArticleProcessingMixin.
    """
    def time_decorator(func):
        """
        Actual decorator
        """
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            # Measure run time
            start_time = time.time()
            function_result = func(*args, **kwargs)
            end_time = time.time()

            # Calculate result and write it
            run_time = end_time - start_time
            hours, minutes, seconds = seconds_to_hms(run_time)
            class_name = " of '{}' ".format(args[0].__class__.__name__) if is_classmethod else ""
            result = "Function '{}'{}took {:.2f} hour(s), {:.2f} minute(s) and {:.2f} second(s) to complete.\n".format(
                func.__name__, class_name, hours, minutes, seconds
            )

            # Write to stdout or file
            if out is not None:
                if out != sys.stdout:
                    with codecs.open(out, "a", "utf-8") as outfile:
                        outfile.write(result)
                else:
                    out.write(result)

            # Add run time to function return value
            if return_time:
                return {
                    "return": function_result,
                    "runtime": run_time
                }

            return function_result

        return func_wrapper

    return time_decorator
