"""
Main application window for the Orthogonalization and FlowNet visualizer.
"""

from typing import List
from typing import Optional

from wx import Button
from wx import CallAfter
from wx import CheckBox
from wx import Choice
from wx import CommandEvent
from wx import EVT_BUTTON
from wx import EVT_CHECKBOX
from wx import EVT_CHOICE
from wx import ID_ANY
from wx import Size
from wx import SplitterWindow
from wx import StaticText
from wx import StatusBar

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from orthogonal.topologyShapeMetric.Orthogonalization import Orthogonalization
from orthogonal.topologyShapeMetric.Planarization import Planarization

from tests.demo.orthovisualizer.OrthoCanvasPanel import OrthoCanvasPanel
from tests.demo.orthovisualizer.OrthoDataSet import OrthoDataSet
from tests.demo.orthovisualizer.OrthoDataSet import createDefaultDataSets
from tests.demo.orthovisualizer.OrthoInspectorPanel import OrthoInspectorPanel

DEFAULT_FRAME_WIDTH:   int   = 1300
DEFAULT_FRAME_HEIGHT:  int   = 850
SPLITTER_SASH_RATIO:   float = 0.62
DEFAULT_SASH_POSITION: int   = int(DEFAULT_FRAME_WIDTH * SPLITTER_SASH_RATIO)


class OrthoVisualizerFrame(SizedFrame):
    """
    Main application frame hosting controls, interactive canvas, and the inspector notebook.
    """

    def __init__(self):
        """
        Construct the Orthogonalization visualizer main frame.
        """
        super().__init__(None, ID_ANY, 'Orthogonalization & FlowNet Visualizer - wxPython ogl', size=Size(DEFAULT_FRAME_WIDTH, DEFAULT_FRAME_HEIGHT))

        self._dataSets: List[OrthoDataSet] = createDefaultDataSets()
        self._currentDataSetIndex: int = 0
        self._orthogonal: Optional[Orthogonalization] = None

        self._initUi()
        self._loadDataSet(0)

    def _initUi(self):
        """
        Construct the top-level toolbar, splitter, canvas, and inspector panels.
        """
        rootPanel: SizedPanel = self.GetContentsPane()
        rootPanel.SetSizerType('vertical')

        # Top Control Toolbar
        toolbarPanel: SizedPanel = SizedPanel(rootPanel, ID_ANY)
        toolbarPanel.SetSizerType('horizontal')
        toolbarPanel.SetSizerProps(expand=True)

        presetLabel: StaticText = StaticText(toolbarPanel, ID_ANY, 'Preset:')
        presetLabel.SetSizerProps(valign='center')

        dataSetNames: List[str] = [ds.name for ds in self._dataSets]
        self._presetChoice: Choice = Choice(toolbarPanel, ID_ANY, choices=dataSetNames)
        self._presetChoice.SetSelection(0)
        self._presetChoice.SetSizerProps(valign='center')
        self._presetChoice.Bind(EVT_CHOICE, self.onPresetChanged)

        # Layer Checkboxes
        self._primalCheck: CheckBox = CheckBox(toolbarPanel, ID_ANY, 'Primal Graph')
        self._primalCheck.SetValue(True)
        self._primalCheck.SetSizerProps(valign='center')
        self._primalCheck.Bind(EVT_CHECKBOX, self.onTogglePrimal)

        self._dualCheck: CheckBox = CheckBox(toolbarPanel, ID_ANY, 'Dual Faces')
        self._dualCheck.SetValue(True)
        self._dualCheck.SetSizerProps(valign='center')
        self._dualCheck.Bind(EVT_CHECKBOX, self.onToggleDual)

        self._flowCheck: CheckBox = CheckBox(toolbarPanel, ID_ANY, 'FlowNet Arcs')
        self._flowCheck.SetValue(True)
        self._flowCheck.SetSizerProps(valign='center')
        self._flowCheck.Bind(EVT_CHECKBOX, self.onToggleFlow)

        self._anglesCheck: CheckBox = CheckBox(toolbarPanel, ID_ANY, 'Angles & Bends')
        self._anglesCheck.SetValue(True)
        self._anglesCheck.SetSizerProps(valign='center')
        self._anglesCheck.Bind(EVT_CHECKBOX, self.onToggleAngles)

        self._resetButton: Button = Button(toolbarPanel, ID_ANY, 'Reset Layout')
        self._resetButton.SetSizerProps(valign='center')
        self._resetButton.Bind(EVT_BUTTON, self.onReset)

        # Main Splitter
        self._splitter: SplitterWindow = SplitterWindow(rootPanel, ID_ANY)
        self._splitter.SetSizerProps(expand=True, proportion=1)

        self._canvasPanel: OrthoCanvasPanel = OrthoCanvasPanel(self._splitter)
        self._inspectorPanel: OrthoInspectorPanel = OrthoInspectorPanel(self._splitter)

        self._splitter.SplitVertically(self._canvasPanel, self._inspectorPanel, DEFAULT_SASH_POSITION)
        self._splitter.SetMinimumPaneSize(250)

        # Status Bar
        self._statusBar: StatusBar = self.CreateStatusBar(2)
        self._statusBar.SetStatusWidths([-3, -2])
        self._statusBar.SetStatusText('Ready', 0)
        self._statusBar.SetStatusText('Circulation: Idle', 1)

    def _loadDataSet(self, index: int):
        """
        Load and solve Orthogonalization for the selected dataset index.

        Args:
            index: Index in self._dataSets.
        """
        if index < 0 or index >= len(self._dataSets):
            return

        self._currentDataSetIndex = index
        dataSet: OrthoDataSet = self._dataSets[index]

        try:
            planar: Planarization = Planarization(dataSet.graph.copy())
            orthogonal: Orthogonalization = Orthogonalization(planar)
            self._orthogonal = orthogonal

            self._canvasPanel.setOrthogonalization(orthogonal, dataSet.initialPositions)
            self._inspectorPanel.updateFromOrthogonalization(orthogonal)
            CallAfter(self._canvasPanel.rebuildDiagram)

            nodeCount: int = dataSet.graph.number_of_nodes()
            edgeCount: int = dataSet.graph.number_of_edges()
            faceCount: int = len(orthogonal.planar.dcel.faceDict)
            costVal: int = orthogonal.flowNetwork.cost

            self._statusBar.SetStatusText(f'Preset: {dataSet.name} | Vertices: {nodeCount} | Edges: {edgeCount} | Faces: {faceCount}', 0)
            self._statusBar.SetStatusText(f'Total Cost: {costVal} | Minimum-Cost Flow Solved', 1)
        except Exception as err:
            self._statusBar.SetStatusText(f'Error loading {dataSet.name}: {err}', 0)

    def onPresetChanged(self, _event: CommandEvent):
        """
        Handle dataset dropdown selection changes.
        """
        selectionIndex: int = self._presetChoice.GetSelection()
        self._loadDataSet(selectionIndex)

    def onTogglePrimal(self, _event: CommandEvent):
        """
        Handle primal graph visibility checkbox toggle.
        """
        self._canvasPanel.showPrimalGraph = self._primalCheck.GetValue()

    def onToggleDual(self, _event: CommandEvent):
        """
        Handle dual face visibility checkbox toggle.
        """
        self._canvasPanel.showDualFaces = self._dualCheck.GetValue()

    def onToggleFlow(self, _event: CommandEvent):
        """
        Handle flow network arcs visibility checkbox toggle.
        """
        self._canvasPanel.showFlowNetArcs = self._flowCheck.GetValue()

    def onToggleAngles(self, _event: CommandEvent):
        """
        Handle angles and bends visibility checkbox toggle.
        """
        self._canvasPanel.showAngleBends = self._anglesCheck.GetValue()

    def onReset(self, _event: CommandEvent):
        """
        Reload the current dataset to reset dragged node positions.
        """
        self._loadDataSet(self._currentDataSetIndex)
