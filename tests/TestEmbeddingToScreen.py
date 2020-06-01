from logging import Logger
from logging import getLogger

from orthogonal.mapping.EmbeddedTypes import Positions
from orthogonal.mapping.EmbeddedTypes import Position

from orthogonal.topologyShapeMetric.EmbeddingToScreen import EmbeddingToScreen

from orthogonal.topologyShapeMetric.ScreenSize import ScreenSize

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
        simplePositions: Positions = {'Node0': Position(0, 0),
                                      'Node5': Position(0, 1),
                                      'Node1': Position(1, 0),
                                      'Node4': Position(1, -1),
                                      'Node3': Position(2, 0),
                                      'Node2': Position(1, 1)
                                      }

        ets: EmbeddingToScreen   = EmbeddingToScreen(ScreenSize(1000, 1000), simplePositions)

        self.assertEqual(2, ets._maxX)
        self.assertEqual(1, ets._maxY)
        self.assertEqual(0, ets._minX)
        self.assertEqual(-1, ets._minY)
        self.assertEqual(2, ets._embeddedWidth)
        self.assertEqual(2, ets._embeddedHeight)

    def testComplex(self):
        complexPositions: Positions = {'Class0': Position(0, 0),
                                       'Class1': Position(0, 1),
                                       'Class4': Position(0, 2),
                                       'Class2': Position(-1, 1),
                                       'Class5': Position(-1, 2),
                                       'Class9': Position(0, 2),
                                       'Class8': Position(-1, 3),
                                       'Class7': Position(-2, 2),
                                       'Class6': Position(-1, 0),
                                       'Class3': Position(1, 0)
                                       }
        ets: EmbeddingToScreen   = EmbeddingToScreen(ScreenSize(1000, 1000), complexPositions)

        self.assertEqual(1, ets._maxX)
        self.assertEqual(3, ets._maxY)
        self.assertEqual(-2, ets._minX)
        self.assertEqual(0, ets._minY)
        self.assertEqual(3, ets._embeddedWidth)
        self.assertEqual(3, ets._embeddedHeight)

    # def testComputeXIntervals(self):
    #
    #     ets: EmbeddingToScreen = EmbeddingToScreen(ScreenSize(1000, 1000))
    #
    #     ets._computeXIntervals(biggestX=2)
