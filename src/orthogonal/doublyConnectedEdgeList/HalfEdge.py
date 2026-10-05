from __future__ import annotations

from typing import Any
from typing import Optional
from typing import Tuple

from orthogonal.doublyConnectedEdgeList.GraphElement import GraphElement


class HalfEdge(GraphElement):
    """
    Represents a directed half-edge in a Doubly-Connected Edge List (DCEL).

    Each undirected edge is composed of two twin half-edges with opposing directions.
    Maintains topological connectivity around vertex origins and face boundaries.
    """

    def __init__(self, name: Any):
        """
        Initialize the half-edge with an identifier.

        Args:
            name: Identifier for the half-edge, typically a tuple of vertex ids (u, v).
        """
        super().__init__(name)
        self.inc: Any = None  # the incident face
        self.twin: Optional[HalfEdge] = None
        self.ori: Any = None
        self._previous: Optional[HalfEdge] = None
        self._next: Optional[HalfEdge] = None

    @property
    def previous(self) -> Optional[HalfEdge]:
        """
        Get the predecessor half-edge on the face boundary cycle.

        Returns:
            The previous half-edge in counter-clockwise order around the face.
        """
        return self._previous

    @previous.setter
    def previous(self, thePrevious: Optional[HalfEdge]):
        """
        Set the predecessor half-edge on the face boundary cycle.

        Args:
            thePrevious: The half-edge preceding this edge on the face boundary.
        """
        self._previous = thePrevious

    @property
    def next(self) -> Optional[HalfEdge]:
        """
        Get the successor half-edge on the face boundary cycle.

        Returns:
            The next half-edge in counter-clockwise order around the face.
        """
        return self._next

    @next.setter
    def next(self, theNext: Optional[HalfEdge]):
        """
        Set the successor half-edge on the face boundary cycle.

        Args:
            theNext: The half-edge succeeding this edge on the face boundary.
        """
        self._next = theNext

    def get_points(self) -> Tuple[Any, Any]:
        """
        Retrieve origin vertex identifiers for this half-edge and its twin.

        Returns:
            A tuple (u, v) of vertex identifiers.
        """
        return self.ori.id, self.twin.ori.id

    def set_all(
        self,
        twin: Optional[HalfEdge],
        ori: Any,
        previous: Optional[HalfEdge],
        next: Optional[HalfEdge],
        inc: Any,
    ):
        """
        Assign all pointers for this half-edge in a single operation.

        Args:
            twin: The opposite directed half-edge.
            ori: Origin vertex of this half-edge.
            previous: Preceding half-edge on the face cycle.
            next: Succeeding half-edge on the face cycle.
            inc: Incident face to the left of this half-edge.
        """
        self.twin = twin
        self.ori = ori
        self.previous = previous
        self.next = next
        self.inc = inc
