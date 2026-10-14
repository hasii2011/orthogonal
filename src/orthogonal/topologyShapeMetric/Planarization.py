
from typing import Dict
from typing import Mapping
from typing import Optional
from typing import Tuple
from typing import Union

from logging import Logger
from logging import getLogger

import math as m

import networkx as nx

from networkx import Graph

from orthogonal.doublyConnectedEdgeList.DoublyConnectedEdgeList import DoublyConnectedEdgeList
from orthogonal.geometry.Geometry2D import Geometry2D
from orthogonal.geometry.Geometry2D import NodeCoordinate
from orthogonal.TopologyTypes import NodeId
from orthogonal.topologyShapeMetric.OrthogonalException import OrthogonalException


type RawCoordinate    = Tuple[int, int]
type CoordinateInput  = Union[NodeCoordinate, RawCoordinate]
type RawNodePositions = Mapping[NodeId, CoordinateInput]
type NodePositions    = Dict[NodeId, NodeCoordinate]


class Planarization:
    """
    This step determines the topology of the drawing which is described by a planar embedding.
    """

    def __init__(self, G: Graph, pos: Optional[RawNodePositions] = None):

        if nx.number_of_selfloops(G) != 0:
            raise OrthogonalException('There can be no self loops in the graph')

        if nx.is_connected(G) is False:
            raise OrthogonalException('The graph or parts of it are not connected.')

        self.logger: Logger = getLogger(__name__)
        self.embedding: nx.PlanarEmbedding
        normalizedPos: NodePositions
        if not pos:
            isPlanar, rawEmbedding = nx.check_planarity(G)
            if not isPlanar or not isinstance(rawEmbedding, nx.PlanarEmbedding):
                raise OrthogonalException('The graph is not planar')
            self.embedding = rawEmbedding
            normalizedPos = {
                node: NodeCoordinate(coord[0], coord[1])
                for node, coord in nx.combinatorial_embedding_to_pos(self.embedding).items()
            }
        else:
            normalizedPos = {
                node: NodeCoordinate(coord[0], coord[1])
                for node, coord in pos.items()
            }
            if self._numberOfCrossings(G, normalizedPos) != 0:
                raise OrthogonalException('The graph has edges that cross each other')
            self.embedding = self._convertPosToEmbedding(G, normalizedPos)

        self.G: Graph = G.copy()
        self.pos: NodePositions = normalizedPos  # is only used to find the ext_face now.
        self.dcel: DoublyConnectedEdgeList = DoublyConnectedEdgeList(G, self.embedding)
        self.ext_face   = self._getExternalFace()

    def dfsFaceOrder(self):  # dfs dual graph, starts at ext_face
        def dfs_face(face, marked):
            marked.add(face.id)
            yield face
            for neighbor_face in set(face.surroundFaces()):
                if neighbor_face.id not in marked:
                    yield from dfs_face(neighbor_face, marked)
        yield from dfs_face(self.ext_face, set())

    def copy(self):
        return self.__class__(self.G, self.pos)

    def _getExternalFace(self):
        def leftMost(G: Graph, pos: NodePositions):
            cornerNode = min(pos, key=lambda k: (pos[k].x, pos[k].y))
            other = max(
                G.adj[cornerNode], key=lambda node:
                (pos[node].y - pos[cornerNode].y) /
                m.hypot(
                    pos[node].x - pos[cornerNode].x,
                    pos[node].y - pos[cornerNode].y
                )
            )  # maximum cosine value
            return sorted([cornerNode, other], key=lambda node:
                          (pos[node].y, pos[node].x))

        if len(self.pos) < 2:
            return list(self.dcel.faceDict.values())[0]
        down, up = leftMost(self.G, self.pos)
        return self.dcel.halfEdgeDict[up, down].incidentFace

    def _numberOfCrossings(self, G: Graph, pos: NodePositions, printIt: bool = True) -> int:
        """
        Not accurate, may be equal to actual number or double
        """
        count: int = 0
        for nodeA, nodeB in G.edges:
            for nodeC, nodeD in G.edges:
                if nodeA not in (nodeC, nodeD) and nodeB not in (nodeC, nodeD):
                    if Geometry2D.isCross(pos[nodeA], pos[nodeB], pos[nodeC], pos[nodeD]):
                        count += 1
                        if printIt is True:
                            self.logger.info(nodeA, nodeB, nodeC, nodeD)
        return count

    def _convertPosToEmbedding(self, G: Graph, pos: NodePositions) -> nx.PlanarEmbedding:
        """
            Only straight line in G.
        """
        emd: nx.PlanarEmbedding = nx.PlanarEmbedding()
        for node in G:
            neighPos: Dict[NodeId, NodeCoordinate] = {
                neigh: NodeCoordinate(pos[neigh].x - pos[node].x, pos[neigh].y - pos[node].y) for neigh in G[node]
            }
            neighborsSorted = sorted(G.adj[node], key=lambda v: m.atan2(neighPos[v].y, neighPos[v].x))  # counter clockwise
            last = None
            for neigh in neighborsSorted:
                emd.add_half_edge_ccw(node, neigh, last)
                last = neigh
        emd.check_structure()
        return emd
