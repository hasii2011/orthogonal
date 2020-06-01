
from typing import Dict


from dataclasses import dataclass

NodeName = str


@dataclass()
class Position:

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
