"""
Preset datasets for the Orthogonalization and FlowNet visualizer.
"""

from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional

from networkx import Graph
from networkx import read_gml

from orthogonal.TopologyTypes import NodeId
from tests.demo.orthovisualizer.OrthoTypes import CanvasPoint
from tests.demo.orthovisualizer.OrthoTypes import NodePositions


@dataclass(frozen=True)
class OrthoDataSet:
    """
    Encapsulates a graph dataset preset with optional predefined canvas coordinates.
    """
    name:             str
    description:      str
    graph:            Graph
    initialPositions: Optional[NodePositions] = None


def createDefaultDataSets() -> List[OrthoDataSet]:
    """
    Create standard planar graph presets for orthogonalization and circulation inspection.

    Returns:
        List of OrthoDataSet instances.
    """
    dataSets: List[OrthoDataSet] = []

    # 1. Triangle K3
    triangleGraph: Graph = Graph()
    triangleGraph.add_nodes_from(['v1', 'v2', 'v3'])
    triangleGraph.add_edges_from([('v1', 'v2'), ('v2', 'v3'), ('v3', 'v1')])
    trianglePositions: NodePositions = NodePositions({
        'v1': CanvasPoint((320.0, 100.0)),
        'v2': CanvasPoint((520.0, 420.0)),
        'v3': CanvasPoint((120.0, 420.0)),
    })
    dataSets.append(OrthoDataSet(
        name='Triangle (K3)',
        description='Minimal 3-cycle planar graph with 1 internal triangular face and 1 outer face.',
        graph=triangleGraph,
        initialPositions=trianglePositions,
    ))

    # 2. Diamond K4 - e
    diamondGraph: Graph = Graph()
    diamondGraph.add_nodes_from(['v1', 'v2', 'v3', 'v4'])
    diamondGraph.add_edges_from([
        ('v1', 'v2'),
        ('v2', 'v3'),
        ('v3', 'v4'),
        ('v4', 'v1'),
        ('v1', 'v3'),
    ])
    diamondPositions: NodePositions = NodePositions({
        'v1': CanvasPoint((320.0, 80.0)),
        'v2': CanvasPoint((520.0, 260.0)),
        'v3': CanvasPoint((320.0, 440.0)),
        'v4': CanvasPoint((120.0, 260.0)),
    })
    dataSets.append(OrthoDataSet(
        name='Diamond (K4 - e)',
        description='Planar diamond with 2 internal triangular faces sharing a central chord.',
        graph=diamondGraph,
        initialPositions=diamondPositions,
    ))

    # 3. House Graph (Pentagon with Roof)
    houseGraph: Graph = Graph()
    houseGraph.add_nodes_from(['v1', 'v2', 'v3', 'v4', 'v5'])
    houseGraph.add_edges_from([
        ('v1', 'v2'),
        ('v1', 'v3'),
        ('v2', 'v3'),
        ('v2', 'v4'),
        ('v3', 'v5'),
        ('v4', 'v5'),
    ])
    housePositions: NodePositions = NodePositions({
        'v1': CanvasPoint((320.0, 70.0)),
        'v2': CanvasPoint((180.0, 200.0)),
        'v3': CanvasPoint((460.0, 200.0)),
        'v4': CanvasPoint((180.0, 440.0)),
        'v5': CanvasPoint((460.0, 440.0)),
    })
    dataSets.append(OrthoDataSet(
        name='House Graph (Pentagon with Roof)',
        description='House-shaped graph containing a triangular roof face and a rectangular base face.',
        graph=houseGraph,
        initialPositions=housePositions,
    ))

    # 4. Simple Benchmark GML
    try:
        simpleGmlGraph: Graph = Graph(read_gml('tests/testdata/simple.gml'))
        # Extract initial positions from label string '(x, y)' if present
        simplePositionsDict: Dict[NodeId, CanvasPoint] = {}
        for nodeId in simpleGmlGraph.nodes:
            labelVal: str = str(simpleGmlGraph.nodes[nodeId].get('label', ''))
            if labelVal.startswith('(') and labelVal.endswith(')'):
                parts: List[str] = labelVal.strip('()').split(',')
                if len(parts) == 2:
                    rawX: float = float(parts[0].strip())
                    rawY: float = float(parts[1].strip())
                    simplePositionsDict[nodeId] = CanvasPoint((rawX * 0.35 + 50.0, rawY * 0.85 + 50.0))
        dataSets.append(OrthoDataSet(
            name='Benchmark: Simple GML',
            description='Loaded from tests/testdata/simple.gml.',
            graph=simpleGmlGraph,
            initialPositions=NodePositions(simplePositionsDict) if simplePositionsDict else None,
        ))
    except (FileNotFoundError, OSError):
        pass

    return dataSets
