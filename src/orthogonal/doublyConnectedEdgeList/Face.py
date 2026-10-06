from typing import Any
from typing import List
from typing import Optional
from typing import Iterator
from typing import TYPE_CHECKING

from orthogonal.doublyConnectedEdgeList.GraphElement import GraphElement

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
    def incidentEdge(self) -> Optional['HalfEdge']:
        """
        Get the first half-edge incident to the face boundary cycle.

        Returns:
            The incident HalfEdge bounding this face.
        """
        return self._incidentEdge

    @incidentEdge.setter
    def incidentEdge(self, edge: Optional['HalfEdge']):
        """
        Set the first half-edge incident to the face boundary cycle.

        Args:
            edge: The incident HalfEdge bounding this face.
        """
        self._incidentEdge = edge

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
            twinEdge: Optional['HalfEdge'] = halfEdge.twin
            if twinEdge is not None:
                adjacentFace: Optional['Face'] = twinEdge.incidentFace
                if adjacentFace is not None:
                    yield adjacentFace

    def surround_half_edges(self) -> Iterator['HalfEdge']:
        """
        Generate half-edges bounding this face in clockwise cycle order.

        Yields:
            Successive HalfEdge instances forming the face boundary.
        """
        startEdge: Optional['HalfEdge'] = self.incidentEdge
        if startEdge is None:
            return

        yield startEdge
        currentEdge: Optional['HalfEdge'] = startEdge.next
        while currentEdge is not None and currentEdge is not startEdge:
            assert currentEdge is not None
            yield currentEdge
            currentEdge = currentEdge.next

    def surround_vertices(self) -> Iterator['Vertex']:
        """
        Generate origin vertices bounding this face in cycle order.

        Yields:
            Successive Vertex instances bounding this face.
        """
        for halfEdge in self.surround_half_edges():
            originVertex: Optional['Vertex'] = halfEdge.origin
            if originVertex is not None:
                yield originVertex

    def __len__(self) -> int:
        return len(self.nodes_id)

    def __repr__(self) -> str:
        return f'FaceView{repr(self.nodes_id)}'
