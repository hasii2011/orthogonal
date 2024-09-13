
from typing import Dict
from typing import Set
from typing import cast

from logging import Logger
from logging import getLogger

from copy import deepcopy

from orthogonal.mapping.exceptions.FailedPositioningException import FailedPositioningException
from orthogonal.mapping.exceptions.UnSupportedOperationException import UnSupportedOperationException

from orthogonal.mapping.EmbeddedTypes import NodeName
from orthogonal.mapping.EmbeddedTypes import Position
from orthogonal.mapping.EmbeddedTypes import Positions


GridColumnType = Dict[int, str]
GridType       = Dict[int, GridColumnType]
LayoutPosition = Dict[NodeName, Position]


class LayoutGrid:

    def __init__(self, width: int, height: int):

        self.logger: Logger = getLogger(__name__)

        self._gridWidth  = width
        self._gridHeight = height

        self.layoutPositions:     LayoutPosition = {}
        self._zeroNodePosition:   Position       = cast(Position, None)
        self._grid:               GridType       = self._initializeValidGrid(self._gridWidth, self._gridHeight)

        self.logger.debug(f'{self._grid}')

    @property
    def zeroNodePosition(self) -> Position:
        return self._zeroNodePosition

    @zeroNodePosition.setter
    def zeroNodePosition(self, theNewValue: Position):
        raise UnSupportedOperationException('This is a computed value')

    def determineZeroZeroNodePosition(self, nodePositions: Positions):

        potentialPos: Position = Position(0, 0)
        maxPos:       Position = Position(self._gridWidth - 1, self._gridHeight - 1)

        while potentialPos <= maxPos:
            try:
                self._computeAGridPosition(potentialPos, nodePositions)
                break   # No exception means we found where to put zero zero node
            except FailedPositioningException as fpe:
                self.logger.debug(f'{fpe}')
            potentialPos = self._nextGridPosition(currentGridPosition=potentialPos)

        self._zeroNodePosition: Position = potentialPos

    def _computeAGridPosition(self, theGridPosition: Position, nodePositions: Positions):

        self.logger.debug(f'Check Zero Zero node at: {theGridPosition}')
        inUsePositions: Set = set()

        gridCopy: GridType = deepcopy(self._grid)
        self.layoutPositions = {}   # reset

        for nodeName in nodePositions:

            currentGridPos: Position = nodePositions[nodeName]

            x = theGridPosition.x + currentGridPos.x
            y = theGridPosition.y - currentGridPos.y         # y is always up
            self.logger.debug(f'{currentGridPos=}  grid x,y = ({x},{y})')
            try:
                # aRow = self._grid[x]
                aRow = gridCopy[x]
                # noinspection PyUnusedLocal
                aCell = aRow[y]         # Only used to see if that key will generate a KeyError
                self.logger.debug(f'{currentGridPos=} fits at {x},{y}')
                gridPos: Position = Position(x, y)
                if gridPos in inUsePositions:
                    raise FailedPositioningException(f'grid position {gridPos} in use')
                else:
                    inUsePositions.add(gridPos)
                    aRow[y] = nodeName
                    self.logger.debug(f'{inUsePositions=}')
                    self.layoutPositions[nodeName] = gridPos
            except KeyError:
                self.logger.debug(f'Potential Position: {theGridPosition} failed at computed {x},{y}')
                raise FailedPositioningException(f'Potential Position: {theGridPosition} failed at computed {x},{y}')

        self.logger.info(f'All nodes positioned;  Zero Zero node at: {theGridPosition}')
        self.logger.debug(f'{self.layoutPositions=}')

    def _nextGridPosition(self, currentGridPosition: Position) -> Position:

        nextX: int = currentGridPosition.x + 1
        nextY: int = currentGridPosition.y
        if nextX > self._gridWidth - 1:
            nextX = 0
            nextY: int = currentGridPosition.y + 1

        return Position(nextX, nextY)

    def _initializeValidGrid(self, width: int, height: int) -> Dict[int, GridColumnType]:

        grid: Dict = {}
        for x in range(width):
            col: GridColumnType = {}
            for y in range(height):
                col[y] = f'{x},{y}'  # Just something to size it
            grid[x] = col

        return grid
