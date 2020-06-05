
from typing import Dict

from logging import Logger
from logging import getLogger

from orthogonal.mapping.LayoutGrid import LayoutGrid
from orthogonal.mapping.EmbeddedTypes import Position
from orthogonal.mapping.EmbeddedTypes import Positions


from orthogonal.topologyShapeMetric.ScreenSize import ScreenSize

IntervalType = Dict[str, int]


class EmbeddingToScreen:

    def __init__(self, screenSize: ScreenSize, nodePositions: Positions):

        self.logger:      Logger = getLogger(__name__)
        self._screenSize: ScreenSize = screenSize

        self._xIntervals: IntervalType = {}
        self._yIntervals: IntervalType = {}

        self._embeddedWidth:  int = 0
        self._embeddedHeight: int = 0

        self._determineGridSize(nodePositions)

        self._layoutGrid: LayoutGrid = LayoutGrid(width=self._embeddedWidth, height=self._embeddedHeight)
        self._layoutGrid.determineZeroZeroNodePosition(nodePositions=nodePositions)

        self._computeXIntervals(self._embeddedWidth - 1)
        self._computeYIntervals(self._embeddedHeight - 1)

    def getScreenPosition(self, nodeName: str):
        pass

    def _determineGridSize(self, nodePositions: Positions):

        maxX: int = self._findMaxX(nodePositions)
        maxY: int = self._findMaxY(nodePositions)
        minX: int = self._findMinX(nodePositions)
        minY: int = self._findMinY(nodePositions)

        self.logger.info(f'maxX: {maxX} maxY: {maxY} minX: {minX} minY: {minY}')

        self._embeddedWidth:  int = abs(minX - maxX) + 1
        self._embeddedHeight: int = abs(minY - maxY) + 1

    def _findMaxX(self, nodePositions: Positions) -> int:

        maxX: int = 0
        for nodeName in nodePositions:
            nodePosition: Position = nodePositions[nodeName]
            if nodePosition.x > maxX:
                maxX = nodePosition.x

        return maxX

    def _findMaxY(self, nodePositions: Positions) -> int:

        maxY: int = 0
        for node in nodePositions:
            nodePosition: Position = nodePositions[node]
            if nodePosition.y > maxY:
                maxY = nodePosition.y

        return maxY

    def _findMinX(self, nodePositions: Positions) -> int:

        minX: int = 0
        for node in nodePositions:
            nodePosition: Position = nodePositions[node]
            if nodePosition.x < minX:
                minX = nodePosition.x

        return minX

    def _findMinY(self, nodePositions: Positions) -> int:

        minY: int = 0
        for node in nodePositions:
            nodePosition: Position = nodePositions[node]
            if nodePosition.y < minY:
                minY = nodePosition.y

        return minY

    def _computeXIntervals(self, maxX: int):
        self._xIntervals = self._computeIntervals(self._screenSize.width, maxX)

    def _computeYIntervals(self, maxY: int):
        self._yIntervals = self._computeIntervals(self._screenSize.height, maxY)

    def _computeIntervals(self, nbrOfPoints: int, maxValue: int) -> IntervalType:

        intervals: IntervalType = {'0': 0}

        interval:  int = nbrOfPoints // maxValue
        for x in range(1, maxValue + 1):
            self.logger.info(f'interval: {interval}')
            intervals[str(x)] = (x * interval) - 1

        return intervals
