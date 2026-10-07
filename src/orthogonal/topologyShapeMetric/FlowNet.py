
from typing import Tuple

from collections import defaultdict

from networkx import MultiDiGraph
from networkx import min_cost_flow

from orthogonal.TopologyTypes import FaceId
from orthogonal.TopologyTypes import FlowEdgeKey
from orthogonal.TopologyTypes import NodeId


class FlowNet(MultiDiGraph):
    """
    Network flow graph representing the minimum-cost circulation problem
    for orthogonal representation angles and bends.
    """

    def __init__(self):
        """
        Initialize an empty flow network and its circulation metrics.
        """
        super().__init__()
        self._cost: int = 0

    @property
    def cost(self) -> int:
        """
        Get the total circulation cost computed by the network flow solver.

        Returns:
            Total circulation cost as an integer.
        """
        return self._cost

    def addVertexToFaceEdge(self, vertexId: NodeId, faceId: FaceId, key: FlowEdgeKey):
        """
        Add a directed edge from a vertex to an incident face representing angle allocation.

        Args:
            vertexId: Origin vertex identifier.
            faceId: Target incident face identifier.
            key: Half-edge identifier key.
        """
        self.add_edge(vertexId, faceId, key=key, lowerbound=1, capacity=4, weight=0)

    def addFaceToFaceEdge(self, sourceFaceId: FaceId, targetFaceId: FaceId, key: FlowEdgeKey):
        """
        Add a directed edge between adjacent faces representing potential edge bends.

        Args:
            sourceFaceId: Origin face identifier.
            targetFaceId: Destination adjacent face identifier.
            key: Half-edge identifier key.
        """
        self.add_edge(sourceFaceId, targetFaceId, key=key, lowerbound=0, capacity=2**32, weight=1)

    def addVertexNode(self, vertexId: NodeId):
        """
        Add a vertex node to the circulation network with supply demand of -4 (2pi).

        Args:
            vertexId: Unique vertex identifier.
        """
        self.add_node(vertexId, demand=-4)

    def addFaceNode(self, faceId: FaceId, degree: int, isExternal: bool):
        """
        Add a face node with demand determined by bounding degree and external status.

        Args:
            faceId: Unique face identifier.
            degree: Count of bounding edges.
            isExternal: True if face is the unbounded external face.
        """
        self.add_node(faceId, demand=(2 * degree + 4) if isExternal else (2 * degree - 4))

    def minCostFlow(self) -> dict:
        """
        Compute the minimum cost flow for the network.

        Returns:
            Dictionary of edge flows fulfilling demand at minimum cost.
        """
        baseDict, newMdg = self.__split()
        flowDict: dict = min_cost_flow(newMdg)
        for u, v, key in self.edges:
            flowDict[u][v][key] += baseDict[u][v][key]

        self._cost = self.costOfFlow(flowDict)
        return flowDict

    def costOfFlow(self, flowDict: dict) -> int:
        """
        Calculate the total cost of the flow assignment.

        Args:
            flowDict: Mapping of assigned edge flows.

        Returns:
            Total circulation cost as an integer.
        """
        cost: int = 0
        for u, v, key in self.edges:
            cost += flowDict[u][v][key] * self[u][v][key]['weight']
        return cost

    def __getDemand(self, flowDict: dict, node: NodeId | FaceId) -> int:
        """
        Calculate the net flow demand (inflow minus outflow) for a node.

        Args:
            flowDict: Mapping of edge flows keyed by (u, v, key).
            node: Node identifier to calculate demand for.

        Returns:
            Net demand as an integer.
        """
        inFlow: int = sum(
            flowDict[u][v][key]
            for u, v, key in self.in_edges(node, keys=True)
        )
        outFlow: int = sum(
            flowDict[u][v][key]
            for u, v, key in self.out_edges(node, keys=True)
        )
        return inFlow - outFlow

    def __split(self) -> Tuple[dict, MultiDiGraph]:
        """
        Transform the network with non-zero lower bounds into a zero lower-bound circulation graph.

        Returns:
            Tuple of base lower-bound flows and transformed MultiDiGraph.
        """
        baseDict: dict = defaultdict(lambda: defaultdict(dict))
        newMdg: MultiDiGraph = MultiDiGraph()

        for u, v, key in self.edges:
            lowerBound: int = self[u][v][key].get('lowerbound', self[u][v][key].get('lowerBound', 0))
            baseDict[u][v][key] = lowerBound
            newMdg.add_edge(
                u,
                v,
                key,
                capacity=self[u][v][key]['capacity'] - lowerBound,
                weight=self[u][v][key]['weight']
            )
        for node in self:
            newMdg.nodes[node]['demand'] = (
                self.nodes[node]['demand'] - self.__getDemand(baseDict, node)
            )
        return baseDict, newMdg
