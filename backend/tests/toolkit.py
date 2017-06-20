# -*- coding: utf-8 -*-
"""
Helper functions for testing.
"""

# STD
import copy
import json


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
