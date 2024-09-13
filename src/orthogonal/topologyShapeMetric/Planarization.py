
from typing import Dict
from typing import Tuple

from logging import Logger
from logging import getLogger

import math as m

import networkx as nx

from networkx import Graph

from orthogonal.doublyConnectedEdgeList.Dcel import Dcel
from orthogonal.topologyShapeMetric.OrthogonalException import OrthogonalException

NODE_NAME = str
POSITION  = Tuple[int, int]
POSITIONS = Dict[NODE_NAME, POSITION]


class Planarization:
    """
    This step determines the topology of the drawing which is described by a planar embedding.
    """

    def __init__(self, G: Graph, pos: POSITIONS = None):

        if nx.number_of_selfloops(G) != 0:
            raise OrthogonalException('There can be no self loops in the graph')

        if nx.is_connected(G) is False:
            raise OrthogonalException('The graph or parts of it are not connected.')

        self.logger: Logger = getLogger(__name__)
        if pos is None:
            is_planar, self.embedding = nx.check_planarity(G)
            assert is_planar
            pos = nx.combinatorial_embedding_to_pos(self.embedding)
        else:
            if self.numberOfCrossings(G, pos) != 0:
                raise OrthogonalException('The graph has edges that cross each other')
            self.embedding: nx.PlanarEmbedding = self.convert_pos_to_embedding(G, pos)

        self.G: Graph = G.copy()
        self.pos = pos  # is only used to find the ext_face now.
        self.dcel: Dcel = Dcel(G, self.embedding)
        self.ext_face   = self.get_external_face()

    def copy(self):
        new_planar = self.__new__(self.__class__)
        new_planar.__init__(self.G, self.pos)
        return new_planar

    def get_external_face(self):
        def left_most(G, pos):
            corner_node = min(pos, key=lambda k: (pos[k][0], pos[k][1]))
            other = max(
                G.adj[corner_node], key=lambda node:
                (pos[node][1] - pos[corner_node][1]) /
                m.hypot(
                    pos[node][0] - pos[corner_node][0],
                    pos[node][1] - pos[corner_node][1]
                )
            )  # maximum cosine value
            return sorted([corner_node, other], key=lambda node:
                          (pos[node][1], pos[node][0]))

        if len(self.pos) < 2:
            return list(self.dcel.face_dict.values())[0]
        down, up = left_most(self.G, self.pos)
        return self.dcel.half_edge_dict[up, down].inc

    def dfs_face_order(self):  # dfs dual graph, starts at ext_face
        def dfs_face(face, marked):
            marked.add(face.id)
            yield face
            for neighbor_face in set(face.surround_faces()):
                if neighbor_face.id not in marked:
                    yield from dfs_face(neighbor_face, marked)
        yield from dfs_face(self.ext_face, set())

    def numberOfCrossings(self, G, pos, printIt=True):
        """
        Not accurate, may be equal to actual number or double
        """
        def is_cross(pa, pb, pc, pd):
            def xmul(v1, v2):
                return v1[0] * v2[1] - v1[1] * v2[0]

            def f(pa, pb, p):
                return (pa[1] - pb[1]) * (p[0] - pb[0]) - (p[1] - pb[1]) * (pa[0] - pb[0])

            ca = (pa[0] - pc[0], pa[1] - pc[1])
            cb = (pb[0] - pc[0], pb[1] - pc[1])
            cd = (pd[0] - pc[0], pd[1] - pc[1])
            # return xmul(ca, cd) >= 0 and xmul(cd, cb) >= 0 and f(pa, pb, pc) * f(pa, pb, pd) < 0  # PyCharm Optimization
            return xmul(ca, cd) >= 0 > f(pa, pb, pc) * f(pa, pb, pd) and xmul(cd, cb) >= 0
        count = 0
        for nodeA, nodeB in G.edges:
            for nodeC, nodeD in G.edges:
                if nodeA not in (nodeC, nodeD) and nodeB not in (nodeC, nodeD):
                    if is_cross(pos[nodeA], pos[nodeB], pos[nodeC], pos[nodeD]):
                        count += 1
                        if printIt is True:
                            self.logger.info(nodeA, nodeB, nodeC, nodeD)
        return count

    def convert_pos_to_embedding(self, G: Graph, pos) -> nx.PlanarEmbedding:
        """
            Only straight line in G.
        """
        emd: nx.PlanarEmbedding = nx.PlanarEmbedding()
        for node in G:
            neigh_pos = {
                neigh: (pos[neigh][0]-pos[node][0], pos[neigh][1]-pos[node][1]) for neigh in G[node]
            }
            neighbors_sorted = sorted(G.adj[node], key=lambda v: m.atan2(neigh_pos[v][1], neigh_pos[v][0]))  # counter clockwise
            last = None
            for neigh in neighbors_sorted:
                emd.add_half_edge_ccw(node, neigh, last)
                last = neigh
        emd.check_structure()
        return emd
