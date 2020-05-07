
from typing import Tuple

from logging import Logger
from logging import getLogger

from orthogonal.topologyShapeMetric.Planarization import POSITIONS


class EmbeddingToScreen:

    def __init__(self, screenSize: Tuple[int, int]):

        self.logger: Logger = getLogger(__name__)

        self._screenSize: Tuple[int, int] = screenSize

    def convertEmbeddingToScreenPosition(self, nodePositions: POSITIONS):
        pass
