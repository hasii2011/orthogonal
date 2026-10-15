"""
Type definitions for the Orthogonalization and FlowNet visualizer.
"""

from typing import NamedTuple

from orthogonal.TopologyTypes import FaceId
from orthogonal.TopologyTypes import FlowEdgeKey
from orthogonal.TopologyTypes import NodeId

from tests.demo.CanvasTypes import CanvasPoint
from tests.demo.CanvasTypes import NodePositions


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
