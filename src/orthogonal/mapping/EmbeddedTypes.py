
from typing import Dict


from dataclasses import dataclass

NodeName = str


@dataclass(frozen=True)
class Position:
    """
    This class is immutable;  frozen=true;  Python then creates a good
    __hash__ method
    """

    __slots__ = ['x', 'y']

    x: int
    y: int

    def __le__(self, other: 'Position'):
        """
        Currently this is the only one used
        """
        ans: bool = True

        if self.x > other.x:
            ans = False
        elif self.y > other.y:
            ans = False

        return ans

    def __ge__(self, other: 'Position'):
        """
        Only defined for completeness
        """
        ans: bool = True

        if self.x < other.x:
            ans = False
        elif self.y < other.y:
            ans = False

        return ans


Positions = Dict[NodeName, Position]


@dataclass
class ScreenCoordinates:

    __slots__ = ['x', 'y']

    x: int
    y: int
