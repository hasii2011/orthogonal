
from typing import Optional

from wx import Point
from wx import Window
from wx import EVT_MOTION
from wx import MouseEvent

from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeCanvas

from tests.demo.dcelvisualizer.DcelCircleShape import DcelCircleShape
from tests.demo.dcelvisualizer.DcelRectangleShape import DcelRectangleShape


class DcelShapeCanvas(ShapeCanvas):
    """
    ShapeCanvas subclass that relays empty-space left clicks to the top-level frame.
    """

    def __init__(self, parent: Window, windowId: int):
        """
        Initialize the canvas and bind mouse motion for dynamic shape tooltips.

        Args:
            parent: Parent container widget.
            windowId: Control identifier.
        """
        super().__init__(parent, windowId)
        self._currentToolTipText: str = ''
        self.Bind(EVT_MOTION, self.onMouseMove)

    def onMouseMove(self, evt: MouseEvent):
        """
        Inspect the shape under cursor on mouse motion and update tooltip dynamically.

        Args:
            evt: Motion mouse event.
        """
        logicalPos: Point = self.CalcUnscrolledPosition(evt.GetPosition())
        shape: Optional[Shape]
        shape, _ = self.FindShape(float(logicalPos.x), float(logicalPos.y))
        if isinstance(shape, (DcelCircleShape, DcelRectangleShape)):
            tooltipText: str = shape.tooltipText
            if self._currentToolTipText != tooltipText:
                self._currentToolTipText = tooltipText
                self.SetToolTip(tooltipText)
        else:
            if self._currentToolTipText != '':
                self._currentToolTipText = ''
                self.UnsetToolTip()
        evt.Skip()

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
