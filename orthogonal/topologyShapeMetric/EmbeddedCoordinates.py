from dataclasses import dataclass


@dataclass
class EmbeddedCoordinates:
    biggestX:  int = 0
    biggestY:  int = 0
    smallestY: int = 0
