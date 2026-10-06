from typing import Any
from typing import List
from typing import Optional
from typing import Iterator
from typing import TYPE_CHECKING

from orthogonal.doublyConnectedEdgeList.DcelExceptions import UninitializedDcelError
from orthogonal.GraphElement import GraphElement

if TYPE_CHECKING:
    from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdge
    from orthogonal.doublyConnectedEdgeList.Vertex import Vertex


class Face(GraphElement):
    """
    Represents a face in a Doubly Connected Edge List (DCEL).

    Maintains references to a bounding half-edge cycle.
    """

    def __init__(self, name: Any):
        """
        Initialize the face with an identifier.

        Args:
            name: Unique identifier for the face.
        """
        super().__init__(name)
        self._incidentEdge: Optional['HalfEdge'] = None
        self.nodes_id:      List[Any]            = []

    @property
    def incidentEdge(self) -> 'HalfEdge':
        """
        Get the first half-edge incident to the face boundary cycle.

        Returns:
            The incident HalfEdge bounding this face.

        Raises:
            UninitializedDcelError: If accessed before incidentEdge is wired.
        """
        if self._incidentEdge is None:
            raise UninitializedDcelError(f'Face {self.id} incidentEdge is uninitialized')
        return self._incidentEdge

    @incidentEdge.setter
    def incidentEdge(self, edge: Optional['HalfEdge']):
        """
        Set the first half-edge incident to the face boundary cycle.

        Args:
            edge: The incident HalfEdge bounding this face.
        """
        self._incidentEdge = edge

    @property
    def hasIncidentEdge(self) -> bool:
        """
        Check if an incident edge has been assigned to this face.

        Returns:
            True if incidentEdge is assigned, False otherwise.
        """
        return self._incidentEdge is not None

    def update_nodes(self):
        """
        Update the list of bounding vertex identifiers for this face.
        """
        self.nodes_id = [vertex.id for vertex in self.surround_vertices()]

    def surround_faces(self) -> Iterator['Face']:
        """
        Generate adjacent faces sharing edges with this face.

        Yields:
            Adjacent Face instances across boundary half-edge twins.
        """
        for halfEdge in self.surround_half_edges():
            yield halfEdge.twin.incidentFace

    def surround_half_edges(self) -> Iterator['HalfEdge']:
        """
        Generate half-edges bounding this face in clockwise cycle order.

        Yields:
            Successive HalfEdge instances forming the face boundary.
        """
        if not self.hasIncidentEdge:
            return

        startEdge: 'HalfEdge' = self.incidentEdge
        yield startEdge
        currentEdge: 'HalfEdge' = startEdge.next
        while currentEdge is not startEdge:
            yield currentEdge
            currentEdge = currentEdge.next

    def surround_vertices(self) -> Iterator['Vertex']:
        """
        Generate origin vertices bounding this face in cycle order.

        Yields:
            Successive Vertex instances bounding this face.
        """
        for halfEdge in self.surround_half_edges():
            yield halfEdge.origin

    def __len__(self) -> int:
        return len(self.nodes_id)

    def __repr__(self) -> str:
        return f'FaceView{repr(self.nodes_id)}'
