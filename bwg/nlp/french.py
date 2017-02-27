# -*- coding: utf-8 -*-
"""
NLP Pipiline tasks for french texts.
"""

# PROJECT
from pipeline import PipelineTask, Pipeline


class FrenchPipeline(Pipeline):
    """
    French NLP pipeline that involves the following steps:
        - Named Entity Recognition
        - Dependency Parsing
        - Open Relation Extraction
    """
    def __init__(self):
        super().__init__(
            NERTaggingTask,
            DependencyParsingTask,
            OpenRelationExtractionTask
        )


class NERTaggingTask(PipelineTask):
    """
    Task that performs Named Entity Recognition on french text.
    """
    def task_function(self, *args, **kwargs):
        #TODO: Implement function
        pass


class DependencyParsingTask(PipelineTask):
    """
    Task that performs Dependency Parsing on french text.
    """
    def task_function(self, *args, **kwargs):
        #TODO: Implement function
        pass


class OpenRelationExtractionTask(PipelineTask):
    """
    Task that performs Open Relation Extraction on french text, utilizing Named Entity tags and Dependency parse trees.
    """
    def task_function(self, *args, **kwargs):
        #TODO: Implement function
        pass

