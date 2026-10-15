
"""
Preset datasets for the Doubly-Connected Edge List (DCEL) visualizer.
"""

from dataclasses import dataclass
from typing import List

from tests.demo.CanvasTypes import CanvasPoint
from tests.demo.dcelvisualizer.DcelStep import DcelStep
from tests.demo.dcelvisualizer.DcelStep import DcelSteps


@dataclass(frozen=True)
class DcelDataSet:
    """
    Encapsulates a planar graph preset and its planned building steps.
    """
    name:         str
    plannedSteps: DcelSteps


def createDefaultDataSets() -> List[DcelDataSet]:
    """
    Construct standard preset datasets: Empty (Blank Canvas), Small (K3), Medium (Diamond), and Large (Grid).

    Returns:
        List of DcelDataSet instances.
    """
    emptyPreset: DcelDataSet = DcelDataSet(
        name='Empty (Blank Canvas)',
        plannedSteps=DcelSteps([]),
    )

    smallPreset: DcelDataSet = DcelDataSet(
        name='Small (Triangle K3)',
        plannedSteps=DcelSteps([
            DcelStep('add_vertex', 'v1', position=CanvasPoint((280.0, 90.0))),
            DcelStep('add_vertex', 'v2', position=CanvasPoint((460.0, 370.0))),
            DcelStep('add_vertex', 'v3', position=CanvasPoint((100.0, 370.0))),
            DcelStep('add_edge', 'v1', 'v2'),
            DcelStep('add_edge', 'v2', 'v3'),
            DcelStep('add_edge', 'v3', 'v1'),
            DcelStep('subdivide', 'v1', 'v2', newNode='v12'),
            DcelStep('subdivide', 'v2', 'v3', newNode='v23'),
        ]),
    )

    mediumPreset: DcelDataSet = DcelDataSet(
        name='Medium (Diamond K4 - e)',
        plannedSteps=DcelSteps([
            DcelStep('add_vertex', 'v1', position=CanvasPoint((280.0, 70.0))),
            DcelStep('add_vertex', 'v2', position=CanvasPoint((460.0, 230.0))),
            DcelStep('add_vertex', 'v3', position=CanvasPoint((280.0, 390.0))),
            DcelStep('add_vertex', 'v4', position=CanvasPoint((100.0, 230.0))),
            DcelStep('add_edge', 'v1', 'v2'),
            DcelStep('add_edge', 'v2', 'v3'),
            DcelStep('add_edge', 'v3', 'v4'),
            DcelStep('add_edge', 'v4', 'v1'),
            DcelStep('add_edge', 'v2', 'v4'),
            DcelStep('subdivide', 'v2', 'v4', newNode='v24'),
            DcelStep('subdivide', 'v1', 'v2', newNode='v12'),
            DcelStep('subdivide', 'v3', 'v4', newNode='v34'),
        ]),
    )

    largePreset: DcelDataSet = DcelDataSet(
        name='Large (2x3 Planar Grid)',
        plannedSteps=DcelSteps([
            DcelStep('add_vertex', 'n1', position=CanvasPoint((120.0, 110.0))),
            DcelStep('add_vertex', 'n2', position=CanvasPoint((280.0, 110.0))),
            DcelStep('add_vertex', 'n3', position=CanvasPoint((440.0, 110.0))),
            DcelStep('add_vertex', 'n4', position=CanvasPoint((120.0, 350.0))),
            DcelStep('add_vertex', 'n5', position=CanvasPoint((280.0, 350.0))),
            DcelStep('add_vertex', 'n6', position=CanvasPoint((440.0, 350.0))),
            DcelStep('add_edge', 'n1', 'n2'),
            DcelStep('add_edge', 'n2', 'n3'),
            DcelStep('add_edge', 'n4', 'n5'),
            DcelStep('add_edge', 'n5', 'n6'),
            DcelStep('add_edge', 'n1', 'n4'),
            DcelStep('add_edge', 'n2', 'n5'),
            DcelStep('add_edge', 'n3', 'n6'),
            DcelStep('subdivide', 'n1', 'n2', newNode='n12'),
            DcelStep('subdivide', 'n2', 'n5', newNode='n25'),
            DcelStep('subdivide', 'n5', 'n6', newNode='n56'),
            DcelStep('subdivide', 'n4', 'n5', newNode='n45'),
        ]),
    )

    return [emptyPreset, smallPreset, mediumPreset, largePreset]
