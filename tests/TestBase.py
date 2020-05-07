
from logging import config
import logging.config

from json import load as jsonLoad

from os import sep as osSep

from unittest import TestCase

from pkg_resources import resource_filename


class TestBase(TestCase):

    RESOURCES_PACKAGE_NAME: str = 'tests.testdata'
    RESOURCES_PATH:         str = f'tests{osSep}testdata'

    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'
    JSON_LOGGING_CONFIG_FILENAME = "testLoggingConfig.json"

    @classmethod
    def setUpLogging(cls):
        """"""
        fqFileName: str = TestBase.retrieveResourcePath(TestBase.JSON_LOGGING_CONFIG_FILENAME)
        with open(fqFileName, 'r') as loggingConfigurationFile:
            configurationDictionary = jsonLoad(loggingConfigurationFile)

        config.dictConfig(configurationDictionary)
        logging.logProcesses = False
        logging.logThreads = False

    @classmethod
    def retrieveResourcePath(cls, bareFileName: str) -> str:

        # Use this method in Python 3.9
        # from importlib_resources import files
        # configFilePath: str  = files('org.pyut.resources').joinpath(Pyut.JSON_LOGGING_CONFIG_FILENAME)

        try:
            fqFileName: str = resource_filename(TestBase.RESOURCES_PACKAGE_NAME, bareFileName)
        except (ValueError, Exception):
            #
            # Maybe we are in an app
            #
            from os import environ
            pathToResources: str = environ.get(f'{TestBase.RESOURCE_ENV_VAR}')
            fqFileName:      str = f'{pathToResources}/{TestBase.RESOURCES_PATH}/{bareFileName}'

        return fqFileName
