
from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from tests.TestBase import TestBase

from orthogonal.mapping.EmbeddedTypes import ScreenCoordinates
from orthogonal.mapping.ScreenSize import ScreenSize
from orthogonal.mapping.EmbeddedTypes import Positions
from orthogonal.mapping.EmbeddedTypes import Position
from orthogonal.mapping.EmbeddingToScreen import EmbeddingToScreen


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
        self._complexPositions: Positions = {'Class0': Position(0, 0),
                                             'Class1': Position(0, 1),
                                             'Class2': Position(1, 1),
                                             'Class6': Position(2, 1),
                                             'Class5': Position(1, 2),
                                             'Class7': Position(2, 2),
                                             'Class8': Position(1, 3),
                                             'Class9': Position(0, 2),
                                             'Class4': Position(-1, 1),
                                             'Class3': Position(1, 0)
                                             }
        self._screenSize: ScreenSize = ScreenSize(1000, 1000)

    def testSimple(self):

        ets: EmbeddingToScreen   = EmbeddingToScreen(self._screenSize, self._simplePositions)

        self.assertEqual(3, ets._embeddedWidth)
        self.assertEqual(3, ets._embeddedHeight)

    def testComplex(self):

        ets: EmbeddingToScreen   = EmbeddingToScreen(self._screenSize, self._complexPositions)

        self.assertEqual(4, ets._embeddedWidth)
        self.assertEqual(4, ets._embeddedHeight)

    def testSimpleGetScreenPosition(self):

        ets: EmbeddingToScreen   = EmbeddingToScreen(self._screenSize, self._simplePositions)

        screenPosition: ScreenCoordinates = ets.getScreenPosition('Node1')
        self.assertEqual(499, screenPosition.x, 'X Mapping must be incorrect')
        self.assertEqual(499, screenPosition.y, 'Y Mapping must be incorrect')

        self.logger.info(f'{screenPosition=}')

    def testComplexGetScreenPosition(self):

        ets: EmbeddingToScreen   = EmbeddingToScreen(self._screenSize, self._complexPositions)

        screenPosition: ScreenCoordinates = ets.getScreenPosition('Class4')
        self.assertEqual(0, screenPosition.x, 'X Mapping must be incorrect')
        self.assertEqual(665, screenPosition.y, 'Y Mapping must be incorrect')

        self.logger.debug(f'Class4 - screenPosition: {screenPosition}')

        screenPosition = ets.getScreenPosition('Class6')
        self.assertEqual(998, screenPosition.x, 'X Mapping must be incorrect')
        self.assertEqual(665, screenPosition.y, 'Y Mapping must be incorrect')

        self.logger.debug(f'Class6 - {screenPosition=}')

    def testComputeXIntervals(self):

        ets: EmbeddingToScreen = EmbeddingToScreen(self._screenSize, self._simplePositions)

        ets._computeXIntervals(maxX=2)

        self.logger.debug(f"xIntervals: {ets._xIntervals=}")

        actualXPos: int = ets._xIntervals[1]
        self.assertEqual(499, actualXPos, 'X Computation changed')

    def testComputeYIntervals(self):

        ets: EmbeddingToScreen = EmbeddingToScreen(self._screenSize, self._simplePositions)

        ets._computeYIntervals(maxY=2)

        self.logger.debug(f"{ets._yIntervals=}")
        actualYPos: int = ets._yIntervals[2]
        self.assertEqual(999, actualYPos, 'Y Computation changed')


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestEmbeddingToScreen))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
