"""
Common canvas coordinate and layout type definitions shared across demo visualizers.
"""

from typing import Dict
from typing import NewType
from typing import Tuple

from orthogonal.TopologyTypes import NodeId

CanvasPoint   = NewType('CanvasPoint',   Tuple[float, float])
NodePositions = NewType('NodePositions', Dict[NodeId, CanvasPoint])
