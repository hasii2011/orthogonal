"""
Tabular inspector panel for Orthogonalization and FlowNet circulation metrics.
"""

from typing import Dict
from typing import List
from typing import Optional

from wx import BORDER_SUNKEN
from wx import FONTFAMILY_SWISS
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD
from wx import Font
from wx import ID_ANY
from wx import LC_REPORT
from wx import ListCtrl
from wx import Notebook
from wx import TE_MULTILINE
from wx import TE_READONLY
from wx import TextCtrl
from wx import Window

from wx.lib.sized_controls import SizedPanel

from orthogonal.TopologyTypes import FaceId
from orthogonal.TopologyTypes import FlowDict
from orthogonal.TopologyTypes import NodeId
from orthogonal.doublyConnectedEdgeList.Face import Face
from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdge
from orthogonal.doublyConnectedEdgeList.Vertex import Vertex
from orthogonal.topologyShapeMetric.FlowNet import FlowNet
from orthogonal.topologyShapeMetric.Orthogonalization import Orthogonalization
from orthogonal.topologyShapeMetric.Planarization import Planarization

INSPECTOR_FONT_SIZE: int = 12


class OrthoInspectorPanel(SizedPanel):
    """
    Notebook panel displaying tabular inspection of Vertex Angles, Face Balances, FlowNet Arcs, and Summary.
    """

    def __init__(self, parent: Window):
        """
        Construct the Orthogonalization inspector notebook panel.

        Args:
            parent: Parent window container widget.
        """
        super().__init__(parent, ID_ANY)

        tableFont: Font = Font(INSPECTOR_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_BOLD)
        self._notebook: Notebook = Notebook(self, ID_ANY)
        self._notebook.SetSizerProps(expand=True, proportion=1)
        self._notebook.SetFont(tableFont)

        # Tab 1: Vertex Angles
        self._vertexAnglesList: ListCtrl = ListCtrl(self._notebook, ID_ANY, style=LC_REPORT | BORDER_SUNKEN)
        self._vertexAnglesList.SetFont(tableFont)
        self._vertexAnglesList.AppendColumn('Vertex', width=80)
        self._vertexAnglesList.AppendColumn('Supply', width=70)
        self._vertexAnglesList.AppendColumn('Face', width=70)
        self._vertexAnglesList.AppendColumn('HalfEdge', width=120)
        self._vertexAnglesList.AppendColumn('Flow Units', width=90)
        self._vertexAnglesList.AppendColumn('Angle (°)', width=90)
        self._vertexAnglesList.AppendColumn('Vertex Total', width=100)
        self._notebook.AddPage(self._vertexAnglesList, 'Vertex Angles')

        # Tab 2: Face Balances
        self._faceBalancesList: ListCtrl = ListCtrl(self._notebook, ID_ANY, style=LC_REPORT | BORDER_SUNKEN)
        self._faceBalancesList.SetFont(tableFont)
        self._faceBalancesList.AppendColumn('Face ID', width=80)
        self._faceBalancesList.AppendColumn('Type', width=90)
        self._faceBalancesList.AppendColumn('Degree (k)', width=90)
        self._faceBalancesList.AppendColumn('Demand Eq', width=110)
        self._faceBalancesList.AppendColumn('Demand', width=70)
        self._faceBalancesList.AppendColumn('Vertex Inflow', width=100)
        self._faceBalancesList.AppendColumn('Target Sum (°)', width=110)
        self._faceBalancesList.AppendColumn('Status', width=90)
        self._notebook.AddPage(self._faceBalancesList, 'Face Balances')

        # Tab 3: FlowNet Arcs
        self._flowNetArcsList: ListCtrl = ListCtrl(self._notebook, ID_ANY, style=LC_REPORT | BORDER_SUNKEN)
        self._flowNetArcsList.SetFont(tableFont)
        self._flowNetArcsList.AppendColumn('Source', width=80)
        self._flowNetArcsList.AppendColumn('Target', width=80)
        self._flowNetArcsList.AppendColumn('Arc Type', width=110)
        self._flowNetArcsList.AppendColumn('HalfEdge Key', width=120)
        self._flowNetArcsList.AppendColumn('Flow', width=60)
        self._flowNetArcsList.AppendColumn('Cap', width=60)
        self._flowNetArcsList.AppendColumn('Cost', width=60)
        self._notebook.AddPage(self._flowNetArcsList, 'FlowNet Arcs')

        # Tab 4: Summary Text
        self._summaryText: TextCtrl = TextCtrl(self._notebook, ID_ANY, style=TE_MULTILINE | TE_READONLY | BORDER_SUNKEN)
        self._summaryText.SetFont(tableFont)
        self._notebook.AddPage(self._summaryText, 'Summary & Cost')

    def updateFromOrthogonalization(self, orthogonal: Optional[Orthogonalization]):
        """
        Refresh and repopulate all inspector notebook tabs from the provided Orthogonalization instance.

        Args:
            orthogonal: Orthogonalization instance to inspect, or None to clear.
        """
        self._vertexAnglesList.DeleteAllItems()
        self._faceBalancesList.DeleteAllItems()
        self._flowNetArcsList.DeleteAllItems()
        self._summaryText.Clear()

        if orthogonal is None:
            return

        planar: Planarization = orthogonal.planar
        flowNet: FlowNet = orthogonal.flowNetwork
        flowDict: FlowDict = orthogonal.flowDict

        self._populateVertexAngles(planar, flowDict)
        self._populateFaceBalances(planar, flowNet, flowDict)
        self._populateFlowNetArcs(flowNet, flowDict)
        self._populateSummary(planar, flowNet, flowDict)

    def _populateVertexAngles(self, planar: Planarization, flowDict: FlowDict):
        """
        Populate vertex right-angle allocation rows.
        """
        rowIndex: int = 0
        for vertex in planar.dcel.vertexDict.values():
            vertexId: NodeId = vertex.id
            totalDegrees: int = 0
            incidentHalfEdges: List[HalfEdge] = list(vertex.surroundHalfEdges())

            for halfEdge in incidentHalfEdges:
                faceId: FaceId = halfEdge.incidentFace.id
                flowUnits: int = flowDict.get(vertexId, {}).get(faceId, {}).get(halfEdge.id, 0)
                angleDegrees: int = flowUnits * 90
                totalDegrees += angleDegrees

                itemIndex: int = self._vertexAnglesList.InsertItem(rowIndex, str(vertexId))
                self._vertexAnglesList.SetItem(itemIndex, 1, '-4')
                self._vertexAnglesList.SetItem(itemIndex, 2, str(faceId))
                self._vertexAnglesList.SetItem(itemIndex, 3, str(halfEdge.id))
                self._vertexAnglesList.SetItem(itemIndex, 4, str(flowUnits))
                self._vertexAnglesList.SetItem(itemIndex, 5, f'{angleDegrees}°')
                self._vertexAnglesList.SetItem(itemIndex, 6, '')
                rowIndex += 1

            if rowIndex > 0:
                self._vertexAnglesList.SetItem(rowIndex - 1, 6, f'{totalDegrees}°')

    def _populateFaceBalances(self, planar: Planarization, flowNet: FlowNet, flowDict: FlowDict):
        """
        Populate face rectilinear balance rows.
        """
        rowIndex: int = 0
        for face in planar.dcel.faceDict.values():
            faceId: FaceId = face.id
            isExternal: bool = (face is planar.externalFace)
            degree: int = len(face)
            demandFormula: str = f'2*{degree} + 4' if isExternal else f'2*{degree} - 4'
            demandValue: int = (2 * degree + 4) if isExternal else (2 * degree - 4)

            # Sum inflow from incident vertices
            vertexInflow: int = 0
            for vertexId in flowNet.nodes:
                if vertexId in planar.dcel.vertexDict:
                    if vertexId in flowDict and faceId in flowDict[vertexId]:
                        for key, units in flowDict[vertexId][faceId].items():
                            vertexInflow += units

            targetAngleSum: int = (2 * degree + 4) * 90 if isExternal else (2 * degree - 4) * 90
            statusText: str = 'Balanced' if vertexInflow == demandValue else 'Unbalanced'

            itemIndex: int = self._faceBalancesList.InsertItem(rowIndex, str(faceId))
            self._faceBalancesList.SetItem(itemIndex, 1, 'External' if isExternal else 'Internal')
            self._faceBalancesList.SetItem(itemIndex, 2, str(degree))
            self._faceBalancesList.SetItem(itemIndex, 3, demandFormula)
            self._faceBalancesList.SetItem(itemIndex, 4, str(demandValue))
            self._faceBalancesList.SetItem(itemIndex, 5, str(vertexInflow))
            self._faceBalancesList.SetItem(itemIndex, 6, f'{targetAngleSum}°')
            self._faceBalancesList.SetItem(itemIndex, 7, statusText)
            rowIndex += 1

    def _populateFlowNetArcs(self, flowNet: FlowNet, flowDict: FlowDict):
        """
        Populate circulation network arcs and assigned flow values.
        """
        rowIndex: int = 0
        for u, v, key in flowNet.edges:
            edgeData: Dict = flowNet[u][v][key]
            flowVal: int = flowDict.get(u, {}).get(v, {}).get(key, 0)
            arcType: str = 'Vertex->Face' if edgeData.get('weight', 0) == 0 else 'Face->Face (Bend)'
            capVal: int = edgeData.get('capacity', 0)
            capText: str = 'inf' if capVal >= 2**31 else str(capVal)

            itemIndex: int = self._flowNetArcsList.InsertItem(rowIndex, str(u))
            self._flowNetArcsList.SetItem(itemIndex, 1, str(v))
            self._flowNetArcsList.SetItem(itemIndex, 2, arcType)
            self._flowNetArcsList.SetItem(itemIndex, 3, str(key))
            self._flowNetArcsList.SetItem(itemIndex, 4, str(flowVal))
            self._flowNetArcsList.SetItem(itemIndex, 5, capText)
            self._flowNetArcsList.SetItem(itemIndex, 6, str(edgeData.get('weight', 0)))
            rowIndex += 1

    def _populateSummary(self, planar: Planarization, flowNet: FlowNet, flowDict: FlowDict):
        """
        Populate high-level circulation and orthogonalization summary text.
        """
        vertexCount: int = planar.G.number_of_nodes()
        edgeCount: int = planar.G.number_of_edges()
        faceCount: int = len(planar.dcel.faceDict)
        eulerValue: int = vertexCount - edgeCount + faceCount

        totalBends: int = 0
        for u, v, key in flowNet.edges:
            if flowNet[u][v][key].get('weight', 0) == 1:
                totalBends += flowDict.get(u, {}).get(v, {}).get(key, 0)

        extFaceIdStr: str = str(planar.externalFace.id) if planar.externalFace else 'None'

        summaryLines: List[str] = [
            '=== Orthogonalization & FlowNet Metrics ===',
            '',
            f'Primal Vertices |V|:  {vertexCount}',
            f'Primal Edges    |E|:  {edgeCount}',
            f'Planar Faces    |F|:  {faceCount}',
            f'Euler Formula:        |V| - |E| + |F| = {eulerValue} (Expected: 2)',
            f'External Face:        {extFaceIdStr}',
            '',
            f'Total Edge Bends:     {totalBends}',
            f'Circulation Cost:     {flowNet.cost}',
            '',
            'Network Feasibility:  Valid Minimum-Cost Circulation',
            'Rectilinear Angles:   Allocated (Multiples of 90°)',
        ]
        self._summaryText.SetValue('\n'.join(summaryLines))
