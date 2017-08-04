# -*- coding: utf-8 -*-
"""
Module that includes multipe helpful decorator functions.
"""

# STD
import codecs
import functools
import random
import sys
import time

# PROJECT
from bwg.helpers import seconds_to_hms


def retry_on_condition(exception_class, condition=lambda: True, max_retries=-1):
    """
    Retry a function in case an exception occurs. You can also define an additional condition that has to be met as
    well as a maximum amount of retries.

    :param exception_class: Exception class that triggers the retry.
    :type exception_class: Exception
    :param condition: Additional condition that has to be met.
    :type: func
    :param max_retries: Maximum amount of retries, -1 means infinite retries.
    """
    def decorator(func):
        """
        Actual decorator.
        """
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            assert callable(condition)
            assert issubclass(exception_class, Exception)

            if condition:
                retries = 0
                last_exception = None

                while retries < max_retries:
                    retries += 1
                    try:
                        return func(*args, **kwargs)
                    except exception_class as exception:
                        last_exception = exception
                    time.sleep(random.randint(0, 25) / 10)

                raise last_exception
            else:
                return func(*args, **kwargs)

        return func_wrapper
    return decorator


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