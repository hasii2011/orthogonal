"""
Common type definitions for topological graph elements and flow networks.
"""

from typing import Dict
from typing import Tuple
from typing import Hashable
from typing import NewType

type NodeId = Hashable
type FaceId = Hashable
type FlowNodeId = NodeId | FaceId

HalfEdgeId = NewType('HalfEdgeId', Tuple[Hashable, Hashable])

type FlowEdgeKey = HalfEdgeId | Hashable

FlowDict = NewType('FlowDict', Dict[FlowNodeId, Dict[FlowNodeId, Dict[FlowEdgeKey, int]]])
