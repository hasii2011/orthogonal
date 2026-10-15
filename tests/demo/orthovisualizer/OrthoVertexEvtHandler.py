"""
Event handler for shapes (vertices and face badges) in the Orthogonalization visualizer to support live interactive dragging.
"""

from typing import Callable
from typing import Optional

from wx import CallAfter

from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeCanvas
from wx.lib.ogl import ShapeEvtHandler

from orthogonal.TopologyTypes import FaceId
from orthogonal.TopologyTypes import NodeId

ShapeElementId = NodeId | FaceId


class OrthoShapeEvtHandler(ShapeEvtHandler):
    """
    Event handler for vector shapes to persist and redraw dragged positions in OrthoVisualizer.
    """

    def __init__(
        self,
        elementId:         ShapeElementId,
        canvas:            ShapeCanvas,
        onPositionDragged: Callable[[ShapeElementId, float, float], None],
        onPositionMoved:   Callable[[ShapeElementId, float, float], None],
    ):
        """
        Initialize the shape event handler.

        Args:
            elementId: Identifier of the vertex or face represented by this shape.
            canvas: Hosting ShapeCanvas instance.
            onPositionDragged: Callback receiving (elementId, newX, newY) live during mouse drag.
            onPositionMoved: Callback receiving (elementId, newX, newY) once mouse drag ends.
        """
        super().__init__()
        self._elementId:         ShapeElementId                                       = elementId
        self._canvas:            ShapeCanvas                                          = canvas
        self._onPositionDragged: Callable[[ShapeElementId, float, float], None]       = onPositionDragged
        self._onPositionMoved:   Callable[[ShapeElementId, float, float], None]       = onPositionMoved
        self._dragOffsetX:       float                                                = 0.0
        self._dragOffsetY:       float                                                = 0.0

    def OnBeginDragLeft(self, x: float, y: float, keys: int = 0, attachment: int = 0):
        """
        Begin dragging the shape and capture mouse input.

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
        Update shape and connected arrows live while dragging.

        Args:
            draw: True on the draw pass of the drag step, False on the erase pass.
            x: Current X drag coordinate.
            y: Current Y drag coordinate.
            keys: Modifier key bitmask.
            attachment: Attachment point index.
        """
        if not draw:
            return

        newX: float = float(x) + self._dragOffsetX
        newY: float = float(y) + self._dragOffsetY
        self._onPositionDragged(self._elementId, newX, newY)

    def OnEndDragLeft(self, x: float, y: float, keys: int = 0, attachment: int = 0):
        """
        Complete shape drag and trigger a final diagram redraw.

        Args:
            x: Final X drag coordinate.
            y: Final Y drag coordinate.
            keys: Modifier key bitmask.
            attachment: Attachment point index.
        """
        if self._canvas.HasCapture():
            self._canvas.ReleaseMouse()

        newX: float = float(x) + self._dragOffsetX
        newY: float = float(y) + self._dragOffsetY
        CallAfter(lambda: self._onPositionMoved(self._elementId, newX, newY))


OrthoVertexEvtHandler = OrthoShapeEvtHandler
