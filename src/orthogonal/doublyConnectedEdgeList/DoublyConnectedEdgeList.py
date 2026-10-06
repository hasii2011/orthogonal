

from typing import Any
from typing import Dict
from typing import Hashable

import networkx as nx

from orthogonal.doublyConnectedEdgeList.Face import Face
from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdge
from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdgeId
from orthogonal.doublyConnectedEdgeList.Vertex import Vertex

type NodeId = Hashable


class DoublyConnectedEdgeList:
    """
    Doubly-Connected Edge List (DCEL) representation of a planar graph.

    Maintains topological connectivity between vertices, half-edges, and faces.
    """

    def __init__(self, G: nx.Graph, embedding: nx.PlanarEmbedding):
        """
        Construct a DCEL from a planar graph and its combinatorial embedding.

        Args:
            G: Planar graph to represent.
            embedding: Planar embedding defining cyclic ordering of edges around vertices.
        """
        assert nx.check_planarity(G)[0]

        self.vertex_dict: Dict[NodeId, Vertex] = {}
        for node in G.nodes:
            self.vertex_dict[node] = Vertex(node)

        self.half_edge_dict: Dict[Any, HalfEdge] = {}
        for u, v in G.edges:
            he1, he2 = HalfEdge(HalfEdgeId((u, v))), HalfEdge(HalfEdgeId((v, u)))
            self.half_edge_dict[he1.id] = he1
            self.half_edge_dict[he2.id] = he2
            he1.twin = he2
            he1.origin = self.vertex_dict[u]
            self.vertex_dict[u].incidentEdge = he1

            he2.twin = he1
            he2.origin = self.vertex_dict[v]
            self.vertex_dict[v].incidentEdge = he2

        for he in self.half_edge_dict.values():
            u, v = he.getPoints()
            he.next = self.half_edge_dict[embedding.next_face_half_edge(u, v)]
            he.next.previous = he

        self.face_dict: Dict[str, Face] = {}
        for he in self.half_edge_dict.values():
            if not he.hasIncidentFace:
                face_id = f'f{len(self.face_dict)}'
                face: Face = Face(face_id)
                face.incidentEdge = he
                self.face_dict[face_id] = face

                face.nodes_id = embedding.traverse_face(*he.getPoints())
                for v1_id, v2_id in zip(face.nodes_id, face.nodes_id[1:]+face.nodes_id[:1]):
                    other = self.half_edge_dict[v1_id, v2_id]
                    assert not other.hasIncidentFace
                    other.incidentFace = face

        if not self.face_dict:
            self.face_dict['f0'] = Face('f0')

    def addNodeBetween(self, u: NodeId, v: NodeId, nodeName: NodeId):
        """
        Insert a new node between existing nodes u and v by splitting the edge.

        Args:
            u: First endpoint of the edge.
            v: Second endpoint of the edge.
            nodeName: Identifier for the new intermediate node.
        """
        midVertex: Vertex = Vertex(nodeName)
        self.vertex_dict[nodeName] = midVertex

        self.__insertNode(u, v, midVertex)
        self.__insertNode(v, u, midVertex)

        for v1, v2 in ((u, midVertex.id), (midVertex.id, v)):
            self.half_edge_dict[v1, v2].twin = self.half_edge_dict[v2, v1]
            self.half_edge_dict[v2, v1].twin = self.half_edge_dict[v1, v2]

    def __insertNode(self, sourceNode: NodeId, targetNode: NodeId, midVertex: Vertex):
        """
        Split a directed half-edge (sourceNode, targetNode) by inserting midVertex.

        Args:
            sourceNode: The origin identifier of the existing half-edge.
            targetNode: The destination identifier of the existing half-edge.
            midVertex: The new intermediate Vertex being inserted.
        """
        he: HalfEdge = self.half_edge_dict.pop((sourceNode, targetNode))
        he1: HalfEdge = HalfEdge(HalfEdgeId((sourceNode, midVertex.id)))
        he2: HalfEdge = HalfEdge(HalfEdgeId((midVertex.id, targetNode)))

        # update half_edge_dict
        self.half_edge_dict[sourceNode, midVertex.id] = he1
        self.half_edge_dict[midVertex.id, targetNode] = he2
        he1.setAll(None, he.origin, he.previous, he2, he.incidentFace)
        he2.setAll(None, midVertex, he1, he.next, he.incidentFace)
        he1.previous.next = he1
        he2.next.previous = he2

        # update face
        if he.incidentFace.incidentEdge is he:
            he.incidentFace.incidentEdge = he1
        he.incidentFace.updateNodes()   # not efficient
