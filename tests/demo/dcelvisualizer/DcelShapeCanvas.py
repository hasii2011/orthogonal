
from wx import Window  # type: ignore[import-untyped]
from wx.lib.ogl import ShapeCanvas  # type: ignore[import-untyped]


class DcelShapeCanvas(ShapeCanvas):
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
        from tests.demo.dcelvisualizer.DcelVisualizerFrame import DcelVisualizerFrame

        topFrame: Window = self.GetTopLevelParent()

        assert isinstance(topFrame, DcelVisualizerFrame), 'Top-level parent must be DcelVisualizerFrame'

        topFrame.onCanvasClick(float(x), float(y))
