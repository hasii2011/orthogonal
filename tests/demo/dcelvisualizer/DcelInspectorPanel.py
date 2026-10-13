
from wx import BORDER_SUNKEN
from wx import FONTFAMILY_SWISS
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD
from wx import Font
from wx import ID_ANY
from wx import LC_REPORT
from wx import ListCtrl
from wx import Notebook
from wx import Window

from wx.lib.sized_controls import SizedPanel

from orthogonal.doublyConnectedEdgeList.DoublyConnectedEdgeList import DoublyConnectedEdgeList

INSPECTOR_FONT_SIZE:  int = 12


class DcelInspectorPanel(SizedPanel):
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
        self._notebook.SetSizerProps(expand=True, proportion=1)
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
