"""
Visual GUI demo application demonstrating Doubly-Connected Edge List (DCEL) operations.

Uses wxPython and wx.lib.ogl (Object Graphics Library) to interactively display
planar graphs, directed twin half-edges, and topological updates resulting from
stepping through addNodeBetween() operations.
"""

from math import sqrt
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from networkx import Graph
from networkx import PlanarEmbedding
from networkx import check_planarity

from wx import ALL  # type: ignore[import-untyped]
from wx import App
from wx import BORDER_SUNKEN

from wx import BoxSizer
from wx import Brush
from wx import Button
from wx import CallAfter
from wx import Choice
from wx import Colour
from wx import CommandEvent
from wx import EVT_BUTTON
from wx import EVT_CHOICE
from wx import EVT_SLIDER
from wx import EVT_TIMER
from wx import EXPAND
from wx import FONTFAMILY_SWISS
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD
from wx import Font
from wx import Frame
from wx import HORIZONTAL
from wx import ID_ANY
from wx import LC_REPORT
from wx import ListCtrl
from wx import Notebook
from wx import Panel
from wx import Pen
from wx import SL_HORIZONTAL
from wx import Size
from wx import Slider
from wx import SplitterWindow
from wx import StaticText
from wx import StatusBar
from wx import TextCtrl
from wx import Timer
from wx import TimerEvent
from wx import VERTICAL
from wx import Window

from wx.lib.ogl import ARROW_ARROW  # type: ignore[import-untyped]
from wx.lib.ogl import ARROW_POSITION_END
from wx.lib.ogl import CircleShape
from wx.lib.ogl import Diagram
from wx.lib.ogl import LineShape
from wx.lib.ogl import OGLInitialize
from wx.lib.ogl import RectangleShape
from wx.lib.ogl import ShapeCanvas
from wx.lib.ogl import ShapeEvtHandler

from orthogonal.TopologyTypes import FaceId
from orthogonal.TopologyTypes import NodeId
from orthogonal.doublyConnectedEdgeList.DoublyConnectedEdgeList import DoublyConnectedEdgeList
from orthogonal.doublyConnectedEdgeList.Face import Face

VERTEX_FONT_SIZE:     int = 12
EDGE_LABEL_FONT_SIZE: int = 12
FACE_BADGE_FONT_SIZE: int = 12
INSPECTOR_FONT_SIZE:  int = 12

VERTEX_CIRCLE_DIAMETER:   float = 44.0
EDGE_LABEL_WIDTH:         float = 72.0
EDGE_LABEL_HEIGHT:        float = 22.0
EDGE_LABEL_CORNER_RADIUS: float = 3.0
EDGE_SPLINE_OFFSET:       float = 18.0
EDGE_ARROW_SIZE:          float = 11.0
FACE_BADGE_WIDTH:         float = 96.0
FACE_BADGE_HEIGHT:        float = 24.0
FACE_BADGE_CORNER_RADIUS: float = 4.0
FACE_BADGE_OFFSET_Y:      float = 18.0


class DcelStep:
    """
    Encapsulates a single step in constructing or modifying a DCEL.
    """

    def __init__(
        self,
        opType: str,
        u: NodeId,
        v: Optional[NodeId] = None,
        newNode: Optional[NodeId] = None,
        position: Optional[Tuple[float, float]] = None,
    ):
        """
        Initialize a DCEL construction step.

        Args:
            opType: Operation type ('add_vertex', 'add_edge', 'subdivide').
            u: First node identifier.
            v: Second node identifier, if applicable.
            newNode: New node identifier for edge subdivision, if applicable.
            position: Canvas coordinate tuple for add_vertex, if applicable.
        """
        self._opType: str = opType
        self._u: NodeId = u
        self._v: Optional[NodeId] = v
        self._newNode: Optional[NodeId] = newNode
        self._position: Optional[Tuple[float, float]] = position

    @property
    def opType(self) -> str:
        """Get the operation type string."""
        return self._opType

    @property
    def u(self) -> NodeId:
        """Get the primary node identifier."""
        return self._u

    @property
    def v(self) -> Optional[NodeId]:
        """Get the secondary node identifier, if any."""
        return self._v

    @property
    def newNode(self) -> Optional[NodeId]:
        """Get the new node identifier, if any."""
        return self._newNode

    @property
    def position(self) -> Optional[Tuple[float, float]]:
        """Get the canvas position coordinates, if any."""
        return self._position


class DatasetDefinition:
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
        topFrame: Any = self.GetTopLevelParent()
        if hasattr(topFrame, 'onCanvasClick'):
            topFrame.onCanvasClick(float(x), float(y))


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
        previousHandler: Any = self.GetPreviousHandler()
        if previousHandler:
            previousHandler.OnEndDragLeft(x, y, keys, attachment)

        shape: Any = self.GetShape()
        if shape is not None:
            newX: float = float(shape.GetX())
            newY: float = float(shape.GetY())
            topFrame: Any = self._canvas.GetTopLevelParent()
            if hasattr(topFrame, 'onVertexMoved'):
                CallAfter(lambda: topFrame.onVertexMoved(self._nodeId, newX, newY))


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

        self._diagram.ShowAll(True)
        self._canvas.Draw()
        self._canvas.Refresh()


class DcelInspectorPanel(Panel):
    """
    Notebook panel displaying tabular inspection of DCEL Vertices, Half-Edges, and Faces.
    """

    def __init__(self, parent: Window):
        """
        Construct the inspector panel.

        Args:
            parent: Parent window widget.
        """
        super().__init__(parent, ID_ANY)

        tableFont: Font = Font(INSPECTOR_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD)
        self._notebook: Notebook = Notebook(self, ID_ANY)
        self._notebook.SetFont(tableFont)

        self._vertexList: ListCtrl = ListCtrl(self._notebook, ID_ANY, style=LC_REPORT | BORDER_SUNKEN)
        self._vertexList.SetFont(tableFont)
        self._vertexList.AppendColumn('Node ID', width=100)
        self._vertexList.AppendColumn('incidentEdge', width=180)
        self._notebook.AddPage(self._vertexList, 'Vertices')

        self._halfEdgeList: ListCtrl = ListCtrl(self._notebook, ID_ANY, style=LC_REPORT | BORDER_SUNKEN)
        self._halfEdgeList.SetFont(tableFont)
        self._halfEdgeList.AppendColumn('HalfEdge ID', width=120)
        self._halfEdgeList.AppendColumn('Origin', width=80)
        self._halfEdgeList.AppendColumn('Twin', width=120)
        self._halfEdgeList.AppendColumn('Next', width=120)
        self._halfEdgeList.AppendColumn('Previous', width=120)
        self._halfEdgeList.AppendColumn('Incident Face', width=100)
        self._notebook.AddPage(self._halfEdgeList, 'Half-Edges')

        self._faceList: ListCtrl = ListCtrl(self._notebook, ID_ANY, style=LC_REPORT | BORDER_SUNKEN)
        self._faceList.SetFont(tableFont)
        self._faceList.AppendColumn('Face ID', width=80)
        self._faceList.AppendColumn('incidentEdge', width=120)
        self._faceList.AppendColumn('nodes_id (Cycle)', width=260)
        self._notebook.AddPage(self._faceList, 'Faces')

        panelSizer: BoxSizer = BoxSizer(VERTICAL)
        panelSizer.Add(self._notebook, 1, EXPAND | ALL, 2)
        self.SetSizer(panelSizer)

    def updateTables(self, dcel: DoublyConnectedEdgeList):
        """
        Refresh list controls with current DCEL contents.

        Args:
            dcel: Current DoublyConnectedEdgeList instance.
        """
        self._vertexList.DeleteAllItems()
        rowIndex: int = 0
        for nodeKey, vertexInstance in sorted(dcel.vertexDict.items(), key=lambda pair: str(pair[0])):
            self._vertexList.InsertItem(rowIndex, str(nodeKey))
            incidentStr: str = str(vertexInstance.incidentEdge.id) if vertexInstance.hasIncidentEdge else 'Uninitialized'
            self._vertexList.SetItem(rowIndex, 1, incidentStr)
            rowIndex += 1

        self._halfEdgeList.DeleteAllItems()
        rowIndex = 0
        for _edgeKey, halfEdge in sorted(dcel.halfEdgeDict.items(), key=lambda pair: str(pair[0])):
            self._halfEdgeList.InsertItem(rowIndex, str(halfEdge.id))
            self._halfEdgeList.SetItem(rowIndex, 1, str(halfEdge.origin.id) if halfEdge.origin else 'None')
            self._halfEdgeList.SetItem(rowIndex, 2, str(halfEdge.twin.id) if halfEdge.twin else 'None')
            self._halfEdgeList.SetItem(rowIndex, 3, str(halfEdge.next.id) if halfEdge.next else 'None')
            self._halfEdgeList.SetItem(rowIndex, 4, str(halfEdge.previous.id) if halfEdge.previous else 'None')
            faceStr: str = str(halfEdge.incidentFace.id) if halfEdge.incidentFace else 'None'
            self._halfEdgeList.SetItem(rowIndex, 5, faceStr)
            rowIndex += 1

        self._faceList.DeleteAllItems()
        rowIndex = 0
        for faceKey, faceInstance in sorted(dcel.faceDict.items(), key=lambda pair: str(pair[0])):
            self._faceList.InsertItem(rowIndex, str(faceKey))
            incidentEdgeStr: str = str(faceInstance.incidentEdge.id) if faceInstance.hasIncidentEdge else 'Uninitialized'
            self._faceList.SetItem(rowIndex, 1, incidentEdgeStr)
            cycleStr: str = ' → '.join(str(n) for n in faceInstance.nodes_id)
            self._faceList.SetItem(rowIndex, 2, f'[{cycleStr}]')
            rowIndex += 1


class DcelVisualizerFrame(Frame):
    """
    Main application frame for DCEL visualization and interactive stepping.
    """

    def __init__(self):
        """
        Initialize the DCEL visualizer window, controls, and default dataset.
        """
        super().__init__(None, ID_ANY, 'DCEL Visualizer - wxPython ogl', size=Size(1280, 800))

        self._datasets: List[DatasetDefinition] = self._createDatasets()
        self._currentDatasetIndex: int = 0
        self._currentStepIndex: int = 0
        self._operations: List[DcelStep] = list(self._datasets[0].plannedSteps)
        self._positionOverrides: Dict[NodeId, Tuple[float, float]] = {}

        self._timer: Timer = Timer(self)
        self.Bind(EVT_TIMER, self.onTimer, self._timer)

        self._initUi()
        self._loadDataset(0)

    def _createDatasets(self) -> List[DatasetDefinition]:
        """
        Construct preset datasets: Empty (Blank Canvas), Small (K3), Medium, and Large.

        Returns:
            List of DatasetDefinition instances.
        """
        emptyPreset: DatasetDefinition = DatasetDefinition(
            name='Empty (Blank Canvas)',
            plannedSteps=[],
        )

        smallPreset: DatasetDefinition = DatasetDefinition(
            name='Small (Triangle K3)',
            plannedSteps=[
                DcelStep('add_vertex', 'v1', position=(280.0, 90.0)),
                DcelStep('add_vertex', 'v2', position=(460.0, 370.0)),
                DcelStep('add_vertex', 'v3', position=(100.0, 370.0)),
                DcelStep('add_edge', 'v1', 'v2'),
                DcelStep('add_edge', 'v2', 'v3'),
                DcelStep('add_edge', 'v3', 'v1'),
                DcelStep('subdivide', 'v1', 'v2', newNode='v12'),
                DcelStep('subdivide', 'v2', 'v3', newNode='v23'),
            ],
        )

        mediumPreset: DatasetDefinition = DatasetDefinition(
            name='Medium (Diamond K4 - e)',
            plannedSteps=[
                DcelStep('add_vertex', 'v1', position=(280.0, 70.0)),
                DcelStep('add_vertex', 'v2', position=(460.0, 230.0)),
                DcelStep('add_vertex', 'v3', position=(280.0, 390.0)),
                DcelStep('add_vertex', 'v4', position=(100.0, 230.0)),
                DcelStep('add_edge', 'v1', 'v2'),
                DcelStep('add_edge', 'v2', 'v3'),
                DcelStep('add_edge', 'v3', 'v4'),
                DcelStep('add_edge', 'v4', 'v1'),
                DcelStep('add_edge', 'v2', 'v4'),
                DcelStep('subdivide', 'v2', 'v4', newNode='v24'),
                DcelStep('subdivide', 'v1', 'v2', newNode='v12'),
                DcelStep('subdivide', 'v3', 'v4', newNode='v34'),
            ],
        )

        largePreset: DatasetDefinition = DatasetDefinition(
            name='Large (2x3 Planar Grid)',
            plannedSteps=[
                DcelStep('add_vertex', 'n1', position=(120.0, 110.0)),
                DcelStep('add_vertex', 'n2', position=(280.0, 110.0)),
                DcelStep('add_vertex', 'n3', position=(440.0, 110.0)),
                DcelStep('add_vertex', 'n4', position=(120.0, 350.0)),
                DcelStep('add_vertex', 'n5', position=(280.0, 350.0)),
                DcelStep('add_vertex', 'n6', position=(440.0, 350.0)),
                DcelStep('add_edge', 'n1', 'n2'),
                DcelStep('add_edge', 'n2', 'n3'),
                DcelStep('add_edge', 'n4', 'n5'),
                DcelStep('add_edge', 'n5', 'n6'),
                DcelStep('add_edge', 'n1', 'n4'),
                DcelStep('add_edge', 'n2', 'n5'),
                DcelStep('add_edge', 'n3', 'n6'),
                DcelStep('subdivide', 'n1', 'n2', newNode='n12'),
                DcelStep('subdivide', 'n2', 'n5', newNode='n25'),
                DcelStep('subdivide', 'n5', 'n6', newNode='n56'),
                DcelStep('subdivide', 'n4', 'n5', newNode='n45'),
            ],
        )

        return [emptyPreset, smallPreset, mediumPreset, largePreset]

    def _initUi(self):
        """
        Build frame layout with top toolbar, splitter canvas/inspector, and status bar.
        """
        mainPanel: Panel = Panel(self, ID_ANY)
        rootSizer: BoxSizer = BoxSizer(VERTICAL)

        topControlsSizer: BoxSizer = BoxSizer(VERTICAL)
        rowOneSizer: BoxSizer = BoxSizer(HORIZONTAL)
        rowTwoSizer: BoxSizer = BoxSizer(HORIZONTAL)

        datasetLabel: StaticText = StaticText(mainPanel, ID_ANY, 'Dataset:')
        rowOneSizer.Add(datasetLabel, 0, ALL, 6)

        datasetNames: List[str] = [d.name for d in self._datasets]
        self._datasetChoice: Choice = Choice(mainPanel, ID_ANY, choices=datasetNames)
        self._datasetChoice.SetSelection(0)
        self._datasetChoice.Bind(EVT_CHOICE, self.onDatasetChanged)
        rowOneSizer.Add(self._datasetChoice, 0, ALL, 4)

        self._btnReset: Button = Button(mainPanel, ID_ANY, '↺ Reset')
        self._btnReset.Bind(EVT_BUTTON, self.onReset)
        rowOneSizer.Add(self._btnReset, 0, ALL, 4)

        self._btnStepBack: Button = Button(mainPanel, ID_ANY, '◀ Step Back')
        self._btnStepBack.Bind(EVT_BUTTON, self.onStepBack)
        rowOneSizer.Add(self._btnStepBack, 0, ALL, 4)

        self._btnStepForward: Button = Button(mainPanel, ID_ANY, 'Step Fwd ▶')
        self._btnStepForward.Bind(EVT_BUTTON, self.onStepForward)
        rowOneSizer.Add(self._btnStepForward, 0, ALL, 4)

        self._btnStepAll: Button = Button(mainPanel, ID_ANY, '⏭ Step All')
        self._btnStepAll.Bind(EVT_BUTTON, self.onStepAll)
        rowOneSizer.Add(self._btnStepAll, 0, ALL, 4)

        self._btnPlay: Button = Button(mainPanel, ID_ANY, '▶ Auto-Play')
        self._btnPlay.Bind(EVT_BUTTON, self.onTogglePlay)
        rowOneSizer.Add(self._btnPlay, 0, ALL, 4)

        sliderLabel: StaticText = StaticText(mainPanel, ID_ANY, 'Step:')
        rowOneSizer.Add(sliderLabel, 0, ALL, 6)

        self._stepSlider: Slider = Slider(mainPanel, ID_ANY, 0, 0, 2, style=SL_HORIZONTAL)
        self._stepSlider.Bind(EVT_SLIDER, self.onSliderChanged)
        rowOneSizer.Add(self._stepSlider, 0, ALL, 4)

        vertexLabel: StaticText = StaticText(mainPanel, ID_ANY, 'Node:')
        rowTwoSizer.Add(vertexLabel, 0, ALL, 6)

        self._vertexNameText: TextCtrl = TextCtrl(mainPanel, ID_ANY, 'v1', size=Size(50, -1))
        rowTwoSizer.Add(self._vertexNameText, 0, ALL, 4)

        self._btnAddVertex: Button = Button(mainPanel, ID_ANY, '+ Add Vertex')
        self._btnAddVertex.Bind(EVT_BUTTON, self.onAddVertex)
        rowTwoSizer.Add(self._btnAddVertex, 0, ALL, 4)

        edgeULabel: StaticText = StaticText(mainPanel, ID_ANY, 'Edge u:')
        rowTwoSizer.Add(edgeULabel, 0, ALL, 6)

        self._edgeUChoice: Choice = Choice(mainPanel, ID_ANY)
        rowTwoSizer.Add(self._edgeUChoice, 0, ALL, 4)

        edgeVLabel: StaticText = StaticText(mainPanel, ID_ANY, 'v:')
        rowTwoSizer.Add(edgeVLabel, 0, ALL, 6)

        self._edgeVChoice: Choice = Choice(mainPanel, ID_ANY)
        rowTwoSizer.Add(self._edgeVChoice, 0, ALL, 4)

        self._btnAddEdge: Button = Button(mainPanel, ID_ANY, '+ Add Edge')
        self._btnAddEdge.Bind(EVT_BUTTON, self.onAddEdge)
        rowTwoSizer.Add(self._btnAddEdge, 0, ALL, 4)

        adHocULabel: StaticText = StaticText(mainPanel, ID_ANY, 'Split u:')
        rowTwoSizer.Add(adHocULabel, 0, ALL, 6)

        self._adhocUChoice: Choice = Choice(mainPanel, ID_ANY)
        self._adhocUChoice.Bind(EVT_CHOICE, self.onAdhocUChanged)
        rowTwoSizer.Add(self._adhocUChoice, 0, ALL, 4)

        adHocVLabel: StaticText = StaticText(mainPanel, ID_ANY, 'v:')
        rowTwoSizer.Add(adHocVLabel, 0, ALL, 6)

        self._adhocVChoice: Choice = Choice(mainPanel, ID_ANY)
        rowTwoSizer.Add(self._adhocVChoice, 0, ALL, 4)

        newNodeLabel: StaticText = StaticText(mainPanel, ID_ANY, 'New Node:')
        rowTwoSizer.Add(newNodeLabel, 0, ALL, 6)

        self._adhocNewText: TextCtrl = TextCtrl(mainPanel, ID_ANY, 'v_mid', size=Size(65, -1))
        rowTwoSizer.Add(self._adhocNewText, 0, ALL, 4)

        self._btnExecuteAdhoc: Button = Button(mainPanel, ID_ANY, '+ Subdivide Edge')
        self._btnExecuteAdhoc.Bind(EVT_BUTTON, self.onExecuteAdhoc)
        rowTwoSizer.Add(self._btnExecuteAdhoc, 0, ALL, 4)

        topControlsSizer.Add(rowOneSizer, 0, EXPAND | ALL, 2)
        topControlsSizer.Add(rowTwoSizer, 0, EXPAND | ALL, 2)
        rootSizer.Add(topControlsSizer, 0, EXPAND | ALL, 4)

        self._splitter: SplitterWindow = SplitterWindow(mainPanel, ID_ANY)
        self._canvasPanel: DcelCanvasPanel = DcelCanvasPanel(self._splitter)
        self._inspectorPanel: DcelInspectorPanel = DcelInspectorPanel(self._splitter)
        self._splitter.SplitVertically(self._canvasPanel, self._inspectorPanel, 640)
        self._splitter.SetMinimumPaneSize(350)

        rootSizer.Add(self._splitter, 1, EXPAND | ALL, 2)

        self._statusBar: StatusBar = self.CreateStatusBar(2)
        self._statusBar.SetStatusWidths([-3, -1])

        mainPanel.SetSizer(rootSizer)
        frameSizer: BoxSizer = BoxSizer(VERTICAL)
        frameSizer.Add(mainPanel, 1, EXPAND)
        self.SetSizer(frameSizer)
        self.Layout()

    def _loadDataset(self, datasetIndex: int):
        """
        Switch to the specified dataset preset and reset execution state.

        Args:
            datasetIndex: Index into _datasets list.
        """
        self._currentDatasetIndex = datasetIndex
        self._currentStepIndex = 0
        self._operations = list(self._datasets[datasetIndex].plannedSteps)
        self._positionOverrides.clear()

        totalSteps: int = len(self._operations)
        self._stepSlider.SetRange(0, totalSteps)
        self._stepSlider.SetValue(0)

        self._refreshState()

    def _getAllSteps(self) -> List[DcelStep]:
        """
        Return active ordered list of DCEL building steps.

        Returns:
            List of DcelStep operation specifications.
        """
        return self._operations

    @staticmethod
    def _buildDcel(graph: Graph) -> DoublyConnectedEdgeList:
        """
        Construct a DCEL from the given planar graph.

        Args:
            graph: Planar graph to convert.

        Returns:
            Newly constructed DoublyConnectedEdgeList.
        """
        isPlanar: bool
        embedding: PlanarEmbedding
        isPlanar, embedding = check_planarity(graph)
        assert isPlanar, 'Graph must be planar'
        return DoublyConnectedEdgeList(graph, embedding)

    def _replaySteps(
        self,
        stepIndex: int,
    ) -> Tuple[Graph, DoublyConnectedEdgeList, Dict[NodeId, Tuple[float, float]], Optional[NodeId], str]:
        """
        Replay construction steps, in order, from an empty DCEL up to stepIndex.

        add_vertex and add_edge rebuild the DCEL from the mirrored graph because the DCEL
        has no incremental insertion API. subdivide calls addNodeBetween() on the live DCEL
        and mirrors the split into the graph so that later rebuilds retain it.

        Args:
            stepIndex: Target step count.

        Returns:
            Tuple of (graph, dcel, positions, lastInsertedNode, lastActionDescription).
        """
        baseGraph: Graph = Graph()
        positions: Dict[NodeId, Tuple[float, float]] = {}
        lastInserted: Optional[NodeId] = None
        lastAction: str = 'Empty DCEL (Blank Canvas)'
        dcel: DoublyConnectedEdgeList = self._buildDcel(baseGraph)

        allSteps: List[DcelStep] = self._getAllSteps()
        clampedStep: int = min(stepIndex, len(allSteps))

        for idx in range(clampedStep):
            step: DcelStep = allSteps[idx]
            stepV: Optional[NodeId] = step.v
            stepNewNode: Optional[NodeId] = step.newNode
            if step.opType == 'add_vertex':
                baseGraph.add_node(step.u)
                stepPos: Optional[Tuple[float, float]] = step.position
                if stepPos is not None:
                    positions[step.u] = stepPos
                else:
                    count: int = len(positions)
                    positions[step.u] = (120.0 + (count % 4) * 120.0, 120.0 + (count // 4) * 120.0)
                dcel = self._buildDcel(baseGraph)
                lastInserted = step.u
                lastAction = f'addVertex({step.u!r})'
            elif step.opType == 'add_edge' and stepV is not None:
                baseGraph.add_edge(step.u, stepV)
                dcel = self._buildDcel(baseGraph)
                lastAction = f'addEdge({step.u!r}, {stepV!r})'
            elif step.opType == 'subdivide' and stepV is not None and stepNewNode is not None:
                dcel.addNodeBetween(step.u, stepV, stepNewNode)
                baseGraph.remove_edge(step.u, stepV)
                baseGraph.add_edge(step.u, stepNewNode)
                baseGraph.add_edge(stepNewNode, stepV)
                lastInserted = stepNewNode
                lastAction = f'addNodeBetween({step.u!r}, {stepV!r}, {stepNewNode!r})'

                if step.u in positions and stepV in positions:
                    posU: Tuple[float, float] = positions[step.u]
                    posV: Tuple[float, float] = positions[stepV]
                    positions[stepNewNode] = ((posU[0] + posV[0]) / 2.0, (posU[1] + posV[1]) / 2.0)
                else:
                    positions[stepNewNode] = (250.0, 200.0)

            for movedNode, movedPos in self._positionOverrides.items():
                if movedNode in positions:
                    positions[movedNode] = movedPos

        return baseGraph, dcel, positions, lastInserted, lastAction

    def _computeDcelAtStep(
        self,
        stepIndex: int,
    ) -> Tuple[DoublyConnectedEdgeList, Dict[NodeId, Tuple[float, float]], Optional[NodeId], str]:
        """
        Reconstruct DCEL from an empty state by replaying steps up to stepIndex.

        Args:
            stepIndex: Target step count.

        Returns:
            Tuple of (dcel, positions, lastInsertedNode, lastActionDescription).
        """
        dcel: DoublyConnectedEdgeList
        positions: Dict[NodeId, Tuple[float, float]]
        lastInserted: Optional[NodeId]
        lastAction: str
        _, dcel, positions, lastInserted, lastAction = self._replaySteps(stepIndex)
        return dcel, positions, lastInserted, lastAction

    def _refreshState(self):
        """
        Recompute DCEL state, refresh canvas and inspector, and update toolbar indicators.
        """
        allSteps: List[DcelStep] = self._getAllSteps()
        totalSteps: int = len(allSteps)

        self._stepSlider.SetRange(0, totalSteps)
        self._stepSlider.SetValue(self._currentStepIndex)

        self._btnStepBack.Enable(self._currentStepIndex > 0)
        self._btnStepForward.Enable(self._currentStepIndex < totalSteps)
        self._btnStepAll.Enable(self._currentStepIndex < totalSteps)

        dcel, positions, insertedNode, lastAction = self._computeDcelAtStep(self._currentStepIndex)

        self._canvasPanel.renderDcel(dcel, positions, insertedNode)
        self._inspectorPanel.updateTables(dcel)

        self._updateAdhocChoices(dcel)
        self._updateBuilderChoices(dcel)

        numV: int = len(dcel.vertexDict)
        numE: int = len(dcel.halfEdgeDict) // 2
        numF: int = len(dcel.faceDict)
        eulerVal: int = numV - numE + numF

        self._statusBar.SetStatusText(f'Step {self._currentStepIndex}/{totalSteps}: {lastAction}', 0)
        self._statusBar.SetStatusText(f'V={numV} E={numE} F={numF} (V-E+F={eulerVal})', 1)

    def onDatasetChanged(self, _event: CommandEvent):
        """
        Handle dataset selection choice change.

        Args:
            _event: wx CommandEvent.
        """
        selection: int = self._datasetChoice.GetSelection()
        self._loadDataset(selection)

    def _getNextVertexName(self) -> str:
        """
        Find next available default vertex identifier (v1, v2, ...).

        Returns:
            Next available node identifier.
        """
        dcel, _, _, _ = self._computeDcelAtStep(self._currentStepIndex)
        idx: int = 1
        while f'v{idx}' in dcel.vertexDict:
            idx += 1
        return f'v{idx}'

    def _updateBuilderChoices(self, dcel: DoublyConnectedEdgeList):
        """
        Update vertex name text and Add Edge choices based on active DCEL state.

        Args:
            dcel: Current DoublyConnectedEdgeList instance.
        """
        self._vertexNameText.SetValue(self._getNextVertexName())

        allNodes: List[str] = sorted([str(k) for k in dcel.vertexDict.keys()])
        currU: str = self._edgeUChoice.GetStringSelection()
        currV: str = self._edgeVChoice.GetStringSelection()
        self._edgeUChoice.Set(allNodes)
        self._edgeVChoice.Set(allNodes)
        if allNodes:
            self._edgeUChoice.SetStringSelection(currU if currU in allNodes else allNodes[0])
            self._edgeVChoice.SetStringSelection(currV if currV in allNodes else (allNodes[1] if len(allNodes) > 1 else allNodes[0]))

    def _updateAdhocChoices(self, dcel: DoublyConnectedEdgeList):
        """
        Populate origin and destination choices based on active half-edges.

        Args:
            dcel: Current DoublyConnectedEdgeList instance.
        """
        validOrigins: List[str] = sorted(list({str(u) for (u, _) in dcel.halfEdgeDict.keys()}))
        currentU: str = self._adhocUChoice.GetStringSelection()
        self._adhocUChoice.Set(validOrigins)

        selectedU: str = currentU if currentU in validOrigins else (validOrigins[0] if validOrigins else '')
        if selectedU:
            self._adhocUChoice.SetStringSelection(selectedU)

        self._updateAdhocVChoices(dcel, selectedU)

    def _updateAdhocVChoices(self, dcel: DoublyConnectedEdgeList, selectedU: str):
        """
        Populate destination choices with valid neighbors of selected origin.

        Args:
            dcel: Current DoublyConnectedEdgeList instance.
            selectedU: Selected origin node ID.
        """
        validDestinations: List[str] = sorted([str(v) for (u, v) in dcel.halfEdgeDict.keys() if str(u) == selectedU])
        self._adhocVChoice.Set(validDestinations)
        if validDestinations:
            self._adhocVChoice.SetSelection(0)

    def onCanvasClick(self, clickX: float, clickY: float):
        """
        Add a vertex at clicked canvas coordinates.

        Args:
            clickX: X coordinate of canvas click.
            clickY: Y coordinate of canvas click.
        """
        nodeName: str = self._vertexNameText.GetValue().strip()
        if not nodeName:
            nodeName = self._getNextVertexName()

        dcel, _, _, _ = self._computeDcelAtStep(self._currentStepIndex)
        if nodeName in dcel.vertexDict:
            self._statusBar.SetStatusText(f'Vertex {nodeName!r} already exists', 0)
            return

        newStep: DcelStep = DcelStep('add_vertex', nodeName, position=(clickX, clickY))
        self._operations = self._operations[:self._currentStepIndex] + [newStep]
        self._currentStepIndex = len(self._operations)
        self._refreshState()

    def onVertexMoved(self, nodeId: NodeId, newX: float, newY: float):
        """
        Record updated canvas coordinates for a dragged vertex and refresh the diagram.

        Args:
            nodeId: Identifier of the dragged vertex.
            newX: New X coordinate on canvas.
            newY: New Y coordinate on canvas.
        """
        self._positionOverrides[nodeId] = (newX, newY)
        self._refreshState()

    def onAddVertex(self, _event: CommandEvent):
        """
        Handle + Add Vertex button click.

        Args:
            _event: wx CommandEvent.
        """
        nodeName: str = self._vertexNameText.GetValue().strip()
        if not nodeName:
            nodeName = self._getNextVertexName()

        dcel, positions, _, _ = self._computeDcelAtStep(self._currentStepIndex)
        if nodeName in dcel.vertexDict:
            self._statusBar.SetStatusText(f'Vertex {nodeName!r} already exists', 0)
            return

        count: int = len(positions)
        posX: float = 120.0 + (count % 4) * 120.0
        posY: float = 120.0 + (count // 4) * 120.0
        newStep: DcelStep = DcelStep('add_vertex', nodeName, position=(posX, posY))
        self._operations = self._operations[:self._currentStepIndex] + [newStep]
        self._currentStepIndex = len(self._operations)
        self._refreshState()

    def onAddEdge(self, _event: CommandEvent):
        """
        Handle + Add Edge button click between selected u and v.

        Args:
            _event: wx CommandEvent.
        """
        uNode: str = self._edgeUChoice.GetStringSelection()
        vNode: str = self._edgeVChoice.GetStringSelection()

        if not uNode or not vNode:
            return
        if uNode == vNode:
            self._statusBar.SetStatusText('Cannot add edge: endpoints u and v must be distinct', 0)
            return

        currentGraph: Graph
        currentGraph, _, _, _, _ = self._replaySteps(self._currentStepIndex)
        if currentGraph.has_edge(uNode, vNode):
            self._statusBar.SetStatusText(f'Edge ({uNode}, {vNode}) already exists', 0)
            return

        testGraph: Graph = currentGraph.copy()
        testGraph.add_edge(uNode, vNode)
        isPlanar: bool
        isPlanar, _ = check_planarity(testGraph)
        if not isPlanar:
            self._statusBar.SetStatusText(f'Cannot add edge ({uNode}, {vNode}): graph would become non-planar', 0)
            return

        newStep: DcelStep = DcelStep('add_edge', uNode, v=vNode)
        self._operations = self._operations[:self._currentStepIndex] + [newStep]
        self._currentStepIndex = len(self._operations)
        self._refreshState()

    def onAdhocUChanged(self, _event: CommandEvent):
        """
        Update destination choices when origin node selection changes.

        Args:
            _event: wx CommandEvent.
        """
        selectedU: str = self._adhocUChoice.GetStringSelection()
        dcel, _, _, _ = self._computeDcelAtStep(self._currentStepIndex)
        self._updateAdhocVChoices(dcel, selectedU)

    def onReset(self, _event: CommandEvent):
        """
        Handle Reset button click.

        Args:
            _event: wx CommandEvent.
        """
        self._currentStepIndex = 0
        self._operations = list(self._datasets[self._currentDatasetIndex].plannedSteps)
        self._positionOverrides.clear()
        self._refreshState()

    def onStepBack(self, _event: CommandEvent):
        """
        Handle Step Back button click.

        Args:
            _event: wx CommandEvent.
        """
        if self._currentStepIndex > 0:
            self._currentStepIndex -= 1
            self._refreshState()

    def onStepForward(self, _event: CommandEvent):
        """
        Handle Step Forward button click.

        Args:
            _event: wx CommandEvent.
        """
        allSteps: List[DcelStep] = self._getAllSteps()
        if self._currentStepIndex < len(allSteps):
            self._currentStepIndex += 1
            self._refreshState()

    def onStepAll(self, _event: CommandEvent):
        """
        Handle Step All button click to execute all pending calls.

        Args:
            _event: wx CommandEvent.
        """
        allSteps: List[DcelStep] = self._getAllSteps()
        self._currentStepIndex = len(allSteps)
        self._refreshState()

    def onTogglePlay(self, _event: CommandEvent):
        """
        Toggle automatic stepping timer.

        Args:
            _event: wx CommandEvent.
        """
        if self._timer.IsRunning():
            self._timer.Stop()
            self._btnPlay.SetLabel('▶ Auto-Play')
        else:
            self._btnPlay.SetLabel('⏸ Pause')
            self._timer.Start(900)

    def onTimer(self, _event: TimerEvent):
        """
        Advance one step on each timer tick.

        Args:
            _event: wx TimerEvent.
        """
        allSteps: List[DcelStep] = self._getAllSteps()
        if self._currentStepIndex < len(allSteps):
            self._currentStepIndex += 1
            self._refreshState()
        else:
            self._timer.Stop()
            self._btnPlay.SetLabel('▶ Auto-Play')

    def onSliderChanged(self, _event: CommandEvent):
        """
        Handle step slider scrubbing.

        Args:
            _event: wx CommandEvent.
        """
        self._currentStepIndex = self._stepSlider.GetValue()
        self._refreshState()

    def onExecuteAdhoc(self, _event: CommandEvent):
        """
        Handle execution of user-specified ad-hoc addNodeBetween call.

        Args:
            _event: wx CommandEvent.
        """
        uSelection: str = self._adhocUChoice.GetStringSelection()
        vSelection: str = self._adhocVChoice.GetStringSelection()
        newName: str = self._adhocNewText.GetValue().strip()

        if not uSelection or not vSelection:
            return

        if uSelection == vSelection:
            return

        dcel, _, _, _ = self._computeDcelAtStep(self._currentStepIndex)
        if (uSelection, vSelection) not in dcel.halfEdgeDict:
            self._statusBar.SetStatusText(f'Cannot subdivide: edge ({uSelection}, {vSelection}) does not exist in current DCEL', 0)
            return

        if not newName:
            newName = f'v_{uSelection}_{vSelection}'

        if newName in dcel.vertexDict:
            self._statusBar.SetStatusText(f'Cannot subdivide: vertex {newName!r} already exists', 0)
            return

        newStep: DcelStep = DcelStep('subdivide', uSelection, v=vSelection, newNode=newName)
        self._operations = self._operations[:self._currentStepIndex] + [newStep]
        self._currentStepIndex = len(self._operations)
        self._refreshState()


def main():
    """
    Launch the DCEL visualizer demo application.
    """
    app: App = App(False)
    OGLInitialize()
    frame: DcelVisualizerFrame = DcelVisualizerFrame()
    frame.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    main()
