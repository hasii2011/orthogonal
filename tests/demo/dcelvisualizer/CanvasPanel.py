
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Optional

from math import sqrt

from wx import ID_ANY
from wx import FONTWEIGHT_BOLD
from wx import FONTSTYLE_NORMAL
from wx import FONTFAMILY_SWISS

from wx import Pen
from wx import Font
from wx import Brush
from wx import Colour
from wx import Window

from wx.lib.ogl import ARROW_ARROW
from wx.lib.ogl import ARROW_POSITION_END

from wx.lib.ogl import Diagram
from wx.lib.ogl import LineShape

from wx.lib.sized_controls import SizedPanel

from orthogonal.TopologyTypes import FaceId
from orthogonal.TopologyTypes import NodeId

from orthogonal.doublyConnectedEdgeList.Face import Face
from orthogonal.doublyConnectedEdgeList.DoublyConnectedEdgeList import DoublyConnectedEdgeList
from tests.demo.CanvasTypes import CanvasPoint

from tests.demo.dcelvisualizer.VisualizerTypes import NodePositions
from tests.demo.dcelvisualizer.VisualizerTypes import CycleNodes
from tests.demo.dcelvisualizer.VisualizerTypes import EdgeShapeEntry
from tests.demo.dcelvisualizer.VisualizerTypes import FaceShapeEntry

from tests.demo.dcelvisualizer.VisualizerCanvas import VisualizerCanvas
from tests.demo.dcelvisualizer.shapes.VertexShape import VertexShape
from tests.demo.dcelvisualizer.shapes.BadgeShape import BadgeShape
from tests.demo.dcelvisualizer.VertexShapeEvtHandler import VertexShapeEvtHandler

from tests.demo.CanvasConstants import BORDER_LIGHT_GREY
from tests.demo.CanvasConstants import CANVAS_BACKGROUND_COLOUR
from tests.demo.CanvasConstants import DEFAULT_NODE_COLOUR
from tests.demo.CanvasConstants import INSERTED_NODE_COLOUR
from tests.demo.CanvasConstants import VERTEX_FONT_SIZE

NODE_SPREAD_FACTOR:       float = 1.35
DEFAULT_NODE_X:           float = 250.0
DEFAULT_NODE_Y:           float = 200.0

VERTEX_CIRCLE_DIAMETER:   float = 44.0
EDGE_SPLINE_OFFSET:       float = 18.0
EDGE_LABEL_WIDTH:         float = 72.0
EDGE_LABEL_HEIGHT:        float = 22.0
EDGE_LABEL_CORNER_RADIUS: float = 3.0
EDGE_LABEL_BORDER_WIDTH:  int   = 1
EDGE_ARROW_SIZE:          float = 11.0
FACE_BADGE_WIDTH:         float = 96.0
FACE_BADGE_HEIGHT:        float = 24.0
FACE_BADGE_CORNER_RADIUS: float = 4.0
FACE_BADGE_BORDER_WIDTH:  int   = 1
FACE_BADGE_OFFSET_Y:      float = 18.0

MIN_EDGE_DISTANCE:        float = 0.001

EDGE_LABEL_FONT_SIZE: int = 12
FACE_BADGE_FONT_SIZE: int = 12

EDGE_LABEL_BACKGROUND_COLOUR: Colour = Colour(255, 255, 255)
EDGE_LABEL_BORDER_COLOUR:     Colour = BORDER_LIGHT_GREY
FACE_BADGE_BACKGROUND_COLOUR: Colour = Colour(241, 245, 249)
FACE_BADGE_BORDER_COLOUR:     Colour = BORDER_LIGHT_GREY

class CanvasPanel(SizedPanel):
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

        self._diagram: Diagram          = Diagram()
        self._canvas:  VisualizerCanvas = VisualizerCanvas(self, ID_ANY)

        # noinspection PyUnresolvedReferences
        self._canvas.SetSizerProps(expand=True, proportion=1, border=('all', 0))
        self._canvas.SetDiagram(self._diagram)
        self._canvas.SetBackgroundColour(CANVAS_BACKGROUND_COLOUR)
        self._diagram.SetCanvas(self._canvas)

        self._positions: NodePositions              = NodePositions({})
        self._shapeMap:  Dict[NodeId, VertexShape]  = {}

        self._edgeShapes: List[EdgeShapeEntry] = []
        self._faceShapes: List[FaceShapeEntry] = []

    def renderDcel(
        self,
        dcel: DoublyConnectedEdgeList,
        positions: NodePositions,
        insertedNode: Optional[NodeId],
    ):
        """
        Clear and redraw the DCEL vertices, half-edge arcs, and face badges on the OGL canvas.

        Args:
            dcel: Current DoublyConnectedEdgeList instance.
            positions: Coordinate lookup for all present vertices.
            insertedNode: Identifier of recently inserted vertex to highlight, if any.
        """
        self._diagram.DeleteAllShapes()
        self._positions = NodePositions(dict(positions))
        self._shapeMap.clear()
        self._edgeShapes.clear()
        self._faceShapes.clear()

        self._renderVertices(dcel, positions, insertedNode)
        self._renderHalfEdges(dcel, positions)
        self._renderFaces(dcel, positions)

        self._diagram.ShowAll(True)
        self._canvas.Draw()
        self._canvas.Refresh()

    def _renderVertices(
        self,
        dcel: DoublyConnectedEdgeList,
        positions: NodePositions,
        insertedNode: Optional[NodeId],
    ):
        """
        Render vertex circular shapes with event handlers and tooltips.

        Args:
            dcel: Current DoublyConnectedEdgeList instance.
            positions: Coordinate lookup for all present vertices.
            insertedNode: Identifier of recently inserted vertex to highlight, if any.
        """
        for nodeId, _vertexInstance in dcel.vertexDict.items():

            pos: CanvasPoint = positions.get(nodeId, CanvasPoint((DEFAULT_NODE_X * NODE_SPREAD_FACTOR, DEFAULT_NODE_Y * NODE_SPREAD_FACTOR)))
            circle: VertexShape = VertexShape(VERTEX_CIRCLE_DIAMETER)
            circle.SetX(pos[0])
            circle.AddText(str(nodeId))
            circle.SetY(pos[1])
            circle.SetFont(Font(VERTEX_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD))
            circle.SetTextColour('WHITE')

            if nodeId == insertedNode:
                circle.SetBrush(Brush(INSERTED_NODE_COLOUR))
            else:
                circle.SetBrush(Brush(DEFAULT_NODE_COLOUR))

            circle.tooltipText = f'Vertex {nodeId}\nPosition: ({int(pos[0])}, {int(pos[1])})'
            self._diagram.AddShape(circle)
            circle.SetCanvas(self._canvas)

            evtHandler: VertexShapeEvtHandler = VertexShapeEvtHandler(
                nodeId,
                self._canvas,
                self._onVertexDragged,
                self._onVertexMoved,
            )
            evtHandler.SetShape(circle)
            evtHandler.SetPreviousHandler(circle.GetEventHandler())

            circle.SetEventHandler(evtHandler)
            self._shapeMap[nodeId] = circle

    def _renderHalfEdges(
        self,
        dcel: DoublyConnectedEdgeList,
        positions: NodePositions,
    ):
        """
        Render directed half-edge splines and midpoint label badges with tooltips.

        Args:
            dcel: Current DoublyConnectedEdgeList instance.
            positions: Coordinate lookup for all present vertices.
        """
        for _edgeKey, halfEdge in dcel.halfEdgeDict.items():
            uId: NodeId = halfEdge.origin.id
            vId: NodeId = halfEdge.twin.origin.id

            if uId in self._shapeMap and vId in self._shapeMap:
                c1: VertexShape = self._shapeMap[uId]
                c2: VertexShape = self._shapeMap[vId]

                posU: CanvasPoint = positions.get(uId, CanvasPoint((0.0, 0.0)))
                posV: CanvasPoint = positions.get(vId, CanvasPoint((0.0, 0.0)))

                deltaX: float = posV[0] - posU[0]
                deltaY: float = posV[1] - posU[1]
                distance: float = sqrt(deltaX * deltaX + deltaY * deltaY)

                normX: float = 0.0
                normY: float = 0.0
                if distance > MIN_EDGE_DISTANCE:
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

                edgeLabel: BadgeShape = BadgeShape(EDGE_LABEL_WIDTH, EDGE_LABEL_HEIGHT)
                edgeLabel.SetCornerRadius(EDGE_LABEL_CORNER_RADIUS)
                edgeLabel.SetX(midX)
                edgeLabel.SetY(midY)
                edgeLabel.AddText(f'{uId}->{vId}')
                edgeLabel.SetFont(Font(EDGE_LABEL_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD))
                edgeLabel.SetBrush(Brush(EDGE_LABEL_BACKGROUND_COLOUR))
                edgeLabel.SetPen(Pen(EDGE_LABEL_BORDER_COLOUR, EDGE_LABEL_BORDER_WIDTH))
                edgeLabel.SetTextColour('BLACK')
                edgeLabel.SetDraggable(False)
                edgeLabel.tooltipText = f'Half-Edge: {uId} -> {vId}'
                self._diagram.AddShape(edgeLabel)
                edgeLabel.SetCanvas(self._canvas)
                self._edgeShapes.append(EdgeShapeEntry((uId, vId, line, edgeLabel)))

    def _calculateOuterFaceId(
        self,
        dcel: DoublyConnectedEdgeList,
        positions: NodePositions,
    ) -> Optional[FaceId]:
        """
        Identify the outer face using the Shoelace signed area formula across cycle nodes.

        Args:
            dcel: Current DoublyConnectedEdgeList instance.
            positions: Coordinate lookup for all present vertices.

        Returns:
            The FaceId of the outer unbounded face if identified, None otherwise.
        """
        faceSignedAreas: Dict[FaceId, float] = {}
        for faceId, faceInstance in dcel.faceDict.items():

            cycleNodes: CycleNodes = CycleNodes(list(faceInstance.nodes_id))
            if len(cycleNodes) >= 3:
                areaSum: float = 0.0
                nodeCount: int = len(cycleNodes)
                for i in range(nodeCount):
                    uNode: NodeId = cycleNodes[i]
                    vNode: NodeId = cycleNodes[(i + 1) % nodeCount]
                    if uNode in positions and vNode in positions:
                        areaSum += positions[uNode][0] * positions[vNode][1] - positions[vNode][0] * positions[uNode][1]
                faceSignedAreas[faceId] = areaSum / 2.0

        if not faceSignedAreas:
            return None

        positiveCount: int = sum(1 for a in faceSignedAreas.values() if a > 0)
        negativeCount: int = sum(1 for a in faceSignedAreas.values() if a < 0)
        if positiveCount > 0 and negativeCount > 0:
            return min(faceSignedAreas, key=lambda fid: faceSignedAreas[fid]) if positiveCount > negativeCount else max(faceSignedAreas, key=lambda fid: faceSignedAreas[fid])
        return None

    def _renderFaces(
        self,
        dcel: DoublyConnectedEdgeList,
        positions: NodePositions,
    ):
        """
        Render face label badges positioned at face centers and attach boundary cycle tooltips.

        Args:
            dcel: Current DoublyConnectedEdgeList instance.
            positions: Coordinate lookup for all present vertices.
        """
        outerFaceId: Optional[FaceId]          = self._calculateOuterFaceId(dcel, positions)
        faceItems:   List[Tuple[FaceId, Face]] = list(dcel.faceDict.items())
        for idx, (faceId, faceInstance) in enumerate(faceItems):

            cycleNodes: CycleNodes            = CycleNodes(list(faceInstance.nodes_id))
            faceCenter: Optional[CanvasPoint] = self._computeFaceCenter(cycleNodes, positions)
            if faceCenter is not None:
                offsetY: float
                if idx == 0:
                    offsetY = -FACE_BADGE_OFFSET_Y
                else:
                    offsetY = FACE_BADGE_OFFSET_Y
                isOuter: bool = (faceId == outerFaceId)
                faceBadge: BadgeShape = self._createFaceBadge(
                    faceId,
                    faceInstance,
                    faceCenter[0],
                    faceCenter[1] + offsetY,
                    isOuter,
                )
                self._diagram.AddShape(faceBadge)
                faceBadge.SetCanvas(self._canvas)
                self._faceShapes.append(FaceShapeEntry((cycleNodes, offsetY, faceBadge)))

        self._diagram.ShowAll(True)
        self._canvas.Draw()
        self._canvas.Refresh()

    def _computeFaceCenter(
        self,
        cycleNodes: CycleNodes,
        positions: NodePositions,
    ) -> Optional[CanvasPoint]:
        """
        Compute arithmetic mean center coordinates of a face boundary cycle.

        Args:
            cycleNodes: Sequence of vertex node IDs forming face boundary.
            positions: Coordinate lookup for all present vertices.

        Returns:
            (centerX, centerY) tuple if valid positions exist, None otherwise.
        """
        sumX:        float = 0.0
        sumY:        float = 0.0
        validPoints: int   = 0

        for cycleNode in cycleNodes:

            if cycleNode in positions:
                sumX += positions[cycleNode][0]
                sumY += positions[cycleNode][1]
                validPoints += 1

        if validPoints > 0:
            return CanvasPoint((sumX / float(validPoints), sumY / float(validPoints)))
        return None

    def _createFaceBadge(
        self,
        faceId: FaceId,
        faceInstance: Face,
        x: float,
        y: float,
        isOuter: bool,
    ) -> BadgeShape:
        """
        Create and configure a styled face badge shape with tooltip.

        Args:
            faceId: Face identifier.
            faceInstance: Face DCEL instance.
            x: Canvas X coordinate.
            y: Canvas Y coordinate.
            isOuter: True if this face is the unbounded outer face.

        Returns:
            Configured BadgeShape instance.
        """
        faceBadge: BadgeShape = BadgeShape(FACE_BADGE_WIDTH, FACE_BADGE_HEIGHT)
        faceBadge.SetCornerRadius(FACE_BADGE_CORNER_RADIUS)
        faceBadge.SetX(x)
        faceBadge.SetY(y)

        labelText: str
        faceTypeStr: str
        if isOuter:
            labelText = f'{faceId} (outer)'
            faceTypeStr = 'Unbounded Outer Face'
        else:
            labelText = str(faceId)
            faceTypeStr = 'Bounded Internal Face'
        faceBadge.AddText(labelText)

        cycleStr: str = ' -> '.join(str(n) for n in faceInstance.nodes_id)

        faceBadge.tooltipText = f'Face {faceId} ({faceTypeStr})\nBoundary Cycle: [{cycleStr}]'
        faceBadge.SetFont(Font(FACE_BADGE_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD))
        faceBadge.SetBrush(Brush(FACE_BADGE_BACKGROUND_COLOUR))
        faceBadge.SetPen(Pen(FACE_BADGE_BORDER_COLOUR, FACE_BADGE_BORDER_WIDTH))
        faceBadge.SetTextColour('BLACK')
        faceBadge.SetDraggable(False)
        return faceBadge

    def dragVertex(self, nodeId: NodeId, newX: float, newY: float):
        """
        Update a dragged vertex, its incident half-edge splines/labels, and face badges in-place.

        Args:
            nodeId: Identifier of the vertex being dragged.
            newX: New X coordinate on canvas.
            newY: New Y coordinate on canvas.
        """
        self._positions[nodeId] = CanvasPoint((newX, newY))

        if nodeId in self._shapeMap:
            circle: VertexShape = self._shapeMap[nodeId]
            circle.SetX(newX)
            circle.SetY(newY)

        for uId, vId, line, edgeLabel in self._edgeShapes:

            if uId == nodeId or vId == nodeId:

                posU: CanvasPoint = self._positions.get(uId, CanvasPoint((0.0, 0.0)))
                posV: CanvasPoint = self._positions.get(vId, CanvasPoint((0.0, 0.0)))

                deltaX:   float = posV[0] - posU[0]
                deltaY:   float = posV[1] - posU[1]
                distance: float = sqrt(deltaX * deltaX + deltaY * deltaY)

                normX: float = 0.0
                normY: float = 0.0

                if distance > MIN_EDGE_DISTANCE:
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
                faceCenter: Optional[CanvasPoint] = self._computeFaceCenter(cycleNodes, self._positions)
                if faceCenter is not None:
                    faceBadge.SetX(faceCenter[0])
                    faceBadge.SetY(faceCenter[1] + offsetY)

        self._canvas.Draw()
        self._canvas.Refresh()

    def _onVertexDragged(self, elementId: NodeId | FaceId, newX: float, newY: float):
        """
        Callback invoked during drag to update node and incident elements in-place.

        Args:
            elementId: NodeId of the dragged vertex.
            newX: New X canvas coordinate.
            newY: New Y canvas coordinate.
        """
        self.dragVertex(str(elementId), newX, newY)

    def _onVertexMoved(self, elementId: NodeId | FaceId, newX: float, newY: float):
        """
        Callback invoked when drag ends to notify the top-level frame of the committed position.

        Args:
            elementId: NodeId of the dragged vertex.
            newX: New X canvas coordinate.
            newY: New Y canvas coordinate.
        """
        topFrame: Window = self.GetTopLevelParent()
        if hasattr(topFrame, 'onVertexMoved'):
            topFrame.onVertexMoved(str(elementId), newX, newY)

