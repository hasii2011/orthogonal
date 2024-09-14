
from os import sep as osSep

from codeallybasic.ResourceManager import ResourceManager
from codeallybasic.UnitTestBase import UnitTestBase


class ProjectTestBase(UnitTestBase):

    RESOURCES_DATA_PACKAGE_NAME: str = 'tests.testdata'
    RESOURCES_DATA_PATH:         str = f'tests{osSep}testdata'

    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'
    JSON_LOGGING_CONFIG_FILENAME = "testLoggingConfig.json"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    @classmethod
    def retrieveResourcePath(cls, bareFileName: str) -> str:

        # Use this method in Python 3.9
        # from importlib_resources import files
        # configFilePath: str  = files('org.pyut.resources').joinpath(Pyut.JSON_LOGGING_CONFIG_FILENAME)

        fqFileName: str = ResourceManager.retrieveResourcePath(bareFileName=bareFileName,
                                                               resourcePath=ProjectTestBase.RESOURCES_DATA_PATH,
                                                               packageName=ProjectTestBase.RESOURCES_DATA_PACKAGE_NAME)
        # try:
        #     fqFileName: str = resource_filename(TestBase.RESOURCES_PACKAGE_NAME, bareFileName)
        # except (ValueError, Exception):
        #     #
        #     # Maybe we are in an app
        #     #
        #     from os import environ
        #     pathToResources: str = environ.get(f'{TestBase.RESOURCE_ENV_VAR}')
        #     fqFileName:      str = f'{pathToResources}/{TestBase.RESOURCES_PATH}/{bareFileName}'

        return fqFileName
