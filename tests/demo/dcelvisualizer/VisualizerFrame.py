
from typing import List
from typing import Optional
from typing import Tuple

from networkx import Graph
from networkx import PlanarEmbedding
from networkx import check_planarity

from wx import Button
from wx import Choice
from wx import CommandEvent
from wx import EVT_BUTTON
from wx import EVT_CHOICE
from wx import EVT_SLIDER
from wx import EVT_TIMER
from wx import ID_ANY
from wx import SL_HORIZONTAL
from wx import Size
from wx import Slider
from wx import SplitterWindow
from wx import StaticText
from wx import StatusBar
from wx import TextCtrl
from wx import Timer
from wx import TimerEvent
from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from orthogonal.TopologyTypes import NodeId
from orthogonal.doublyConnectedEdgeList.DoublyConnectedEdgeList import DoublyConnectedEdgeList
from tests.demo.CanvasTypes import CanvasPoint
from tests.demo.dcelvisualizer.CanvasPanel import NODE_SPREAD_FACTOR
from tests.demo.dcelvisualizer.CanvasPanel import CanvasPanel
from tests.demo.dcelvisualizer.DcelDataSet import DcelDataSet
from tests.demo.dcelvisualizer.DcelDataSet import createDefaultDataSets
from tests.demo.dcelvisualizer.InspectorPanel import InspectorPanel

from tests.demo.dcelvisualizer.VisualizerTypes import NodePositions
from tests.demo.dcelvisualizer.VisualizerTypes import StepState

from tests.demo.dcelvisualizer.DcelStep import DcelStep
from tests.demo.dcelvisualizer.DcelStep import DcelSteps

DEFAULT_FRAME_WIDTH:   int   = 1280
DEFAULT_FRAME_HEIGHT:  int   = 800
SPLITTER_SASH_RATIO:   float = 2.0 / 3.0
DEFAULT_SASH_POSITION: int   = int(DEFAULT_FRAME_WIDTH * SPLITTER_SASH_RATIO)

class VisualizerFrame(SizedFrame):
    """
    Main application frame for DCEL visualization and interactive stepping.
    """

    def __init__(self):
        """
        Initialize the DCEL visualizer window, controls, and default dataset.
        """
        super().__init__(None, ID_ANY, 'DCEL Visualizer - wxPython ogl', size=Size(DEFAULT_FRAME_WIDTH, DEFAULT_FRAME_HEIGHT))

        self._datasets: List[DcelDataSet] = createDefaultDataSets()
        self._currentDatasetIndex: int = 0
        self._currentStepIndex: int = 0
        self._operations: DcelSteps = DcelSteps(list(self._datasets[0].plannedSteps))
        self._positionOverrides: NodePositions = NodePositions({})

        self._timer: Timer = Timer(self)
        self.Bind(EVT_TIMER, self.onTimer, self._timer)

        self._initUi()
        self._loadDataset(0)

    def _initUi(self):
        """
        Build frame layout with top toolbar, splitter canvas/inspector, and status bar.
        """
        mainPane: SizedPanel = self.GetContentsPane()

        self._buildPlaybackRow(mainPane)
        self._buildEditRow(mainPane)

        self._splitter: SplitterWindow = SplitterWindow(mainPane, ID_ANY)
        self._splitter.SetSizerProps(expand=True, proportion=1)

        self._canvasPanel:    CanvasPanel    = CanvasPanel(self._splitter)
        self._inspectorPanel: InspectorPanel = InspectorPanel(self._splitter)

        self._splitter.SplitVertically(self._canvasPanel, self._inspectorPanel, DEFAULT_SASH_POSITION)
        self._splitter.SetSashGravity(SPLITTER_SASH_RATIO)
        self._splitter.SetMinimumPaneSize(250)

        self._statusBar: StatusBar = self.CreateStatusBar(2)
        self._statusBar.SetStatusWidths([-3, -1])

        self.Layout()
        splitterWidth: int = self._splitter.GetClientSize().width
        if splitterWidth > 0:
            self._splitter.SetSashPosition(int(splitterWidth * SPLITTER_SASH_RATIO))

    def _buildPlaybackRow(self, parent: SizedPanel):
        """
        Build the top toolbar row with dataset selector, playback buttons, and step slider.

        Args:
            parent: Parent SizedPanel container.
        """
        rowOnePanel: SizedPanel = SizedPanel(parent, ID_ANY)
        rowOnePanel.SetSizerType('horizontal')
        rowOnePanel.SetSizerProps(expand=True)

        datasetLabel: StaticText = StaticText(rowOnePanel, ID_ANY, 'Dataset:')
        datasetLabel.SetSizerProps(valign='center')

        datasetNames: List[str] = [d.name for d in self._datasets]
        self._datasetChoice: Choice = Choice(rowOnePanel, ID_ANY, choices=datasetNames)
        self._datasetChoice.SetSelection(0)
        self._datasetChoice.Bind(EVT_CHOICE, self.onDatasetChanged)

        self._btnReset: Button = Button(rowOnePanel, ID_ANY, '↺ Reset')
        self._btnReset.Bind(EVT_BUTTON, self.onReset)

        self._btnStepBack: Button = Button(rowOnePanel, ID_ANY, '◀ Step Back')
        self._btnStepBack.Bind(EVT_BUTTON, self.onStepBack)

        self._btnStepForward: Button = Button(rowOnePanel, ID_ANY, 'Step Fwd ▶')
        self._btnStepForward.Bind(EVT_BUTTON, self.onStepForward)

        self._btnStepAll: Button = Button(rowOnePanel, ID_ANY, '⏭ Step All')
        self._btnStepAll.Bind(EVT_BUTTON, self.onStepAll)

        self._btnPlay: Button = Button(rowOnePanel, ID_ANY, '▶ Auto-Play')
        self._btnPlay.Bind(EVT_BUTTON, self.onTogglePlay)

        sliderLabel: StaticText = StaticText(rowOnePanel, ID_ANY, 'Step:')
        sliderLabel.SetSizerProps(valign='center')

        self._stepSlider: Slider = Slider(rowOnePanel, ID_ANY, 0, 0, 2, style=SL_HORIZONTAL)
        self._stepSlider.Bind(EVT_SLIDER, self.onSliderChanged)

    def _buildEditRow(self, parent: SizedPanel):
        """
        Build the second toolbar row with vertex, edge, and subdivision controls.

        Args:
            parent: Parent SizedPanel container.
        """
        rowTwoPanel: SizedPanel = SizedPanel(parent, ID_ANY)
        rowTwoPanel.SetSizerType('horizontal')
        rowTwoPanel.SetSizerProps(expand=True)

        vertexLabel: StaticText = StaticText(rowTwoPanel, ID_ANY, 'Node:')
        vertexLabel.SetSizerProps(valign='center')

        self._vertexNameText: TextCtrl = TextCtrl(rowTwoPanel, ID_ANY, 'v1', size=Size(50, -1))

        self._btnAddVertex: Button = Button(rowTwoPanel, ID_ANY, '+ Add Vertex')
        self._btnAddVertex.Bind(EVT_BUTTON, self.onAddVertex)

        edgeULabel: StaticText = StaticText(rowTwoPanel, ID_ANY, 'Edge u:')
        edgeULabel.SetSizerProps(valign='center')

        self._edgeUChoice: Choice = Choice(rowTwoPanel, ID_ANY)

        edgeVLabel: StaticText = StaticText(rowTwoPanel, ID_ANY, 'v:')
        edgeVLabel.SetSizerProps(valign='center')

        self._edgeVChoice: Choice = Choice(rowTwoPanel, ID_ANY)

        self._btnAddEdge: Button = Button(rowTwoPanel, ID_ANY, '+ Add Edge')
        self._btnAddEdge.Bind(EVT_BUTTON, self.onAddEdge)

        adHocULabel: StaticText = StaticText(rowTwoPanel, ID_ANY, 'Split u:')
        adHocULabel.SetSizerProps(valign='center')

        self._adhocUChoice: Choice = Choice(rowTwoPanel, ID_ANY)
        self._adhocUChoice.Bind(EVT_CHOICE, self.onAdhocUChanged)

        adHocVLabel: StaticText = StaticText(rowTwoPanel, ID_ANY, 'v:')
        adHocVLabel.SetSizerProps(valign='center')

        self._adhocVChoice: Choice = Choice(rowTwoPanel, ID_ANY)

        newNodeLabel: StaticText = StaticText(rowTwoPanel, ID_ANY, 'New Node:')
        newNodeLabel.SetSizerProps(valign='center')

        self._adhocNewText: TextCtrl = TextCtrl(rowTwoPanel, ID_ANY, 'v_mid', size=Size(65, -1))

        self._btnExecuteAdhoc: Button = Button(rowTwoPanel, ID_ANY, '+ Subdivide Edge')
        self._btnExecuteAdhoc.Bind(EVT_BUTTON, self.onExecuteAdhoc)

    def _loadDataset(self, datasetIndex: int):
        """
        Switch to the specified dataset preset and reset execution state.

        Args:
            datasetIndex: Index into _datasets list.
        """
        self._currentDatasetIndex = datasetIndex
        self._currentStepIndex = 0
        self._operations = DcelSteps(list(self._datasets[datasetIndex].plannedSteps))
        self._positionOverrides.clear()

        totalSteps: int = len(self._operations)
        self._stepSlider.SetRange(0, totalSteps)
        self._stepSlider.SetValue(0)

        self._refreshState()

    def _getAllSteps(self) -> DcelSteps:
        """
        Return active ordered list of DCEL building steps.

        Returns:
            DcelSteps operation specifications.
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
    ) -> Tuple[Graph, DoublyConnectedEdgeList, NodePositions, Optional[NodeId], str]:
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
        positions: NodePositions = NodePositions({})
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
                stepPos: Optional[CanvasPoint] = step.position
                if stepPos is not None:
                    positions[step.u] = CanvasPoint((stepPos[0] * NODE_SPREAD_FACTOR, stepPos[1] * NODE_SPREAD_FACTOR))
                else:
                    count: int = len(positions)
                    positions[step.u] = CanvasPoint((
                        (120.0 + (count % 4) * 120.0) * NODE_SPREAD_FACTOR,
                        (120.0 + (count // 4) * 120.0) * NODE_SPREAD_FACTOR,
                    ))
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
                    posU: CanvasPoint = positions[step.u]
                    posV: CanvasPoint = positions[stepV]
                    positions[stepNewNode] = CanvasPoint(((posU[0] + posV[0]) / 2.0, (posU[1] + posV[1]) / 2.0))
                else:
                    positions[stepNewNode] = CanvasPoint((250.0 * NODE_SPREAD_FACTOR, 200.0 * NODE_SPREAD_FACTOR))

            for movedNode, movedPos in self._positionOverrides.items():
                if movedNode in positions:
                    positions[movedNode] = movedPos

        return baseGraph, dcel, positions, lastInserted, lastAction

    def _computeDcelAtStep(
        self,
        stepIndex: int,
    ) -> StepState:
        """
        Reconstruct DCEL from an empty state by replaying steps up to stepIndex.

        Args:
            stepIndex: Target step count.

        Returns:
            StepState encapsulating dcel, positions, lastInsertedNode, and lastAction.
        """
        dcel: DoublyConnectedEdgeList
        positions: NodePositions
        lastInserted: Optional[NodeId]
        lastAction: str
        _, dcel, positions, lastInserted, lastAction = self._replaySteps(stepIndex)

        return StepState(dcel, positions, lastInserted, lastAction)

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

        stepState: StepState = self._computeDcelAtStep(self._currentStepIndex)
        dcel: DoublyConnectedEdgeList = stepState.dcel

        self._canvasPanel.renderDcel(dcel, stepState.positions, stepState.insertedNode)
        self._inspectorPanel.updateTables(dcel)

        self._updateAdhocChoices(dcel)
        self._updateBuilderChoices(dcel)

        numV: int = len(dcel.vertexDict)
        numE: int = len(dcel.halfEdgeDict) // 2
        numF: int = len(dcel.faceDict)
        eulerVal: int = numV - numE + numF

        self._statusBar.SetStatusText(f'Step {self._currentStepIndex}/{totalSteps}: {stepState.lastAction}', 0)
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
        dcel: DoublyConnectedEdgeList = self._computeDcelAtStep(self._currentStepIndex).dcel
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

        dcel: DoublyConnectedEdgeList = self._computeDcelAtStep(self._currentStepIndex).dcel
        if nodeName in dcel.vertexDict:
            self._statusBar.SetStatusText(f'Vertex {nodeName!r} already exists', 0)
            return

        newStep: DcelStep = DcelStep('add_vertex', nodeName, position=CanvasPoint((clickX, clickY)))
        self._operations = DcelSteps(list(self._operations[:self._currentStepIndex]) + [newStep])
        self._currentStepIndex = len(self._operations)
        self._refreshState()

    def onVertexDragged(self, nodeId: NodeId, newX: float, newY: float):
        """
        Update a vertex position in-place while dragging on the canvas.

        Args:
            nodeId: Identifier of the dragged vertex.
            newX: Current X drag coordinate on canvas.
            newY: Current Y drag coordinate on canvas.
        """
        self._positionOverrides[nodeId] = CanvasPoint((newX, newY))
        self._canvasPanel.dragVertex(nodeId, newX, newY)

    def onVertexMoved(self, nodeId: NodeId, newX: float, newY: float):
        """
        Record updated canvas coordinates for a dragged vertex and refresh the diagram.

        Args:
            nodeId: Identifier of the dragged vertex.
            newX: New X coordinate on canvas.
            newY: New Y coordinate on canvas.
        """
        self._positionOverrides[nodeId] = CanvasPoint((newX, newY))
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

        stepState: StepState = self._computeDcelAtStep(self._currentStepIndex)
        dcel: DoublyConnectedEdgeList = stepState.dcel
        positions: NodePositions = stepState.positions
        if nodeName in dcel.vertexDict:
            self._statusBar.SetStatusText(f'Vertex {nodeName!r} already exists', 0)
            return

        count: int = len(positions)
        posX: float = (120.0 + (count % 4) * 120.0) * NODE_SPREAD_FACTOR
        posY: float = (120.0 + (count // 4) * 120.0) * NODE_SPREAD_FACTOR
        newStep: DcelStep = DcelStep('add_vertex', nodeName, position=CanvasPoint((posX, posY)))
        self._operations = DcelSteps(list(self._operations[:self._currentStepIndex]) + [newStep])
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
        self._operations = DcelSteps(list(self._operations[:self._currentStepIndex]) + [newStep])
        self._currentStepIndex = len(self._operations)
        self._refreshState()

    def onAdhocUChanged(self, _event: CommandEvent):
        """
        Update destination choices when origin node selection changes.

        Args:
            _event: wx CommandEvent.
        """
        selectedU: str = self._adhocUChoice.GetStringSelection()
        dcel: DoublyConnectedEdgeList = self._computeDcelAtStep(self._currentStepIndex).dcel
        self._updateAdhocVChoices(dcel, selectedU)

    def onReset(self, _event: CommandEvent):
        """
        Handle Reset button click.

        Args:
            _event: wx CommandEvent.
        """
        self._currentStepIndex = 0
        self._operations = DcelSteps(list(self._datasets[self._currentDatasetIndex].plannedSteps))
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

        dcel: DoublyConnectedEdgeList = self._computeDcelAtStep(self._currentStepIndex).dcel

        if (uSelection, vSelection) not in dcel.halfEdgeDict:
            self._statusBar.SetStatusText(f'Cannot subdivide: edge ({uSelection}, {vSelection}) does not exist in current DCEL', 0)
            return

        if not newName:
            newName = f'v_{uSelection}_{vSelection}'

        if newName in dcel.vertexDict:
            self._statusBar.SetStatusText(f'Cannot subdivide: vertex {newName!r} already exists', 0)
            return

        newStep: DcelStep = DcelStep('subdivide', uSelection, v=vSelection, newNode=newName)
        self._operations = DcelSteps(list(self._operations[:self._currentStepIndex]) + [newStep])
        self._currentStepIndex = len(self._operations)
        self._refreshState()
