from dataclasses import dataclass


@dataclass
class EmbeddedCoordinates:
    maxX: int = 0
    maxY: int = 0
    minX: int = 0
    minY: int = 0
