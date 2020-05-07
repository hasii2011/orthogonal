from typing import Dict
from typing import List
from typing import Tuple

from logging import Logger
from logging import getLogger

from orthogonal.topologyShapeMetric.EmbeddedCoordinates import EmbeddedCoordinates

NODE_NAME = str
POSITION  = Tuple[int, int]
POSITIONS = Dict[NODE_NAME, POSITION]


class EmbeddingToScreen:

    def __init__(self, screenSize: Tuple[int, int]):

        self.logger: Logger = getLogger(__name__)

        self._screenSize: Tuple[int, int] = screenSize

        self._xIntervalList:     List[int] = []
        self._yUpIntervalList:   List[int] = []
        self._yDownIntervalList: List[int] = []

    def convertEmbeddingToScreenPosition(self, nodePositions: POSITIONS) -> EmbeddedCoordinates:

        biggestX:  int = self._findFarthestRight(nodePositions)
        biggestY:  int = self._findFarthestUp(nodePositions)
        smallestY: int = self._findFarthestDown(nodePositions)

        self.logger.info(f'biggestX: {biggestX} biggestY: {biggestY} smallestY: {smallestY}')

        return EmbeddedCoordinates(biggestX=biggestX, biggestY=biggestY, smallestY=smallestY)

    def _findFarthestRight(self, nodePositions: POSITIONS) -> int:

        biggestX: int = 0
        for node in nodePositions:
            currentX, currentY = nodePositions[node]
            if currentX > biggestX:
                biggestX = currentX

        return biggestX

    def _findFarthestUp(self, nodePositions: POSITIONS) -> int:

        biggestY: int = 0
        for node in nodePositions:
            currentX, currentY = nodePositions[node]
            if currentY > biggestY:
                biggestY = currentY

        return biggestY

    def _findFarthestDown(self, nodePositions: POSITIONS) -> int:

        smallestY: int = 0
        for node in nodePositions:
            currentX, currentY = nodePositions[node]
            if currentY < smallestY:
                smallestY = currentY

        return smallestY

    def _computeXIntervals(self, biggestX: int):

        self._xIntervalList[0] = 0
