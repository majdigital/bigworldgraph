# -*- coding: utf-8 -*-
"""
Module for simple helper functions.
"""

# STD
import codecs
import functools
import sys
import time
import types
import os
import pickle

# EXT
import nltk


def filter_dict(dictionary, keep_fields):
    """
    Filter a dictionary's entries.
    
    :param dictionary: Dictionary that is going to be filtered.
    :type dictionary: dict
    :param keep_fields: Dictionary keys that aren't going to be filtered.
    :type keep_fields: dict or list or set
    :return: Filtered dictionary.
    :rtype: dict
    """
    return {
        key: value
        for key, value in dictionary.items()
        if key in keep_fields
    }


def construct_dict_from_source(fields, source):
    """
    Construct a new dict from a source dict and catch all KeyErrors, using predefined functions to extract desired 
    values from a source dictionary.
    
    :param fields: Dictionary with fields in the the target dict as keys and functions to extract their desired value .
        for these fields from the source dict
    :type fields: dict
    :param source: Source dictionary.
    :type source: dict
    :return: Target dictionary.
    :rtype: dict
    """
    new_dict = {}

    for field_name, getter_func in fields.items():
        try:
            new_dict[field_name] = getter_func(source)
        except KeyError:
            pass

    return new_dict


def get_config_from_py_file(config_path):
    """
    Load a configuration from a .py file.
    
    :param config_path: Path to configuration file.
    :type config_path: str
    :return: Configuration parameters as a dictionary.
    :rtype: dict
    """
    config = types.ModuleType('config')
    config.__file__ = config_path

    try:
        with codecs.open(config_path, "rb", "utf-8") as config_file:
            exec(compile(config_file.read(), config_path, 'exec'),
                 config.__dict__)
    except IOError:
        pass

    return {
        key: getattr(config, key) for key in dir(config) if key.isupper()
    }


def overwrite_local_config_with_environ(config):
    """
    Overwrite a local configuration file's parameters by environment variables, if they exist.

    :param config: Current configuration.
    :type config: dict
    :return: New configuration.
    :rtype: dict
    """
    return {
        key: (value if key not in os.environ else os.environ[key])
        for key, value in config.items()
    }


def flatten_dictlist(dictlist):
    """
    Turns a list of dictionaries into a single dictionary.
    
    :param dictlist: List of dictionaries.
    :type dictlist: list
    :return: Flattened dictionary.
    :rtype: dict

    :Example:
    
    >>> dictlist = [{"a": 1}, {"b": 2, "a": 3}, {"c": 4}]
    >>> flatten_dictlist(dictlist)
    {"a": 3, "b": 2, "c": 4}
    """
    new_dict = {}

    for dict_ in dictlist:
        new_dict.update(dict_)

    return new_dict


def download_nltk_resource_if_missing(resource_path, resource):
    """
    Download a missing resource from the Natural Language Processing Toolkit.
    
    :param resource_path: Link / path for NLTK resource.
    :type resource_path: str
    :param resource: Identifier / name of resource (will be used to download the resource if its not found).
    :type resource: str
    """
    try:
        nltk.data.find(resource_path)
    except LookupError:
        nltk.download(resource)


def is_collection(obj):
    """
    Check if an object is iterable collection.
    
    :param obj: Object that is to be checked.
    :type obj: object
    :return: Result of check.
    :rtype: bool
    """
    return hasattr(obj, '__iter__') and not isinstance(obj, str)


def seconds_to_hms(seconds):
    """
    Convert seconds to hours, minutes and seconds.
    
    :param seconds: Number of seconds to be converted.
    :type seconds: int, float
    :return: Number of seconds as hours, minutes and remaining seconds.
    :rtype: tuple
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return h, m, s


def time_function(out=sys.stdout, is_classmethod=False, return_time=False):
    """
    Time run time of a function and write to stdout or a log file. Also has some extra functions in case you want to
    apply it to a ArticleProcessingMixin.
    
    :param out: Output of choice. None will result in no output, sys.stdout to printing to terminal and a path to the 
        output being appended to a file.
    :type out: None, str, _io.TextIOWrapper
    :param is_classmethod: Declare the function being decorated a class method.
    :type is_classmethod: bool
    :param return_time: Flag to indicate whether the function's runtime should be returned alongside the decorated 
        function's return value in an dictionary.
    :return: Decorator function.
    :rtype: func
    
    :Example:
    
    >>> @time_function(return_time=True)
    >>> def test_func():
    >>>    return 3
    
    >>> test_func()
    {"return": 3, "runtime": 3.0994415283203125e-06}
    """
    def time_decorator(func):
        """
        Actual decorator.
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
            class_name = " of '{}' ".format(args[0].__class__.__name__) if is_classmethod else " "
            result = "Function '{}'{}took {:.2f} hour(s), {:.2f} minute(s) and {:.2f} second(s) to complete.\n".format(
                func.__name__, class_name, hours, minutes, seconds
            )

            # Write to stdout or file
            if out is not None:
                if type(out) == str:
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


def fast_copy(obj):
    """
    Create a fast copy of a object.

    :param obj: Object to be copied.
    :type obj: object
    :return: Copy.
    :rtype: object
    """
    return pickle.loads(pickle.dumps(obj, -1), encoding="utf-8")


def get_if_exists(dictionary, *keys, default=None):
    """
    Get a value from a nested dictionary without raising a ``KeyError``, but returning a default value instead.

    :param dictionary: Dictionary in question.
    :type dictionary: dict
    :param keys: Keys that lead to the desired value within the nested dictionary.
    :type keys: list
    :param default: Default value that should be returned instead of raising a ``KeyError``.
    :type default: None
    :return: Desired target value
    :rtype: None or other
    """
    value = default

    for key in keys:
        try:
            value = dictionary[key]
            # In case there's another key to be looked up
            dictionary = value
        except (KeyError, TypeError):
            return default

    return value
