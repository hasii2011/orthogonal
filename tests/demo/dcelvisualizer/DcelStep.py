
from typing import Tuple
from typing import Optional

from orthogonal.TopologyTypes import NodeId


class DcelStep:
    """
    Encapsulates a single step in constructing or modifying a DCEL.
    """

    def __init__(
        self,
        opType: str,
        u: NodeId,
        v: Optional[NodeId] = None,
        newNode: Optional[NodeId] = None,
        position: Optional[Tuple[float, float]] = None,
    ):
        """
        Initialize a DCEL construction step.

        Args:
            opType: Operation type ('add_vertex', 'add_edge', 'subdivide').
            u: First node identifier.
            v: Second node identifier, if applicable.
            newNode: New node identifier for edge subdivision, if applicable.
            position: Canvas coordinate tuple for add_vertex, if applicable.
        """
        self._opType: str = opType
        self._u: NodeId = u
        self._v: Optional[NodeId] = v
        self._newNode: Optional[NodeId] = newNode
        self._position: Optional[Tuple[float, float]] = position

    @property
    def opType(self) -> str:
        """Get the operation type string."""
        return self._opType

    @property
    def u(self) -> NodeId:
        """Get the primary node identifier."""
        return self._u

    @property
    def v(self) -> Optional[NodeId]:
        """Get the secondary node identifier, if any."""
        return self._v

    @property
    def newNode(self) -> Optional[NodeId]:
        """Get the new node identifier, if any."""
        return self._newNode

    @property
    def position(self) -> Optional[Tuple[float, float]]:
        """Get the canvas position coordinates, if any."""
        return self._position
