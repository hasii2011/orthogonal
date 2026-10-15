
"""
VisualizerCanvas subclass delegating empty-space canvas clicks to VisualizerFrame.
"""

from wx import Window

from tests.demo.BaseVisualizerCanvas import BaseVisualizerCanvas


class VisualizerCanvas(BaseVisualizerCanvas):
    """
    ShapeCanvas subclass that relays empty-space left clicks to the top-level frame.
    """

    def OnLeftClick(self, x: float, y: float, keys: int = 0):
        """
        Handle left click on unoccupied canvas background.

        Args:
            x: Logical X coordinate of click.
            y: Logical Y coordinate of click.
            keys: Modifier key bitmask.
        """
        from tests.demo.dcelvisualizer.VisualizerFrame import VisualizerFrame

        topFrame: Window = self.GetTopLevelParent()

        assert isinstance(topFrame, VisualizerFrame), 'Top-level parent must be VisualizerFrame'

        topFrame.onCanvasClick(float(x), float(y))
