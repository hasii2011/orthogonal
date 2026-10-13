"""
Common type definitions for the DCEL vector visualizer.
"""

from typing import Dict
from typing import List
from typing import Tuple
from typing import NewType

from orthogonal.TopologyTypes import NodeId

from wx.lib.ogl import LineShape
from tests.demo.dcelvisualizer.DcelBadgeShape import DcelBadgeShape

CanvasPoint    = NewType('CanvasPoint',    Tuple[float, float])
NodePositions  = NewType('NodePositions',  Dict[NodeId, CanvasPoint])
CycleNodes     = NewType('CycleNodes',     List[NodeId])
EdgeShapeEntry = NewType('EdgeShapeEntry', Tuple[NodeId, NodeId, LineShape, DcelBadgeShape])
FaceShapeEntry = NewType('FaceShapeEntry', Tuple[CycleNodes, float, DcelBadgeShape])
