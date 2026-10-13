
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Optional

from math import sqrt

from wx import ALL  # type: ignore[import-untyped]
from wx import Pen
from wx import Brush
from wx import Font
from wx import Colour
from wx import EXPAND
from wx import BoxSizer
from wx import ID_ANY
from wx import Panel
from wx import Window
from wx import VERTICAL
from wx import FONTFAMILY_SWISS
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD

from wx.lib.ogl import ARROW_ARROW  # type: ignore[import-untyped]
from wx.lib.ogl import ARROW_POSITION_END

from wx.lib.ogl import CircleShape
from wx.lib.ogl import Diagram
from wx.lib.ogl import LineShape
from wx.lib.ogl import RectangleShape

from orthogonal.TopologyTypes import FaceId
from orthogonal.TopologyTypes import NodeId
from orthogonal.doublyConnectedEdgeList.DoublyConnectedEdgeList import DoublyConnectedEdgeList
from orthogonal.doublyConnectedEdgeList.Face import Face

from tests.demo.dcelvisualizer.DcelShapeCanvas import DcelShapeCanvas
from tests.demo.dcelvisualizer.VertexShapeEvtHandler import VertexShapeEvtHandler

VERTEX_CIRCLE_DIAMETER:   float = 44.0
EDGE_SPLINE_OFFSET:       float = 18.0
EDGE_LABEL_WIDTH:         float = 72.0
EDGE_LABEL_HEIGHT:        float = 22.0
EDGE_LABEL_CORNER_RADIUS: float = 3.0
EDGE_ARROW_SIZE:          float = 11.0
FACE_BADGE_WIDTH:         float = 96.0
FACE_BADGE_HEIGHT:        float = 24.0
FACE_BADGE_CORNER_RADIUS: float = 4.0
FACE_BADGE_OFFSET_Y:      float = 18.0

VERTEX_FONT_SIZE:     int = 12
EDGE_LABEL_FONT_SIZE: int = 12

FACE_BADGE_FONT_SIZE: int = 12

class DcelCanvasPanel(Panel):
    """
    Canvas panel hosting wx.lib.ogl.ShapeCanvas for vector graph rendering.
    """

    def __init__(self, parent: Window):
        """
        Construct the OGL canvas panel.

        Args:
            parent: Parent window widget.
        """
        super().__init__(parent, ID_ANY)

        self._diagram: Diagram = Diagram()
        self._canvas: DcelShapeCanvas = DcelShapeCanvas(self, ID_ANY)
        self._canvas.SetDiagram(self._diagram)
        self._canvas.SetBackgroundColour(Colour(255, 255, 255))
        self._diagram.SetCanvas(self._canvas)

        self._positions: Dict[NodeId, Tuple[float, float]] = {}
        self._shapeMap:  Dict[NodeId, CircleShape]         = {}

        self._edgeShapes: List[Tuple[NodeId, NodeId, LineShape, RectangleShape]] = []
        self._faceShapes: List[Tuple[List[NodeId], float, RectangleShape]]       = []

        panelSizer: BoxSizer = BoxSizer(VERTICAL)
        panelSizer.Add(self._canvas, 1, EXPAND | ALL, 0)
        self.SetSizer(panelSizer)

    def renderDcel(
        self,
        dcel: DoublyConnectedEdgeList,
        positions: Dict[NodeId, Tuple[float, float]],
        insertedNode: Optional[NodeId],
    ):
        """
        Clear and redraw the DCEL vertices, half-edge arcs, and face centroids on the OGL canvas.

        Args:
            dcel: Current DoublyConnectedEdgeList instance.
            positions: Coordinate lookup for all present vertices.
            insertedNode: Identifier of recently inserted vertex to highlight, if any.
        """
        self._diagram.DeleteAllShapes()
        self._positions = dict(positions)
        self._shapeMap.clear()
        self._edgeShapes.clear()
        self._faceShapes.clear()

        shapeMap: Dict[NodeId, CircleShape] = {}
        for nodeId, _vertexInstance in dcel.vertexDict.items():
            pos: Tuple[float, float] = positions.get(nodeId, (250.0, 200.0))
            circle: CircleShape = CircleShape(VERTEX_CIRCLE_DIAMETER)
            circle.SetX(pos[0])
            circle.SetY(pos[1])
            circle.AddText(str(nodeId))
            circle.SetFont(Font(VERTEX_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD))
            circle.SetTextColour('WHITE')

            if nodeId == insertedNode:
                circle.SetBrush(Brush(Colour(244, 63, 94)))
            else:
                circle.SetBrush(Brush(Colour(96, 165, 250)))

            self._diagram.AddShape(circle)
            circle.SetCanvas(self._canvas)
            evtHandler: VertexShapeEvtHandler = VertexShapeEvtHandler(nodeId, self._canvas)
            evtHandler.SetShape(circle)
            evtHandler.SetPreviousHandler(circle.GetEventHandler())
            circle.SetEventHandler(evtHandler)
            shapeMap[nodeId] = circle
            self._shapeMap[nodeId] = circle

        for _edgeKey, halfEdge in dcel.halfEdgeDict.items():
            uId: NodeId = halfEdge.origin.id
            vId: NodeId = halfEdge.twin.origin.id

            if uId in shapeMap and vId in shapeMap:
                c1: CircleShape = shapeMap[uId]
                c2: CircleShape = shapeMap[vId]

                posU: Tuple[float, float] = positions.get(uId, (0.0, 0.0))
                posV: Tuple[float, float] = positions.get(vId, (0.0, 0.0))

                deltaX: float = posV[0] - posU[0]
                deltaY: float = posV[1] - posU[1]
                distance: float = sqrt(deltaX * deltaX + deltaY * deltaY)

                normX: float = 0.0
                normY: float = 0.0
                if distance > 0.001:
                    normX = -deltaY / distance
                    normY = deltaX / distance

                midX: float = (posU[0] + posV[0]) / 2.0 + normX * EDGE_SPLINE_OFFSET
                midY: float = (posU[1] + posV[1]) / 2.0 + normY * EDGE_SPLINE_OFFSET

                line: LineShape = LineShape()
                line.MakeLineControlPoints(3)
                line.SetSpline(True)
                ctrlPoints: Any = line.GetLineControlPoints()
                if len(ctrlPoints) >= 2:
                    ctrlPoints[1].x = midX
                    ctrlPoints[1].y = midY

                line.AddArrow(ARROW_ARROW, ARROW_POSITION_END, EDGE_ARROW_SIZE, 0.0, '')
                c1.AddLine(line, c2)
                self._diagram.AddShape(line)

                edgeLabel: RectangleShape = RectangleShape(EDGE_LABEL_WIDTH, EDGE_LABEL_HEIGHT)
                edgeLabel.SetCornerRadius(EDGE_LABEL_CORNER_RADIUS)
                edgeLabel.SetX(midX)
                edgeLabel.SetY(midY)
                edgeLabel.AddText(f'{uId}->{vId}')
                edgeLabel.SetFont(Font(EDGE_LABEL_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD))
                edgeLabel.SetBrush(Brush(Colour(255, 255, 255)))
                edgeLabel.SetPen(Pen(Colour(203, 213, 225), 1))
                edgeLabel.SetTextColour('BLACK')
                edgeLabel.SetDraggable(False)
                self._diagram.AddShape(edgeLabel)
                edgeLabel.SetCanvas(self._canvas)
                self._edgeShapes.append((uId, vId, line, edgeLabel))

        faceItems: List[Tuple[FaceId, Face]] = list(dcel.faceDict.items())
        for idx, (faceId, faceInstance) in enumerate(faceItems):
            if faceInstance.nodes_id:
                sumX: float = 0.0
                sumY: float = 0.0
                validPoints: int = 0
                for cycleNode in faceInstance.nodes_id:
                    if cycleNode in positions:
                        sumX += positions[cycleNode][0]
                        sumY += positions[cycleNode][1]
                        validPoints += 1
                if validPoints > 0:
                    centroidX: float = sumX / float(validPoints)
                    centroidY: float = sumY / float(validPoints)
                    offsetY: float = -FACE_BADGE_OFFSET_Y if idx == 0 else FACE_BADGE_OFFSET_Y
                    faceBadge: RectangleShape = RectangleShape(FACE_BADGE_WIDTH, FACE_BADGE_HEIGHT)
                    faceBadge.SetCornerRadius(FACE_BADGE_CORNER_RADIUS)
                    faceBadge.SetX(centroidX)
                    faceBadge.SetY(centroidY + offsetY)
                    labelText: str = str(faceId) if idx == 0 else f'{faceId} (outer)'
                    faceBadge.AddText(labelText)
                    faceBadge.SetFont(Font(FACE_BADGE_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD))
                    faceBadge.SetBrush(Brush(Colour(241, 245, 249)))
                    faceBadge.SetPen(Pen(Colour(203, 213, 225), 1))
                    faceBadge.SetTextColour('BLACK')
                    faceBadge.SetDraggable(False)
                    self._diagram.AddShape(faceBadge)
                    faceBadge.SetCanvas(self._canvas)
                    self._faceShapes.append((list(faceInstance.nodes_id), offsetY, faceBadge))

        self._diagram.ShowAll(True)
        self._canvas.Draw()
        self._canvas.Refresh()

    def dragVertex(self, nodeId: NodeId, newX: float, newY: float):
        """
        Update a dragged vertex, its incident half-edge splines/labels, and face badges in-place.

        Args:
            nodeId: Identifier of the vertex being dragged.
            newX: New X coordinate on canvas.
            newY: New Y coordinate on canvas.
        """
        self._positions[nodeId] = (newX, newY)
        if nodeId in self._shapeMap:
            circle: CircleShape = self._shapeMap[nodeId]
            circle.SetX(newX)
            circle.SetY(newY)

        for uId, vId, line, edgeLabel in self._edgeShapes:
            if uId == nodeId or vId == nodeId:
                posU: Tuple[float, float] = self._positions.get(uId, (0.0, 0.0))
                posV: Tuple[float, float] = self._positions.get(vId, (0.0, 0.0))
                deltaX: float = posV[0] - posU[0]
                deltaY: float = posV[1] - posU[1]
                distance: float = sqrt(deltaX * deltaX + deltaY * deltaY)
                normX: float = 0.0
                normY: float = 0.0
                if distance > 0.001:
                    normX = -deltaY / distance
                    normY = deltaX / distance
                midX: float = (posU[0] + posV[0]) / 2.0 + normX * EDGE_SPLINE_OFFSET
                midY: float = (posU[1] + posV[1]) / 2.0 + normY * EDGE_SPLINE_OFFSET
                ctrlPoints: Any = line.GetLineControlPoints()
                if len(ctrlPoints) >= 2:
                    ctrlPoints[1].x = midX
                    ctrlPoints[1].y = midY
                endPoints: Any = line.FindLineEndPoints()
                if endPoints is not None:
                    line.SetEnds(endPoints[0], endPoints[1], endPoints[2], endPoints[3])
                edgeLabel.SetX(midX)
                edgeLabel.SetY(midY)

        for cycleNodes, offsetY, faceBadge in self._faceShapes:
            if nodeId in cycleNodes:
                sumX: float = 0.0
                sumY: float = 0.0
                validPoints: int = 0
                for cycleNode in cycleNodes:
                    if cycleNode in self._positions:
                        sumX += self._positions[cycleNode][0]
                        sumY += self._positions[cycleNode][1]
                        validPoints += 1
                if validPoints > 0:
                    faceBadge.SetX(sumX / float(validPoints))
                    faceBadge.SetY(sumY / float(validPoints) + offsetY)

        self._canvas.Draw()
        self._canvas.Refresh()
