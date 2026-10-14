
from dataclasses import dataclass

from tests.demo.dcelvisualizer.DcelStep import DcelSteps


@dataclass(frozen=True)
class DcelDataSet:
    """
    Encapsulates a planar graph preset and its planned building steps.
    """
    name:         str
    plannedSteps: DcelSteps
