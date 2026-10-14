
from orthogonal.TopologyTypes import FlowDict
from orthogonal.topologyShapeMetric.FlowNet import FlowNet
from orthogonal.topologyShapeMetric.OrthogonalException import OrthogonalException
from orthogonal.topologyShapeMetric.Planarization import Planarization


class Orthogonalization:
    """
    Works on a planar embedding, changes shape of the graph.
    """

    def __init__(self, planar: Planarization):

        for pair in planar.G.degree:
            if pair[1] > 4:
                raise OrthogonalException('There is a node in this graph with a degree greater than 4')
        assert planar.G.number_of_nodes() > 1

        self._planar:      Planarization = planar
        self._flowNetwork: FlowNet       = self._faceDetermination()
        self._flowDict:    FlowDict      = self._tamassiaOrthogonalization()

    @property
    def planar(self) -> Planarization:
        """
        Get the underlying planar embedding.

        Returns:
            Planarization instance.
        """
        return self._planar

    @property
    def flowNetwork(self) -> FlowNet:
        """
        Get the flow network used for circulation.

        Returns:
            FlowNet instance.
        """
        return self._flowNetwork

    @property
    def flowDict(self) -> FlowDict:
        """
        Get the dictionary of edge flows fulfilling demand at minimum cost.

        Returns:
            FlowDict instance containing calculated flows.
        """
        return self._flowDict

    def _faceDetermination(self) -> FlowNet:
        flowNetwork: FlowNet = FlowNet()

        for vertex in self._planar.dcel.vertexDict.values():
            flowNetwork.addVertexNode(vertex.id)

        for face in self._planar.dcel.faceDict.values():
            flowNetwork.addFaceNode(face.id, len(face), face is self._planar.externalFace)

        for vertex in self._planar.dcel.vertexDict.values():
            for he in vertex.surroundHalfEdges():
                flowNetwork.addVertexToFaceEdge(vertex.id, he.incidentFace.id, he.id)

        for he in self._planar.dcel.halfEdgeDict.values():
            flowNetwork.addFaceToFaceEdge(he.twin.incidentFace.id, he.incidentFace.id, he.id)  # lf -> rf

        return flowNetwork

    def _tamassiaOrthogonalization(self) -> FlowDict:
        return self._flowNetwork.minCostFlow()
