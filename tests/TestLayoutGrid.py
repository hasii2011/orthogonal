
from logging import Logger
from logging import getLogger

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

    def testSimple(self):

        simplePositions: Positions = {'Node0': Position(0, 0),
                                      'Node5': Position(0, 1),
                                      'Node1': Position(1, 0),
                                      'Node4': Position(1, -1),
                                      'Node3': Position(2, 0),
                                      'Node2': Position(1, 1)
                                      }

        layoutGrid: LayoutGrid = LayoutGrid(width=3, height=3, nodePositions=simplePositions)

        expectedZeroZeroPosition: Position = Position(0, 1)
        self.assertEqual(expectedZeroZeroPosition, layoutGrid.zeroNodePosition)
