"""
Interactive OGL canvas panel rendering Primal Graph, Dual Faces, FlowNet circulation arcs, and Orthogonal shapes.
"""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from math import sqrt

from wx import Brush
from wx import Colour
from wx import FONTFAMILY_SWISS
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD
from wx import Font
from wx import ID_ANY
from wx import Pen
from wx import TRANSPARENT_BRUSH
from wx import TRANSPARENT_PEN
from wx import Window

from wx.lib.ogl import ARROW_ARROW
from wx.lib.ogl import ARROW_POSITION_END
from wx.lib.ogl import Diagram
from wx.lib.ogl import LineShape

from wx.lib.sized_controls import SizedPanel

from orthogonal.TopologyTypes import FaceId
from orthogonal.TopologyTypes import FlowDict
from orthogonal.TopologyTypes import NodeId

from orthogonal.doublyConnectedEdgeList.Vertex import Vertex
from orthogonal.topologyShapeMetric.Orthogonalization import Orthogonalization
from orthogonal.topologyShapeMetric.Planarization import Planarization

from tests.demo.orthovisualizer.OrthoCanvas import OrthoCanvas
from tests.demo.orthovisualizer.OrthoVertexEvtHandler import OrthoShapeEvtHandler
from tests.demo.dcelvisualizer.shapes.BadgeShape import BadgeShape
from tests.demo.dcelvisualizer.shapes.VertexShape import VertexShape
from tests.demo.orthovisualizer.OrthoTypes import CanvasPoint
from tests.demo.orthovisualizer.OrthoTypes import NodePositions

from tests.demo.CanvasConstants import BORDER_LIGHT_GREY
from tests.demo.CanvasConstants import CANVAS_BACKGROUND_COLOUR
from tests.demo.CanvasConstants import PRIMAL_VERTEX_COLOUR
from tests.demo.CanvasConstants import VERTEX_FONT_SIZE

PRIMAL_EDGE_COLOUR:            Colour = Colour(100, 116, 139)
INTERNAL_FACE_BADGE_COLOUR:    Colour = Colour(224, 231, 255)
EXTERNAL_FACE_BADGE_COLOUR:    Colour = Colour(254, 243, 199)
VERTEX_TO_FACE_FLOW_COLOUR:    Colour = Colour(16, 185, 129)
FACE_TO_FACE_BEND_COLOUR:      Colour = Colour(239, 68, 68)
ZERO_FLOW_BEND_COLOUR:         Colour = BORDER_LIGHT_GREY
ANGLE_BADGE_BACKGROUND_COLOUR: Colour = Colour(243, 244, 246)

VERTEX_CIRCLE_DIAMETER:   float = 40.0
FACE_BADGE_WIDTH:         float = 88.0
FACE_BADGE_HEIGHT:        float = 26.0
ANGLE_BADGE_WIDTH:        float = 52.0
ANGLE_BADGE_HEIGHT:       float = 18.0
EDGE_ARROW_SIZE:          float = 9.0

BADGE_FONT_SIZE:  int = 11


class OrthoCanvasPanel(SizedPanel):
    """
    OGL canvas panel rendering the primal graph layout alongside FlowNet circulation arcs and shape metrics.
    """

    def __init__(self, parent: Window):
        """
        Construct the OrthoCanvasPanel.

        Args:
            parent: Parent container widget.
        """
        super().__init__(parent, ID_ANY)

        self._diagram: Diagram     = Diagram()
        self._canvas:  OrthoCanvas = OrthoCanvas(self, ID_ANY)

        # noinspection PyUnresolvedReferences
        self._canvas.SetSizerProps(expand=True, proportion=1, border=('all', 0))
        self._canvas.SetDiagram(self._diagram)
        self._canvas.SetBackgroundColour(CANVAS_BACKGROUND_COLOUR)
        self._diagram.SetCanvas(self._canvas)

        self._orthogonal: Optional[Orthogonalization] = None
        self._positions:  NodePositions              = NodePositions({})
        self._facePositions: Dict[FaceId, CanvasPoint] = {}

        self._showPrimalGraph: bool = True
        self._showDualFaces:   bool = True
        self._showFlowNetArcs: bool = True
        self._showAngleBends:  bool = True

        self._vertexShapeDict:   Dict[NodeId, VertexShape]                                = {}
        self._primalEdgeLines:   List[Tuple[NodeId, NodeId, LineShape]]                   = []
        self._faceBadgeDict:     Dict[FaceId, BadgeShape]                                 = {}
        self._faceBadgeEntries:  List[Tuple[FaceId, List[NodeId], bool, BadgeShape]]      = []
        self._flowArcLines:      List[Tuple[NodeId | FaceId, NodeId | FaceId, LineShape]] = []
        self._angleBadgeEntries: List[Tuple[NodeId, FaceId, BadgeShape, int]]             = []

    @property
    def showPrimalGraph(self) -> bool:
        """
        True if primal graph vertices and edges should be rendered.
        """
        return self._showPrimalGraph

    @showPrimalGraph.setter
    def showPrimalGraph(self, show: bool):
        self._showPrimalGraph = show
        self.rebuildDiagram()

    @property
    def showDualFaces(self) -> bool:
        """
        True if dual face center badges should be rendered.
        """
        return self._showDualFaces

    @showDualFaces.setter
    def showDualFaces(self, show: bool):
        self._showDualFaces = show
        self.rebuildDiagram()

    @property
    def showFlowNetArcs(self) -> bool:
        """
        True if directed circulation arcs should be rendered.
        """
        return self._showFlowNetArcs

    @showFlowNetArcs.setter
    def showFlowNetArcs(self, show: bool):
        self._showFlowNetArcs = show
        self.rebuildDiagram()

    @property
    def showAngleBends(self) -> bool:
        """
        True if corner angle allocations and bend badges should be rendered.
        """
        return self._showAngleBends

    @showAngleBends.setter
    def showAngleBends(self, show: bool):
        self._showAngleBends = show
        self.rebuildDiagram()

    def setOrthogonalization(self, orthogonal: Optional[Orthogonalization], initialPositions: Optional[NodePositions] = None):
        """
        Set active Orthogonalization model and initial node positions.

        Args:
            orthogonal: Orthogonalization instance.
            initialPositions: Optional dictionary of initial node canvas coordinates.
        """
        self._orthogonal = orthogonal
        self._facePositions = {}
        if initialPositions:
            self._positions = NodePositions(dict(initialPositions))
        elif orthogonal is not None:
            computedPositions: Dict[NodeId, CanvasPoint] = {}
            for nodeId, coord in orthogonal.planar.pos.items():
                computedPositions[nodeId] = CanvasPoint((float(coord.x) * 120.0 + 150.0, float(coord.y) * 120.0 + 150.0))
            self._positions = NodePositions(computedPositions)
        else:
            self._positions = NodePositions({})

        self.rebuildDiagram()

    def dragVertex(self, nodeId: NodeId, newX: float, newY: float):
        """
        Update vertex position, incident edge lines, dual face centers, and circulation arcs in-place while dragging.

        Args:
            nodeId: Identifier of the vertex being dragged.
            newX: Current X drag coordinate.
            newY: Current Y drag coordinate.
        """
        self._positions[nodeId] = CanvasPoint((newX, newY))

        if nodeId in self._vertexShapeDict:
            vertexShape: VertexShape = self._vertexShapeDict[nodeId]
            vertexShape.SetX(newX)
            vertexShape.SetY(newY)
            vertexShape.tooltipText = f'Vertex: {nodeId}\nDemand/Supply: -4 (2pi)\nPos: ({int(newX)}, {int(newY)})'

        for u, v, line in self._primalEdgeLines:
            if u == nodeId or v == nodeId:
                endPoints: Any = line.FindLineEndPoints()
                if endPoints is not None:
                    line.SetEnds(endPoints[0], endPoints[1], endPoints[2], endPoints[3])

        # Recalculate face centers affected by moved node
        for faceId, cycleNodes, isExternal, faceBadge in self._faceBadgeEntries:
            if faceId in self._facePositions:
                continue
            if isExternal:
                minX: float = min(p[0] for p in self._positions.values())
                maxX: float = max(p[0] for p in self._positions.values())
                minY: float = min(p[1] for p in self._positions.values())
                midX: float = (minX + maxX) / 2.0
                extY: float = max(40.0, minY - 70.0)
                faceBadge.SetX(midX)
                faceBadge.SetY(extY)
            elif nodeId in cycleNodes:
                cyclePts: List[CanvasPoint] = [self._positions[n] for n in cycleNodes if n in self._positions]
                if cyclePts:
                    avgX: float = sum(p[0] for p in cyclePts) / len(cyclePts)
                    avgY: float = sum(p[1] for p in cyclePts) / len(cyclePts)
                    faceBadge.SetX(avgX)
                    faceBadge.SetY(avgY)

        for source, target, flowLine in self._flowArcLines:
            endPoints = flowLine.FindLineEndPoints()
            if endPoints is not None:
                flowLine.SetEnds(endPoints[0], endPoints[1], endPoints[2], endPoints[3])

        for vId, fId, angleBadge, flowUnits in self._angleBadgeEntries:
            vx, vy = self._positions.get(vId, CanvasPoint((0.0, 0.0)))
            if fId in self._faceBadgeDict:
                faceBadgeObj: BadgeShape = self._faceBadgeDict[fId]
                fcX: float = float(faceBadgeObj.GetX())
                fcY: float = float(faceBadgeObj.GetY())
                deltaX: float = fcX - vx
                deltaY: float = fcY - vy
                dist: float = sqrt(deltaX * deltaX + deltaY * deltaY)
                badgeDist: float = 34.0
                if dist > 0.001:
                    offsetX: float = (deltaX / dist) * badgeDist
                    offsetY: float = (deltaY / dist) * badgeDist
                else:
                    offsetX = 0.0
                    offsetY = -badgeDist
                angleBadge.SetX(vx + offsetX)
                angleBadge.SetY(vy + offsetY)

        self._canvas.Draw()
        self._canvas.Refresh()

    def dragFace(self, elementId: NodeId | FaceId, newX: float, newY: float):
        """
        Update face badge position, incident circulation arcs, and corner angle badges in-place while dragging.

        Args:
            elementId: Face identifier being dragged.
            newX: Current X drag coordinate.
            newY: Current Y drag coordinate.
        """
        faceId: FaceId = str(elementId)
        self._facePositions[faceId] = CanvasPoint((newX, newY))

        if faceId in self._faceBadgeDict:
            faceBadge: BadgeShape = self._faceBadgeDict[faceId]
            faceBadge.SetX(newX)
            faceBadge.SetY(newY)

        for source, target, flowLine in self._flowArcLines:
            if source == faceId or target == faceId:
                endPoints: Any = flowLine.FindLineEndPoints()
                if endPoints is not None:
                    flowLine.SetEnds(endPoints[0], endPoints[1], endPoints[2], endPoints[3])

        for vId, fId, angleBadge, flowUnits in self._angleBadgeEntries:
            if fId == faceId:
                vx, vy = self._positions.get(vId, CanvasPoint((0.0, 0.0)))
                deltaX: float = newX - vx
                deltaY: float = newY - vy
                dist: float = sqrt(deltaX * deltaX + deltaY * deltaY)
                badgeDist: float = 34.0
                if dist > 0.001:
                    offsetX: float = (deltaX / dist) * badgeDist
                    offsetY: float = (deltaY / dist) * badgeDist
                else:
                    offsetX = 0.0
                    offsetY = -badgeDist
                angleBadge.SetX(vx + offsetX)
                angleBadge.SetY(vy + offsetY)

        self._canvas.Draw()
        self._canvas.Refresh()

    def onFaceMoved(self, elementId: NodeId | FaceId, newX: float, newY: float):
        """
        Callback invoked when a face badge drag operation completes to commit positions and refresh state.

        Args:
            elementId: Face identifier.
            newX: New X canvas coordinate.
            newY: New Y canvas coordinate.
        """
        faceId: FaceId = str(elementId)
        self._facePositions[faceId] = CanvasPoint((newX, newY))
        self.rebuildDiagram()

    def onVertexMoved(self, nodeId: NodeId, newX: float, newY: float):
        """
        Callback invoked when a vertex drag operation completes to commit positions and refresh state.

        Args:
            nodeId: Vertex identifier.
            newX: New X canvas coordinate.
            newY: New Y canvas coordinate.
        """
        self._positions[nodeId] = CanvasPoint((newX, newY))
        self.rebuildDiagram()

    def rebuildDiagram(self):
        """
        Clear and redraw all shapes and layers on the OGL canvas diagram.
        """
        self._diagram.DeleteAllShapes()

        self._vertexShapeDict.clear()
        self._primalEdgeLines.clear()
        self._faceBadgeDict.clear()
        self._faceBadgeEntries.clear()
        self._flowArcLines.clear()
        self._angleBadgeEntries.clear()

        if self._orthogonal is None:
            self._canvas.Refresh()
            return

        planar: Planarization = self._orthogonal.planar
        flowDict: FlowDict = self._orthogonal.flowDict

        faceCenterDict: Dict[FaceId, CanvasPoint] = self._computeFaceCenters(planar)

        # 1. Primal Layer: Vertices
        if self._showPrimalGraph:
            for vertex in planar.dcel.vertexDict.values():
                vertexId: NodeId = vertex.id
                posX, posY = self._positions.get(vertexId, CanvasPoint((200.0, 200.0)))
                vertexShape: VertexShape = VertexShape(VERTEX_CIRCLE_DIAMETER)
                vertexShape.SetX(posX)
                vertexShape.SetY(posY)
                vertexShape.SetPen(Pen(PRIMAL_VERTEX_COLOUR, 2))
                vertexShape.SetBrush(Brush(Colour(239, 246, 255)))

                textFont: Font = Font(VERTEX_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD)
                vertexShape.SetFont(textFont)
                vertexShape.AddText(str(vertexId))
                vertexShape.tooltipText = f'Vertex: {vertexId}\nDemand/Supply: -4 (2pi)\nPos: ({int(posX)}, {int(posY)})'

                evtHandler: OrthoShapeEvtHandler = OrthoShapeEvtHandler(
                    vertexId,
                    self._canvas,
                    self.dragVertex,
                    self.onVertexMoved,
                )
                evtHandler.SetShape(vertexShape)
                evtHandler.SetPreviousHandler(vertexShape.GetEventHandler())
                vertexShape.SetEventHandler(evtHandler)

                vertexShape.Show(True)
                self._diagram.AddShape(vertexShape)
                vertexShape.SetCanvas(self._canvas)
                self._vertexShapeDict[vertexId] = vertexShape

            # Primal Layer: Edges
            seenEdges: set = set()
            for u, v in planar.G.edges:
                edgeKey: Tuple = (min(str(u), str(v)), max(str(u), str(v)))
                if edgeKey not in seenEdges and u in self._vertexShapeDict and v in self._vertexShapeDict:
                    seenEdges.add(edgeKey)
                    edgeLine: LineShape = LineShape()
                    edgeLine.MakeLineControlPoints(2)
                    edgeLine.SetPen(Pen(PRIMAL_EDGE_COLOUR, 2))
                    self._vertexShapeDict[u].AddLine(edgeLine, self._vertexShapeDict[v])
                    edgeLine.Show(True)
                    self._diagram.AddShape(edgeLine)
                    edgeLine.SetCanvas(self._canvas)
                    self._primalEdgeLines.append((u, v, edgeLine))

        # 2. Dual Layer: Faces
        for face in planar.dcel.faceDict.values():
            faceId: FaceId = face.id
            isExternal: bool = (face is planar.externalFace)
            degree: int = len(face)
            demandVal: int = (2 * degree + 4) if isExternal else (2 * degree - 4)

            faceCenter: CanvasPoint = faceCenterDict.get(faceId, CanvasPoint((250.0, 100.0)))
            badgeWidth: float = FACE_BADGE_WIDTH if self._showDualFaces else 4.0
            badgeHeight: float = FACE_BADGE_HEIGHT if self._showDualFaces else 4.0
            faceBadge: BadgeShape = BadgeShape(badgeWidth, badgeHeight)
            faceBadge.SetX(faceCenter[0])
            faceBadge.SetY(faceCenter[1])

            if self._showDualFaces:
                badgeColour: Colour = EXTERNAL_FACE_BADGE_COLOUR if isExternal else INTERNAL_FACE_BADGE_COLOUR
                faceBadge.SetPen(Pen(Colour(148, 163, 184), 1))
                faceBadge.SetBrush(Brush(badgeColour))

                badgeFont: Font = Font(BADGE_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD)
                faceBadge.SetFont(badgeFont)
                labelText: str = f'{faceId} [d={demandVal}]'
                faceBadge.AddText(labelText)
                typeLabel: str = 'External Face' if isExternal else 'Internal Face'
                faceBadge.tooltipText = f'{typeLabel}: {faceId}\nDegree: {degree}\nDemand: {demandVal}'
            else:
                faceBadge.SetPen(TRANSPARENT_PEN)
                faceBadge.SetBrush(TRANSPARENT_BRUSH)
                faceBadge.SetDraggable(False)

            faceEvtHandler: OrthoShapeEvtHandler = OrthoShapeEvtHandler(
                faceId,
                self._canvas,
                self.dragFace,
                self.onFaceMoved,
            )
            faceEvtHandler.SetShape(faceBadge)
            faceEvtHandler.SetPreviousHandler(faceBadge.GetEventHandler())
            faceBadge.SetEventHandler(faceEvtHandler)

            faceBadge.Show(True)
            self._diagram.AddShape(faceBadge)
            faceBadge.SetCanvas(self._canvas)
            self._faceBadgeDict[faceId] = faceBadge

            cycleNodes: List[NodeId] = [v.id for v in face.surroundVertices()]
            self._faceBadgeEntries.append((faceId, cycleNodes, isExternal, faceBadge))

        # 3. FlowNet Layer: Arcs
        if self._showFlowNetArcs and self._showPrimalGraph:
            # Vertex to Face arcs
            for vertexId in self._vertexShapeDict:
                for faceId in self._faceBadgeDict:
                    if vertexId in flowDict and faceId in flowDict[vertexId]:
                        for key, units in flowDict[vertexId][faceId].items():
                            if units > 0:
                                flowLine: LineShape = LineShape()
                                flowLine.MakeLineControlPoints(2)
                                flowLine.SetPen(Pen(VERTEX_TO_FACE_FLOW_COLOUR, 1))
                                flowLine.AddArrow(ARROW_ARROW, ARROW_POSITION_END, EDGE_ARROW_SIZE, 0.0, f'{units*90}°')
                                self._vertexShapeDict[vertexId].AddLine(flowLine, self._faceBadgeDict[faceId])
                                flowLine.Show(True)
                                self._diagram.AddShape(flowLine)
                                flowLine.SetCanvas(self._canvas)
                                self._flowArcLines.append((vertexId, faceId, flowLine))

            # Face to Face dual bend arcs
            for sourceFaceId in self._faceBadgeDict:
                for targetFaceId in self._faceBadgeDict:
                    if sourceFaceId != targetFaceId:
                        if sourceFaceId in flowDict and targetFaceId in flowDict[sourceFaceId]:
                            for key, bendUnits in flowDict[sourceFaceId][targetFaceId].items():
                                if bendUnits > 0:
                                    bendLine: LineShape = LineShape()
                                    bendLine.MakeLineControlPoints(2)
                                    bendLine.SetPen(Pen(FACE_TO_FACE_BEND_COLOUR, 2))
                                    bendLine.AddArrow(ARROW_ARROW, ARROW_POSITION_END, EDGE_ARROW_SIZE, 0.0, f'bends={bendUnits}')
                                    self._faceBadgeDict[sourceFaceId].AddLine(bendLine, self._faceBadgeDict[targetFaceId])
                                    bendLine.Show(True)
                                    self._diagram.AddShape(bendLine)
                                    bendLine.SetCanvas(self._canvas)
                                    self._flowArcLines.append((sourceFaceId, targetFaceId, bendLine))

        # 4. Solved Orthogonal Shape: Angle Wedges & Bend Badges
        if self._showAngleBends and self._showPrimalGraph:
            self._renderAngleAndBendBadges(planar, flowDict, faceCenterDict)

        self._diagram.ShowAll(True)
        self._canvas.Draw()
        self._canvas.Refresh()

    def _renderAngleAndBendBadges(self, planar: Planarization, flowDict: FlowDict, faceCenters: Dict[FaceId, CanvasPoint]):
        """
        Render corner angle badges near each vertex pointing towards its incident face.
        """
        for vertex in planar.dcel.vertexDict.values():
            vertexId: NodeId = vertex.id
            if vertexId not in self._positions:
                continue
            vx, vy = self._positions[vertexId]

            for halfEdge in vertex.surroundHalfEdges():
                faceId: FaceId = halfEdge.incidentFace.id
                flowUnits: int = flowDict.get(vertexId, {}).get(faceId, {}).get(halfEdge.id, 0)
                if flowUnits <= 0:
                    continue

                angleDegrees: int = flowUnits * 90
                # Vector towards face center
                fcX, fcY = faceCenters.get(faceId, CanvasPoint((vx, vy - 60.0)))
                deltaX: float = fcX - vx
                deltaY: float = fcY - vy
                dist: float = sqrt(deltaX * deltaX + deltaY * deltaY)
                badgeDist: float = 34.0
                if dist > 0.001:
                    offsetX: float = (deltaX / dist) * badgeDist
                    offsetY: float = (deltaY / dist) * badgeDist
                else:
                    offsetX = 0.0
                    offsetY = -badgeDist

                angleBadge: BadgeShape = BadgeShape(ANGLE_BADGE_WIDTH, ANGLE_BADGE_HEIGHT)
                angleBadge.SetDraggable(False)
                angleBadge.SetX(vx + offsetX)
                angleBadge.SetY(vy + offsetY)
                angleBadge.SetPen(Pen(Colour(203, 213, 225), 1))
                angleBadge.SetBrush(Brush(ANGLE_BADGE_BACKGROUND_COLOUR))

                badgeFont: Font = Font(BADGE_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD)
                angleBadge.SetFont(badgeFont)
                angleBadge.AddText(f'{angleDegrees}°')
                angleBadge.tooltipText = f'Angle at {vertexId} in {faceId}: {angleDegrees}° ({flowUnits} x 90°)'

                angleBadge.Show(True)
                self._diagram.AddShape(angleBadge)
                angleBadge.SetCanvas(self._canvas)
                self._angleBadgeEntries.append((vertexId, faceId, angleBadge, flowUnits))

    def _computeFaceCenters(self, planar: Planarization) -> Dict[FaceId, CanvasPoint]:
        """
        Compute 2D canvas coordinates for each face center.
        """
        faceCenters: Dict[FaceId, CanvasPoint] = {}
        minX: float = 999999.0
        maxX: float = -999999.0
        minY: float = 999999.0
        maxY: float = -999999.0

        for pos in self._positions.values():
            minX = min(minX, pos[0])
            maxX = max(maxX, pos[0])
            minY = min(minY, pos[1])
            maxY = max(maxY, pos[1])

        for face in planar.dcel.faceDict.values():
            faceId: FaceId = face.id
            if faceId in self._facePositions:
                faceCenters[faceId] = self._facePositions[faceId]
                continue

            if face is planar.externalFace:
                # Place external face badge above the graph bounding box
                midX: float = (minX + maxX) / 2.0 if minX <= maxX else 300.0
                extY: float = max(40.0, minY - 70.0) if minY <= maxY else 50.0
                faceCenters[faceId] = CanvasPoint((midX, extY))
                continue

            cycleVertices: List[Vertex] = list(face.surroundVertices())
            if not cycleVertices:
                faceCenters[faceId] = CanvasPoint((300.0, 300.0))
                continue

            sumX: float = 0.0
            sumY: float = 0.0
            validCount: int = 0
            for v in cycleVertices:
                if v.id in self._positions:
                    pt: CanvasPoint = self._positions[v.id]
                    sumX += pt[0]
                    sumY += pt[1]
                    validCount += 1

            if validCount > 0:
                faceCenters[faceId] = CanvasPoint((sumX / validCount, sumY / validCount))
            else:
                faceCenters[faceId] = CanvasPoint((300.0, 300.0))

        return faceCenters
