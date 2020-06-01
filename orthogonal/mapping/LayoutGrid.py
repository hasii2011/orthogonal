
from typing import cast

from logging import Logger
from logging import getLogger

from orthogonal.mapping.exceptions.FailedPositioningException import FailedPositioningException
from orthogonal.mapping.exceptions.UnSupportedOperationException import UnSupportedOperationException

from orthogonal.mapping.EmbeddedTypes import Position
from orthogonal.mapping.EmbeddedTypes import Positions


class LayoutGrid:

    ZERO_ZERO_POSITION: Position = Position(0, 0)

    def __init__(self, width: int, height: int, nodePositions: Positions):

        self.logger: Logger = getLogger(__name__)

        self._gridWidth  = width
        self._gridHeight = height

        self._grid = {}
        for x in range(self._gridWidth):
            col = {}
            for y in range(self._gridHeight):
                col[y] = f'{x},{y}'  # Just something to size it
            self._grid[x] = col

        self.logger.info(f'{self._grid}')

        self._zeroNodePosition: Position = cast(Position, None)

        self.determineZeroZeroNodePosition(nodePositions)

    @property
    def zeroNodePosition(self) -> Position:
        return self._zeroNodePosition

    @zeroNodePosition.setter
    def zeroNodePosition(self, theNewValue: Position):
        raise UnSupportedOperationException('This is a computed value')

    def determineZeroZeroNodePosition(self, nodePositions: Positions):

        potentialPos:     Position = Position(0, 0)
        maxPos:           Position = Position(self._gridWidth - 1, self._gridHeight - 1)

        while potentialPos <= maxPos:
            self.logger.info(f'Try: {potentialPos}')
            potentialPos = self.nextGridPosition(currentGridPosition=potentialPos)
            try:
                self.computeAGridPosition(potentialPos, nodePositions)
                break   # No exception means we found where to put zero zero node
            except FailedPositioningException as fpe:
                self.logger.error(f'{fpe}')

        self.logger.info(f'All nodes positioned;  Zero Zero node at: {potentialPos}')
        self._zeroNodePosition: Position = potentialPos

    def computeAGridPosition(self, theGridPosition: Position, nodePositions: Positions):

        for nodePosition in nodePositions:

            currP: Position = nodePositions[nodePosition]
            if currP != LayoutGrid.ZERO_ZERO_POSITION:
                self.logger.info(f'currP :{currP}')

                x = theGridPosition.x + currP.x
                y = theGridPosition.y + currP.y
                self.logger.debug(f'grid x,y = ({x},{y})')
                try:
                    aRow = self._grid[x]
                    aCell = aRow[y]
                    self.logger.debug(f'aRow: {aRow} aCell: {aCell}')
                except KeyError as e:
                    self.logger.error(f'Potential Position: {theGridPosition} does not work')
                    raise FailedPositioningException()

        self.logger.info(f'All nodes positioned;  Zero Zero node at: {theGridPosition}')

    def nextGridPosition(self, currentGridPosition: Position) -> Position:

        nextX: int = currentGridPosition.x + 1
        nextY: int = currentGridPosition.y
        if nextX > self._gridWidth - 1:
            nextX = 0
            nextY: int = currentGridPosition.y + 1

        return Position(nextX, nextY)
