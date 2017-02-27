# -*- coding: utf-8 -*-
"""
Classes affiliated to the Natural Language Processing Pipeline.
"""

# STD
from abc import abstractmethod

class Pipeline:
    """
    Natural Language Processing pipeline class. This class is used to process corpora when added to the system. Usually, processing consists of Named Entity recognition, Dependency Parsing and using those to do Open Relation Extraction, but more steps can also be added.
    """
    def __init__(self, *tasks, **pipeline_config):
        self.tasks = tasks
        self.pipeline_config = pipeline_config

    def start(self):
        """
        Start pipeline.
        """
        result = tuple()

        for task in self.tasks:
            ready_task = task(*result, **self.pipeline_config)
            result = ready_task.start()

        return result


class PipelineTask:
    """
    Task that is scheduled within the pipeline.
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def start(self):
        """
        Start the task.
        """
        return self.task_function(*self.args, **self.kwargs)

    @abstractmethod
    def task_function(self, *args, **kwargs):
        """
        Executes the core work done in this task. Should be overwritten in subclasses.
        """
        pass
