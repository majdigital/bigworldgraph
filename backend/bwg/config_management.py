# -*- coding: utf-8 -*-
"""
Functions concerning the config management of the NLP pipeline.
"""

# STD
import os

# PROJECT
from bwg.helpers import get_config_from_py_file, overwrite_local_config_with_environ


class MissingConfigParameterException(Exception):
    """
    Exception that's being raised, when there are parameter missing in a configuration.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)


class UnsupportedLanguageException(Exception):
    """
    Exception that's being raised, when a user starts the NLP pipeline for a language that's not supported yet.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)


def build_task_config_for_language(tasks, language, config_file_path, include_optionals=True):
    """
    Builds a configuration for a NLP pipeline for a specific language given a list of tasks the pipeline should include.
    
    :param tasks: List of tasks that are included in this pipeline.
    :type tasks: list
    :param language: Pipeline language.
    :type language: str
    :param config_file_path: Path to config file.
    :type config_file_path: str
    :param include_optionals: Flag to include optional config parameters (True by default).
    :type include_optionals: bool
    :return: Dictionary with configuration parameters.
    :rtype: dict
    """
    raw_config = get_config_from_py_file(config_file_path)
    raw_config = overwrite_local_config_with_environ(raw_config)
    dependencies = raw_config["CONFIG_DEPENDENCIES"]
    target_config = {}

    # Check language support
    if language.upper() not in raw_config["SUPPORTED_LANGUAGES"]:
        raise UnsupportedLanguageException(
            "Language {language} is not supported. Please follow the following steps:\n\t* Add appropriate models to "
            "{stanford_path}\n\t* Construct a NLP pipeline in a separate module in the bwg.nlp package\n\t* Update "
            "config_management.py accordingly".format(language=language, stanford_path=raw_config["STANFORD_PATH"])
        )

    # Get task-independent config parameters
    target_config = _add_from_config_dependencies(target_config, raw_config, language, "all", dependencies)

    # Get optional config parameters if flag is set
    if include_optionals:
        target_config = _add_from_config_dependencies(target_config, raw_config, language, "optional", dependencies)

    # Get task-specific config parameters
    for task in tasks:
        # Check if dependent config parameters were defined
        if task not in dependencies:
            raise MissingConfigParameterException("No config parameters found for task {}".format(task))

        target_config = _add_from_config_dependencies(target_config, raw_config, language, task, dependencies)

    # Make sure everything unwanted is excluded, like...
    # ...config parameters that should intentionally be excluded
    for config_parameter in dependencies["exclude"]:
        config_parameter = format_config_parameter(config_parameter, language)
        if config_parameter in target_config:
            del target_config[config_parameter]

    # ...config parameters from other languages
    other_languages = set(raw_config["SUPPORTED_LANGUAGES"]) - set(language) \
        if len(raw_config["SUPPORTED_LANGUAGES"]) > 1 \
        else set()
    target_config = {
        key: value
        for key, value in target_config.items()
        if not any([key.startswith(lang) for lang in other_languages])
    }

    return target_config


def format_config_parameter(config_parameter, language):
    """
    Format the name of config parameter, adding the target language of necessary.
    
    :param config_parameter: Name of config parameter.
    :type config_parameter: str
    :param language: Pipeline language.
    :type language: str
    :return: Formatted config parameter.
    :rtype: str
    """
    if "{language}" in config_parameter:
        return config_parameter.format(language=language.upper())
    return config_parameter


def format_task_config_key(config_parameter):
    """
    Format the name of config parameter to be included as in the final task config, without any language references
    (because the names of parameters in Luigi tasks are language agnostic).
    
    :param config_parameter: Name of config parameter.
    :type config_parameter: str
    :return: Formatted config parameter.
    :rtype: str
    """
    if "{language}" in config_parameter:
        return "_".join(config_parameter.split("_")[1:])
    return config_parameter


def _add_from_config_dependencies(target_config, raw_config, language, dependency_name, dependencies):
    """
    Add configuration parameters from a specific configuration dependency (list of configuration parameters that should
    be included in the final configuration or as environment variables, given a list of tasks for the NLP pipeline).
    Raise an exception if parameters are missing.
    
    :param target_config: Target configuration.
    :type target_config: dict
    :param raw_config: Raw configuration.
    :type raw_config: dict
    :param language: Pipeline language.
    :type language: str
    :param dependency_name: Name of current configuration dependency.
    :type: dependency_name: str
    :param dependencies: Dictionary of all task dependencies.
    :type dependencies: dict
    :return: Enriched configuration.
    :rtype: dict
    """
    dependent_config_parameters = dependencies[dependency_name]

    def _get_from_raw_config_or_environ(config_parameter_, language_, raw_config_):
        formatted_config_parameter = format_config_parameter(config_parameter_, language_)

        if formatted_config_parameter in raw_config_:
            return raw_config_[formatted_config_parameter]

        return os.environ[formatted_config_parameter]

    # Check if all configuration parameters are present
    missing_config_parameters = [
        format_config_parameter(config_parameter, language)
        for config_parameter in dependent_config_parameters
        if format_config_parameter(config_parameter, language) not in raw_config and
           format_config_parameter(config_parameter, language) not in os.environ
    ]
    if len(missing_config_parameters) > 0:
        raise MissingConfigParameterException(
            "The following parameters are missing in the config that are mentioned under '{}' in the meta "
            "config: {}".format(dependency_name, ", ".join(missing_config_parameters))
        )

    # Add them
    target_config.update(
        {
            format_task_config_key(config_parameter): _get_from_raw_config_or_environ(
                config_parameter, language, raw_config
            )
            for config_parameter in dependent_config_parameters
        }
    )
    return target_config
