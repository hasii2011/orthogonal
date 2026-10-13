
from typing import List

from tests.demo.dcelvisualizer.DcelStep import DcelStep


class DcelDataSet:
    """
    Encapsulates a planar graph preset and its planned building steps.
    """

    def __init__(
        self,
        name: str,
        plannedSteps: List[DcelStep],
    ):
        """
        Initialize dataset configuration.

        Args:
            name: Human-readable dataset name.
            plannedSteps: Sequence of DcelStep operations starting from an empty DCEL.
        """
        self._name: str = name
        self._plannedSteps: List[DcelStep] = plannedSteps

    @property
    def name(self) -> str:
        """
        Get the dataset name.

        Returns:
            Dataset name string.
        """
        return self._name

    @property
    def plannedSteps(self) -> List[DcelStep]:
        """
        Get pre-configured building steps.

        Returns:
            List of DcelStep operation specifications.
        """
        return self._plannedSteps
