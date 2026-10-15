
from dataclasses import dataclass
from typing import List
from typing import NewType
from typing import Optional

from orthogonal.TopologyTypes import NodeId
from tests.demo.CanvasTypes import CanvasPoint


@dataclass(frozen=True)
class DcelStep:
    """
    Encapsulates a single step in constructing or modifying a DCEL.
    """
    opType:   str
    u:        NodeId
    v:        Optional[NodeId]      = None
    newNode:  Optional[NodeId]      = None
    position: Optional[CanvasPoint] = None


DcelSteps = NewType('DcelSteps', List[DcelStep])
