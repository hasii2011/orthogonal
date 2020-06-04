
from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from orthogonal.mapping.LayoutGrid import GridColumnType
from orthogonal.mapping.LayoutGrid import LayoutGrid

from tests.TestBase import TestBase


from orthogonal.mapping.EmbeddedTypes import Position
from orthogonal.mapping.EmbeddedTypes import Positions


class TestLayoutGrid(TestBase):

    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestLayoutGrid.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestLayoutGrid.clsLogger

    def testInitializeValidGrid(self):

        layoutGrid: LayoutGrid = LayoutGrid(width=9, height=6)

        self.assertTrue(len(layoutGrid._grid) == 9, 'Incorrect width')
        col: GridColumnType = layoutGrid._grid[4]
        self.assertTrue(len(col) == 6, 'Incorrect height')

    def testNextGridPosition(self):
        layoutGrid: LayoutGrid = LayoutGrid(width=9, height=6)

        currentPosition:    Position = Position(3, 3)
        actualNextPosition: Position = layoutGrid._nextGridPosition(currentGridPosition=currentPosition)

        expectedPosition:   Position = Position(4, 3)

        self.assertEqual(expectedPosition, actualNextPosition, 'Oops something is broken')

    def testSimple(self):

        simplePositions: Positions = {'Node0': Position(0, 0),
                                      'Node5': Position(0, 1),
                                      'Node1': Position(1, 0),
                                      'Node4': Position(1, -1),
                                      'Node3': Position(2, 0),
                                      'Node2': Position(1, 1)
                                      }

        layoutGrid: LayoutGrid = LayoutGrid(width=3, height=3)

        layoutGrid.determineZeroZeroNodePosition(nodePositions=simplePositions)

        expectedZeroZeroPosition: Position = Position(0, 1)
        self.assertEqual(expectedZeroZeroPosition, layoutGrid.zeroNodePosition)

    def testComplex(self):
        complexPositions: Positions = {'Class0': Position(0, 0),
                                       'Class1': Position(0, 1),
                                       'Class2': Position(1, 1),
                                       'Class6': Position(2, 1),
                                       'Class5': Position(1, 2),
                                       'Class7': Position(2, 2),
                                       'Class8': Position(1, 3),
                                       'Class9': Position(0, 2),
                                       'Class4': Position(-1, 1),
                                       'Class3': Position(1, 0),
                                       }
        layoutGrid: LayoutGrid = LayoutGrid(width=4, height=4)

        layoutGrid.determineZeroZeroNodePosition(nodePositions=complexPositions)

        expectedZeroZeroPosition: Position = Position(1, 3)
        self.assertEqual(expectedZeroZeroPosition, layoutGrid.zeroNodePosition)

    # def testLayoutFail(self):
    #
    #     complexPositions: Positions = {'Class0': Position(0, 0),
    #                                    'Class1': Position(0, 1),
    #                                    'Class4': Position(0, 2),
    #                                    'Class2': Position(-1, 1),
    #                                    'Class5': Position(-1, 2),
    #                                    'Class9': Position(0, 2),      # This was a bug in the layout engine
    #                                    'Class8': Position(-1, 3),
    #                                    'Class7': Position(-2, 2),
    #                                    'Class6': Position(-1, 0),
    #                                    'Class3': Position(1, 0)
    #                                    }
    #
    #     layoutGrid: LayoutGrid = LayoutGrid(width=4, height=4, nodePositions=complexPositions)
    #
    #     expectedZeroZeroPosition: Position = Position(2, 3)
    #     self.assertEqual(expectedZeroZeroPosition, layoutGrid.zeroNodePosition)


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestLayoutGrid))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
