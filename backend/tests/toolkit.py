# -*- coding: utf-8 -*-
"""
Helper functions for testing.
"""

# STD
import copy
import functools
import json
import time
import random


class MockInput:
    """
    Class to mock an input file.
    """
    def __init__(self, contents=[]):
        self.contents = contents
        self.pointer = 0

    def open(self, mode):
        assert mode in ("r", "rb")
        return self

    def read(self):
        if self.pointer == len(self.contents):
            return None

        read_item = self.contents[self.pointer]
        self.pointer += 1
        return read_item

    def readlines(self):
        return self.__iter__()

    def __iter__(self):
        return (line for line in self.contents)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockOutput:
    """
    Class to mock an output file.
    """
    is_tmp = True

    def __init__(self):
        self.contents = []

    def open(self, mode):
        assert mode in ("w", "wb")
        return self

    def write(self, line):
        self.contents.append(line)

    @staticmethod
    def exists():
        return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def make_api_request(app, request_type, endpoint, content={}, headers={},
                     **kwargs):
    request_type = request_type.lower()
    headers.update({'Content-Type': 'application/json; charset=utf-8'})
    content = json.dumps(content)

    return getattr(app, request_type)(
        endpoint, data=content, headers=headers, **kwargs
    )


class mock_class_method:
    def __init__(self, cls, method_name, new_method):
        self.original_class = cls
        self.method_name = method_name
        self.original_method = getattr(cls, method_name)
        patched_class = copy.deepcopy(cls)
        setattr(patched_class, method_name, new_method)
        self.patched_class = patched_class

    def __enter__(self):
        return self.patched_class

    def __exit__(self, exc_type, exc_val, exc_tb):
        setattr(self.original_class, self.method_name, self.original_method)
