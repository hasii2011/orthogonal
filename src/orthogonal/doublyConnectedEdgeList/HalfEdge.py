
from typing import Tuple
from typing import NewType
from typing import Optional
from typing import Hashable
from typing import TYPE_CHECKING

from orthogonal.doublyConnectedEdgeList.GraphElement import GraphElement

HalfEdgeId = NewType('HalfEdgeId', Tuple[Hashable, Hashable])

if TYPE_CHECKING:
    from orthogonal.doublyConnectedEdgeList.Face import Face
    from orthogonal.doublyConnectedEdgeList.Vertex import Vertex


class HalfEdge(GraphElement):
    """
    Represents a directed half-edge in a Doubly-Connected Edge List (DCEL).

    Each undirected edge is composed of two twin half-edges with opposing directions.
    Maintains topological connectivity around vertex origins and face boundaries.
    """

    def __init__(self, edgeId: HalfEdgeId):
        """
        Initialize the half-edge with an identifier.

        Args:
            edgeId: Unique HalfEdgeId identifier for the half-edge, a 2-tuple (u, v).
        """
        super().__init__(edgeId)
        self._twin:         Optional['HalfEdge'] = None
        self._origin:       Optional['Vertex']   = None
        self._incidentFace: Optional['Face']     = None
        self._previous:     Optional['HalfEdge'] = None
        self._next:         Optional['HalfEdge'] = None

    @property
    def twin(self) -> Optional['HalfEdge']:
        """
        Get the opposite directed twin half-edge.

        Returns:
            The twin half-edge running in the opposing direction.
        """
        return self._twin

    @twin.setter
    def twin(self, twinEdge: Optional['HalfEdge']):
        """
        Set the opposite directed twin half-edge.

        Args:
            twinEdge: The twin half-edge running in the opposing direction.
        """
        self._twin = twinEdge

    @property
    def origin(self) -> Optional['Vertex']:
        """
        Get the origin vertex of this directed half-edge.

        Returns:
            The starting vertex where this half-edge originates.
        """
        return self._origin

    @origin.setter
    def origin(self, originVertex: Optional['Vertex']):
        """
        Set the origin vertex of this directed half-edge.

        Args:
            originVertex: The starting vertex where this half-edge originates.
        """
        self._origin = originVertex

    @property
    def incidentFace(self) -> Optional['Face']:
        """
        Get the face incident to the left of this directed half-edge.

        Returns:
            The incident Face object.
        """
        return self._incidentFace

    @incidentFace.setter
    def incidentFace(self, theIncidentFace: Optional['Face']):
        """
        Set the face incident to the left of this directed half-edge.

        Args:
            theIncidentFace: The incident Face object.
        """
        self._incidentFace = theIncidentFace

    @property
    def previous(self) -> Optional['HalfEdge']:
        """
        Get the predecessor half-edge on the face boundary cycle.

        Returns:
            The previous half-edge in counter-clockwise order around the face.
        """
        return self._previous

    @previous.setter
    def previous(self, previousEdge: Optional['HalfEdge']):
        """
        Set the predecessor half-edge on the face boundary cycle.

        Args:
            previousEdge: The half-edge preceding this edge on the face boundary.
        """
        self._previous = previousEdge

    @property
    def next(self) -> Optional['HalfEdge']:
        """
        Get the successor half-edge on the face boundary cycle.

        Returns:
            The next half-edge in counter-clockwise order around the face.
        """
        return self._next

    @next.setter
    def next(self, nextEdge: Optional['HalfEdge']):
        """
        Set the successor half-edge on the face boundary cycle.

        Args:
            nextEdge: The half-edge succeeding this edge on the face boundary.
        """
        self._next = nextEdge

    def getPoints(self) -> HalfEdgeId:
        """
        Retrieve origin vertex identifiers for this half-edge and its twin.

        Returns:
            The HalfEdgeId (u, v) representing this directed half-edge.
        """
        originVertex: Optional['Vertex']   = self.origin
        twinEdge:     Optional['HalfEdge'] = self.twin

        assert originVertex is not None
        assert twinEdge is not None

        twinOrigin: Optional['Vertex'] = twinEdge.origin
        assert twinOrigin is not None

        return HalfEdgeId((originVertex.id, twinOrigin.id))

    def setAll(
        self,
        twinEdge: Optional['HalfEdge'],
        originVertex: Optional['Vertex'],
        previousEdge: Optional['HalfEdge'],
        nextEdge: Optional['HalfEdge'],
        incidentFace: Optional['Face'],
    ):
        """
        Assign all references for this half-edge in a single operation.

        Args:
            twinEdge: The opposite directed half-edge.
            originVertex: Origin vertex of this half-edge.
            previousEdge: Preceding half-edge on the face cycle.
            nextEdge: Succeeding half-edge on the face cycle.
            incidentFace: Incident face to the left of this half-edge.
        """
        self.twin = twinEdge
        self.origin = originVertex
        self.previous = previousEdge
        self.next = nextEdge
        self.incidentFace = incidentFace
