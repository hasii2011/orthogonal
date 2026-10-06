from typing import Any
from typing import Optional
from typing import Iterator
from typing import TYPE_CHECKING

from orthogonal.doublyConnectedEdgeList.DcelExceptions import UninitializedDcelError
from orthogonal.doublyConnectedEdgeList.GraphElement import GraphElement

if TYPE_CHECKING:
    from orthogonal.doublyConnectedEdgeList.Face import Face
    from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdge


class Vertex(GraphElement):
    """
    Represents a vertex in a Doubly Connected Edge List (DCEL).

    Maintains a reference to an outgoing incident half-edge.
    """

    def __init__(self, name: Any):
        """
        Initialize the vertex with an identifier.

        Args:
            name: Unique identifier for the vertex.
        """
        super().__init__(name)
        self._incidentEdge: Optional['HalfEdge'] = None
        self.x:             Optional[float]      = None
        self.y:             Optional[float]      = None

    @property
    def incidentEdge(self) -> 'HalfEdge':
        """
        Get the first outgoing incident half-edge originating from this vertex.

        Returns:
            The incident HalfEdge originating from this vertex.

        Raises:
            UninitializedDcelError: If accessed before incidentEdge is wired.
        """
        if self._incidentEdge is None:
            raise UninitializedDcelError(f'Vertex {self.id} incidentEdge is uninitialized')
        return self._incidentEdge

    @incidentEdge.setter
    def incidentEdge(self, edge: Optional['HalfEdge']):
        """
        Set the first outgoing incident half-edge originating from this vertex.

        Args:
            edge: The incident HalfEdge originating from this vertex.
        """
        self._incidentEdge = edge

    @property
    def hasIncidentEdge(self) -> bool:
        """
        Check if an incident edge has been assigned to this vertex.

        Returns:
            True if incidentEdge is assigned, False otherwise.
        """
        return self._incidentEdge is not None

    def surround_faces(self) -> Iterator['Face']:
        """
        Generate faces incident to this vertex in clockwise order.

        Yields:
            Incident Face instances surrounding this vertex.
        """
        for halfEdge in self.surround_half_edges():
            yield halfEdge.incidentFace

    def surround_half_edges(self) -> Iterator['HalfEdge']:
        """
        Generate outgoing half-edges incident to this vertex in clockwise order.

        Yields:
            Successive HalfEdge instances originating from this vertex.
        """
        if not self.hasIncidentEdge:
            return

        startEdge: 'HalfEdge' = self.incidentEdge
        yield startEdge
        currentEdge: 'HalfEdge' = startEdge.previous.twin
        while currentEdge is not startEdge:
            yield currentEdge
            currentEdge = currentEdge.previous.twin
