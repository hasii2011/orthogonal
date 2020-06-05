
from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from tests.TestBase import TestBase

from orthogonal.mapping.EmbeddedTypes import Positions
from orthogonal.mapping.EmbeddedTypes import Position

from orthogonal.topologyShapeMetric.EmbeddingToScreen import EmbeddingToScreen

from orthogonal.topologyShapeMetric.ScreenSize import ScreenSize


class TestEmbeddingToScreen(TestBase):

    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestEmbeddingToScreen.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestEmbeddingToScreen.clsLogger
        self._simplePositions: Positions = {'Node0': Position(0, 0),
                                            'Node5': Position(0, 1),
                                            'Node1': Position(1, 0),
                                            'Node4': Position(1, -1),
                                            'Node3': Position(2, 0),
                                            'Node2': Position(1, 1)
                                            }
        self._screenSize: ScreenSize = ScreenSize(1000, 1000)

    def testSimple(self):

        ets: EmbeddingToScreen   = EmbeddingToScreen(ScreenSize(1000, 1000), self._simplePositions)

        self.assertEqual(3, ets._embeddedWidth)
        self.assertEqual(3, ets._embeddedHeight)

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

        self.assertEqual(4, ets._embeddedWidth)
        self.assertEqual(4, ets._embeddedHeight)

    def testComputeXIntervals(self):

        ets: EmbeddingToScreen = EmbeddingToScreen(self._screenSize, self._simplePositions)

        ets._computeXIntervals(maxX=2)

        self.logger.info(f"xIntervals: {ets._xIntervals}")

        actualXPos: int = ets._xIntervals['1']
        self.assertEqual(499, actualXPos, 'X Computation changed')

    def testComputeYIntervals(self):

        ets: EmbeddingToScreen = EmbeddingToScreen(self._screenSize, self._simplePositions)

        ets._computeYIntervals(maxY=2)

        self.logger.info(f"yIntervals: {ets._yIntervals}")
        actualYPos: int = ets._yIntervals['2']
        self.assertEqual(999, actualYPos, 'Y Computation changed')


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestEmbeddingToScreen))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
