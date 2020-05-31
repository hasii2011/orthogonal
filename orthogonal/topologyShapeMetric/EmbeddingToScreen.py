from typing import Dict
from typing import List
from typing import Tuple

from logging import Logger
from logging import getLogger

from orthogonal.topologyShapeMetric.ScreenSize import ScreenSize

NODE_NAME = str
POSITION  = Tuple[int, int]
POSITIONS = Dict[NODE_NAME, POSITION]


class EmbeddingToScreen:

    def __init__(self, screenSize: ScreenSize, nodePositions: POSITIONS):

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

        self._embeddedWidth:  int = abs(self._minX - self._maxX)
        self._embeddedHeight: int = abs(self._minY - self._maxY)

    def _convertEmbeddingToScreenPosition(self, nodePositions: POSITIONS):

        self._maxX: int = self._findMaxX(nodePositions)
        self._maxY: int = self._findMaxY(nodePositions)
        self._minX: int = self._findMinX(nodePositions)
        self._minY: int = self._findMinY(nodePositions)

        self.logger.info(f'maxX: {self._maxX} maxY: {self._maxY} minX: {self._minX} minY: {self._minY}')

    def _findMaxX(self, nodePositions: POSITIONS) -> int:

        MaxX: int = 0
        for node in nodePositions:
            currentX, currentY = nodePositions[node]
            if currentX > MaxX:
                MaxX = currentX

        return MaxX

    def _findMaxY(self, nodePositions: POSITIONS) -> int:

        maxY: int = 0
        for node in nodePositions:
            currentX, currentY = nodePositions[node]
            if currentY > maxY:
                maxY = currentY

        return maxY

    def _findMinX(self, nodePositions: POSITIONS) -> int:

        minX: int = 0
        for node in nodePositions:
            currentX, currentY = nodePositions[node]
            if currentX < minX:
                minX = currentX

        return minX

    def _findMinY(self, nodePositions: POSITIONS) -> int:

        minY: int = 0
        for node in nodePositions:
            currentX, currentY = nodePositions[node]
            if currentY < minY:
                minY = currentY

        return minY

    def _computeXIntervals(self, biggestX: int):

        self._xIntervalList['0'] = 0
        xInterval: int = self._screenSize.width // biggestX
        for x in range(1, biggestX + 1):
            self.logger.info(f'xInterval: {xInterval}')
            self._xIntervalList[str(x)] = (x * xInterval) - 1
