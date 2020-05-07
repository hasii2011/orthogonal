from logging import Logger
from logging import getLogger

from tests.TestBase import TestBase


class TestEmbeddingToScreen(TestBase):

    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestEmbeddingToScreen.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestEmbeddingToScreen.clsLogger

    def testSimple(self):
        pass
