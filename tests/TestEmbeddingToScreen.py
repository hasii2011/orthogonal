from logging import Logger
from logging import getLogger

from orthogonal.topologyShapeMetric.EmbeddedCoordinates import EmbeddedCoordinates
from orthogonal.topologyShapeMetric.EmbeddingToScreen import EmbeddingToScreen
from tests.TestBase import TestBase

from orthogonal.topologyShapeMetric.EmbeddingToScreen import POSITIONS


class TestEmbeddingToScreen(TestBase):

    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestEmbeddingToScreen.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestEmbeddingToScreen.clsLogger

    def testSimple(self):

        ets: EmbeddingToScreen = EmbeddingToScreen(screenSize=(1000, 1000))

        nodePositions: POSITIONS = {'Node0': (0, 0),
                                    'Node5': (0, 1),
                                    'Node1': (1, 0),
                                    'Node4': (1, -1),
                                    'Node3': (2, 0),
                                    'Node2': (1, 1)
                                    }

        ec: EmbeddedCoordinates = ets.convertEmbeddingToScreenPosition(nodePositions)

        self.assertEqual(2, ec.biggestX)
        self.assertEqual(1, ec.biggestY)
        self.assertEqual(-1, ec.smallestY)
