"""
Type definitions for the Orthogonalization and FlowNet visualizer.
"""

from typing import Dict
from typing import NamedTuple
from typing import NewType
from typing import Tuple

from orthogonal.TopologyTypes import FaceId
from orthogonal.TopologyTypes import FlowEdgeKey
from orthogonal.TopologyTypes import NodeId

CanvasPoint   = NewType('CanvasPoint',   Tuple[float, float])
NodePositions = NewType('NodePositions', Dict[NodeId, CanvasPoint])


class AngleEntry(NamedTuple):
    """
    Encapsulates resolved corner angle metrics at a vertex within an incident face.
    """
    vertexId:     NodeId
    faceId:       FaceId
    halfEdgeId:   FlowEdgeKey
    flowUnits:    int
    angleDegrees: int


class FaceBalanceEntry(NamedTuple):
    """
    Encapsulates rectilinear polygon angle sum and network circulation balance for a face.
    """
    faceId:         FaceId
    isExternal:     bool
    degree:         int
    demand:         int
    vertexInflow:   int
    targetAngleSum: int
    isBalanced:     bool


class FlowArcEntry(NamedTuple):
    """
    Encapsulates a single directed circulation arc in the FlowNet graph.
    """
    source:     NodeId | FaceId
    target:     NodeId | FaceId
    arcType:    str
    key:        FlowEdgeKey
    lowerbound: int
    capacity:   int
    weight:     int
    flow:       int
