from typing import Dict
from typing import List

from logging import Logger
from logging import getLogger

from orthogonal.mapping.LayoutGrid import LayoutGrid
from orthogonal.mapping.EmbeddedTypes import Position
from orthogonal.mapping.EmbeddedTypes import Positions


from orthogonal.topologyShapeMetric.ScreenSize import ScreenSize


class EmbeddingToScreen:

    def __init__(self, screenSize: ScreenSize, nodePositions: Positions):

        self.logger:      Logger = getLogger(__name__)
        self._screenSize: ScreenSize = screenSize

        self._xIntervalList:     Dict[str, int] = {}
        self._yUpIntervalList:   List[int] = []
        self._yDownIntervalList: List[int] = []

        self._minX: int = 0
        self._maxX: int = 0
        self._minY: int = 0
        self._maxY: int = 0

        self._convertEmbeddingToScreenPosition(nodePositions)

        self._embeddedWidth:  int = abs(self._minX - self._maxX) + 1
        self._embeddedHeight: int = abs(self._minY - self._maxY) + 1

        self._layoutGrid: LayoutGrid = LayoutGrid(width=self._embeddedWidth, height=self._embeddedHeight, nodePositions=nodePositions)

    def _convertEmbeddingToScreenPosition(self, nodePositions: Positions):

        self._maxX: int = self._findMaxX(nodePositions)
        self._maxY: int = self._findMaxY(nodePositions)
        self._minX: int = self._findMinX(nodePositions)
        self._minY: int = self._findMinY(nodePositions)

        self.logger.info(f'maxX: {self._maxX} maxY: {self._maxY} minX: {self._minX} minY: {self._minY}')

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

    def _computeXIntervals(self, biggestX: int):

        self._xIntervalList['0'] = 0
        xInterval: int = self._screenSize.width // biggestX
        for x in range(1, biggestX + 1):
            self.logger.info(f'xInterval: {xInterval}')
            self._xIntervalList[str(x)] = (x * xInterval) - 1
