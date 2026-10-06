from typing import Any


class GraphElement:
    """
    Base class representing a topological element within a Doubly-Connected Edge List (DCEL).

    Serves as the common superclass for vertices, faces, and half-edges, providing
    a unique identifier and hashability for dictionary lookups and set operations.
    """

    def __init__(self, name: Any):
        """
        Initialize the graph element with a unique identifier.

        Args:
            name: Unique identifier for the topological element (e.g., vertex key, face tag, or half-edge tuple)
        """
        self.id: Any = name

    def __hash__(self) -> int:
        """
        Compute the hash based on the element identifier.

        Returns:
            Integer hash value of the element identifier.
        """
        return hash(self.id)
