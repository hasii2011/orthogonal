
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

    def OnEndDragLeft(self, x: float, y: float, keys: int = 0, attachment: int = 0):
        """
        Complete node drag and schedule a DCEL canvas refresh at the new position.

        Args:
            x: Final X drag coordinate.
            y: Final Y drag coordinate.
            keys: Modifier key bitmask.
            attachment: Attachment point index.
        """
        previousHandler: Optional[ShapeEvtHandler] = self.GetPreviousHandler()
        if previousHandler is not None:
            previousHandler.OnEndDragLeft(x, y, keys, attachment)

        shape: Optional[Shape] = self.GetShape()
        if shape is not None:
            from tests.demo.dcelvisualizer.DcelVisualizerFrame import DcelVisualizerFrame

            newX:     float = float(shape.GetX())
            newY:     float = float(shape.GetY())
            topFrame: Window = self._canvas.GetTopLevelParent()

            assert isinstance(topFrame, DcelVisualizerFrame), 'Top-level parent must be DcelVisualizerFrame'

            visualizerFrame: DcelVisualizerFrame = topFrame
            CallAfter(lambda: visualizerFrame.onVertexMoved(self._nodeId, newX, newY))
