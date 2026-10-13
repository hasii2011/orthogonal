
from typing import Optional

from wx import CallAfter  # type: ignore[import-untyped]
from wx import Window

from wx.lib.ogl import Shape  # type: ignore[import-untyped]
from wx.lib.ogl import ShapeCanvas
from wx.lib.ogl import ShapeEvtHandler

from orthogonal.TopologyTypes import NodeId


class VertexShapeEvtHandler(ShapeEvtHandler):
    """
    Event handler for vertex CircleShapes to persist dragged node positions.
    """

    def __init__(self, nodeId: NodeId, canvas: ShapeCanvas):
        """
        Initialize the vertex event handler.

        Args:
            nodeId: Identifier of the vertex represented by this shape.
            canvas: Hosting ShapeCanvas instance.
        """
        super().__init__()
        self._nodeId: NodeId = nodeId
        self._canvas: ShapeCanvas = canvas
        self._dragOffsetX: float = 0.0
        self._dragOffsetY: float = 0.0

    def OnBeginDragLeft(self, x: float, y: float, keys: int = 0, attachment: int = 0):
        """
        Begin dragging the vertex shape and capture mouse input.

        Args:
            x: Initial X drag coordinate.
            y: Initial Y drag coordinate.
            keys: Modifier key bitmask.
            attachment: Attachment point index.
        """
        shape: Optional[Shape] = self.GetShape()
        if shape is not None:
            self._dragOffsetX = float(shape.GetX()) - float(x)
            self._dragOffsetY = float(shape.GetY()) - float(y)

        if not self._canvas.HasCapture():
            self._canvas.CaptureMouse()

    def OnDragLeft(self, draw: bool, x: float, y: float, keys: int = 0, attachment: int = 0):
        """
        Update vertex and connected edge positions live while dragging.

        Args:
            draw: True on the draw pass of the drag step, False on the erase pass.
            x: Current X drag coordinate.
            y: Current Y drag coordinate.
            keys: Modifier key bitmask.
            attachment: Attachment point index.
        """
        if not draw:
            return

        from tests.demo.dcelvisualizer.DcelVisualizerFrame import DcelVisualizerFrame

        newX: float = float(x) + self._dragOffsetX
        newY: float = float(y) + self._dragOffsetY
        topFrame: Window = self._canvas.GetTopLevelParent()

        assert isinstance(topFrame, DcelVisualizerFrame), 'Top-level parent must be DcelVisualizerFrame'

        topFrame.onVertexDragged(self._nodeId, newX, newY)

    def OnEndDragLeft(self, x: float, y: float, keys: int = 0, attachment: int = 0):
        """
        Complete node drag and schedule a DCEL canvas refresh at the new position.

        Args:
            x: Final X drag coordinate.
            y: Final Y drag coordinate.
            keys: Modifier key bitmask.
            attachment: Attachment point index.
        """
        if self._canvas.HasCapture():
            self._canvas.ReleaseMouse()

        shape: Optional[Shape] = self.GetShape()
        if shape is not None:
            from tests.demo.dcelvisualizer.DcelVisualizerFrame import DcelVisualizerFrame

            newX:     float = float(x) + self._dragOffsetX
            newY:     float = float(y) + self._dragOffsetY
            topFrame: Window = self._canvas.GetTopLevelParent()

            assert isinstance(topFrame, DcelVisualizerFrame), 'Top-level parent must be DcelVisualizerFrame'

            visualizerFrame: DcelVisualizerFrame = topFrame
            CallAfter(lambda: visualizerFrame.onVertexMoved(self._nodeId, newX, newY))
