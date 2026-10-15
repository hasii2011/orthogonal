"""
Common type definitions for the DCEL vector visualizer.
"""

from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Tuple
from typing import NewType

from orthogonal.TopologyTypes import NodeId
from orthogonal.doublyConnectedEdgeList.DoublyConnectedEdgeList import DoublyConnectedEdgeList

from wx.lib.ogl import LineShape
from tests.demo.dcelvisualizer.shapes.BadgeShape import BadgeShape

from tests.demo.CanvasTypes import NodePositions

CycleNodes     = NewType('CycleNodes',     List[NodeId])
EdgeShapeEntry = NewType('EdgeShapeEntry', Tuple[NodeId, NodeId, LineShape, BadgeShape])
FaceShapeEntry = NewType('FaceShapeEntry', Tuple[CycleNodes, float, BadgeShape])


@dataclass(frozen=True)
class StepState:
    """
    Encapsulates the reconstructed DCEL graph state at a given replay step.
    """
    dcel:         DoublyConnectedEdgeList
    positions:    NodePositions
    insertedNode: Optional[NodeId]
    lastAction:   str
