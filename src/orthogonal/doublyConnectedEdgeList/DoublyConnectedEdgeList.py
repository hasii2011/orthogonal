
from typing import Any
from typing import Dict

from networkx import Graph
from networkx import PlanarEmbedding
from networkx import check_planarity

from orthogonal.TopologyTypes import FaceId
from orthogonal.TopologyTypes import HalfEdgeId
from orthogonal.TopologyTypes import NodeId
from orthogonal.doublyConnectedEdgeList.Face import Face
from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdge
from orthogonal.doublyConnectedEdgeList.Vertex import Vertex


class DoublyConnectedEdgeList:
    """
    Doubly-Connected Edge List (DCEL) representation of a planar graph.

    Maintains topological connectivity between vertices, half-edges, and faces.
    """
    def __init__(self, G: Graph, embedding: PlanarEmbedding):
        """
        Construct a DCEL from a planar graph and its combinatorial embedding.

        Args:
            G: Planar graph to represent.
            embedding: Planar embedding defining cyclic ordering of edges around vertices.
        """
        assert check_planarity(G)[0]

        self._vertexDict: Dict[NodeId, Vertex] = {}
        for node in G.nodes:
            self._vertexDict[node] = Vertex(node)

        self._halfEdgeDict: Dict[Any, HalfEdge] = {}
        for u, v in G.edges:
            he1, he2 = HalfEdge(HalfEdgeId((u, v))), HalfEdge(HalfEdgeId((v, u)))
            self._halfEdgeDict[he1.id] = he1
            self._halfEdgeDict[he2.id] = he2
            he1.twin = he2
            he1.origin = self._vertexDict[u]
            self._vertexDict[u].incidentEdge = he1

            he2.twin = he1
            he2.origin = self._vertexDict[v]
            self._vertexDict[v].incidentEdge = he2

        for he in self._halfEdgeDict.values():
            u, v = he.getPoints()
            he.next = self._halfEdgeDict[embedding.next_face_half_edge(u, v)]
            he.next.previous = he

        self._faceDict: Dict[FaceId, Face] = {}
        for he in self._halfEdgeDict.values():
            if not he.hasIncidentFace:
                faceId: str = f'f{len(self._faceDict)}'
                face: Face = Face(faceId)
                face.incidentEdge = he
                self._faceDict[faceId] = face

                face.nodes_id = embedding.traverse_face(*he.getPoints())
                for v1Id, v2Id in zip(face.nodes_id, face.nodes_id[1:]+face.nodes_id[:1]):
                    other: HalfEdge = self._halfEdgeDict[v1Id, v2Id]
                    assert not other.hasIncidentFace
                    other.incidentFace = face

        if not self._faceDict:
            self._faceDict['f0'] = Face('f0')

    @property
    def vertexDict(self) -> Dict[NodeId, Vertex]:
        """
        Get the mapping of node IDs to Vertex instances.

        Returns:
            Dictionary mapping NodeId to Vertex.
        """
        return self._vertexDict

    @property
    def halfEdgeDict(self) -> Dict[Any, HalfEdge]:
        """
        Get the mapping of edge ID keys to HalfEdge instances.

        Returns:
            Dictionary mapping edge identifiers to HalfEdge.
        """
        return self._halfEdgeDict

    @property
    def faceDict(self) -> Dict[FaceId, Face]:
        """
        Get the mapping of face IDs to Face instances.

        Returns:
            Dictionary mapping FaceId to Face.
        """
        return self._faceDict

    def addNodeBetween(self, u: NodeId, v: NodeId, nodeName: NodeId):
        """
        Insert a new node between existing nodes u and v by splitting the edge.

        Args:
            u: First endpoint of the edge.
            v: Second endpoint of the edge.
            nodeName: Identifier for the new intermediate node.
        """
        midVertex: Vertex = Vertex(nodeName)
        self._vertexDict[nodeName] = midVertex

        self.__insertNode(u, v, midVertex)
        self.__insertNode(v, u, midVertex)

        for v1, v2 in ((u, midVertex.id), (midVertex.id, v)):
            self._halfEdgeDict[v1, v2].twin = self._halfEdgeDict[v2, v1]
            self._halfEdgeDict[v2, v1].twin = self._halfEdgeDict[v1, v2]

    def __insertNode(self, sourceNode: NodeId, targetNode: NodeId, midVertex: Vertex):
        """
        Split a directed half-edge (sourceNode, targetNode) by inserting midVertex.

        Args:
            sourceNode: The origin identifier of the existing half-edge.
            targetNode: The destination identifier of the existing half-edge.
            midVertex: The new intermediate Vertex being inserted.
        """
        he: HalfEdge = self._halfEdgeDict.pop((sourceNode, targetNode))
        he1: HalfEdge = HalfEdge(HalfEdgeId((sourceNode, midVertex.id)))
        he2: HalfEdge = HalfEdge(HalfEdgeId((midVertex.id, targetNode)))

        # update halfEdgeDict
        self._halfEdgeDict[sourceNode, midVertex.id] = he1
        self._halfEdgeDict[midVertex.id, targetNode] = he2
        he1.setAll(None, he.origin, he.previous, he2, he.incidentFace)
        he2.setAll(None, midVertex, he1, he.next, he.incidentFace)
        he1.previous.next = he1
        he2.next.previous = he2

        # update face
        if he.incidentFace.incidentEdge is he:
            he.incidentFace.incidentEdge = he1
        he.incidentFace.updateNodes()   # not efficient
