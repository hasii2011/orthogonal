"""
Common type definitions for topological graph elements and flow networks.
"""

from typing import Tuple
from typing import Hashable
from typing import NewType

type NodeId = Hashable
type FaceId = Hashable

HalfEdgeId = NewType('HalfEdgeId', Tuple[Hashable, Hashable])

type FlowEdgeKey = HalfEdgeId | Hashable
