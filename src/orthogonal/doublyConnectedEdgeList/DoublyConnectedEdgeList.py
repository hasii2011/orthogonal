

import networkx as nx

from orthogonal.doublyConnectedEdgeList.Face import Face
from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdge
from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdgeId
from orthogonal.doublyConnectedEdgeList.Vertex import Vertex


class DoublyConnectedEdgeList:
    def __init__(self, G, embedding):
        assert nx.check_planarity(G)[0]

        self.vertex_dict = {}
        for node in G.nodes:
            self.vertex_dict[node] = Vertex(node)

        self.half_edge_dict = {}
        for u, v in G.edges:
            he1, he2 = HalfEdge(HalfEdgeId((u, v))), HalfEdge(HalfEdgeId((v, u)))
            self.half_edge_dict[he1.id] = he1
            self.half_edge_dict[he2.id] = he2
            he1.twin = he2
            he1.origin = self.vertex_dict[u]
            self.vertex_dict[u].inc = he1

            he2.twin = he1
            he2.origin = self.vertex_dict[v]
            self.vertex_dict[v].inc = he2

        for he in self.half_edge_dict.values():
            u, v = he.getPoints()
            he.next = self.half_edge_dict[embedding.next_face_half_edge(u, v)]
            he.next.previous = he

        self.face_dict = {}
        for he in self.half_edge_dict.values():
            if not he.incidentFace:
                face_id = f'f{len(self.face_dict)}'
                face: Face = Face(face_id)
                face.incidentEdge = he
                self.face_dict[face_id] = face

                face.nodes_id = embedding.traverse_face(*he.getPoints())
                for v1_id, v2_id in zip(face.nodes_id, face.nodes_id[1:]+face.nodes_id[:1]):
                    other = self.half_edge_dict[v1_id, v2_id]
                    assert not other.incidentFace
                    other.incidentFace = face

        if not self.face_dict:
            self.face_dict['f0'] = Face('f0')

    def add_node_between(self, u: 'id', v: 'id', node_name):
        def insert_node(u, v, midVertice):

            he = self.half_edge_dict.pop((u, v))
            he1 = HalfEdge(HalfEdgeId((u, midVertice.id)))
            he2 = HalfEdge(HalfEdgeId((midVertice.id, v)))
            # update half_edge_dict
            self.half_edge_dict[u, midVertice.id] = he1
            self.half_edge_dict[midVertice.id, v] = he2
            he1.setAll(None, he.origin, he.previous, he2, he.incidentFace)
            he2.setAll(None, midVertice, he1, he.next, he.incidentFace)
            he1.previous.next = he1
            he2.next.previous = he2
            # update face
            if he.incidentFace.incidentEdge is he:
                he.incidentFace.incidentEdge = he1
            he.incidentFace.update_nodes() # not efficient

        # update vertex_dict
        mid_vertice = Vertex(node_name)
        self.vertex_dict[node_name] = mid_vertice
        # insert
        insert_node(u, v, mid_vertice)
        insert_node(v, u, mid_vertice)
        for v1, v2 in ((u, mid_vertice.id), (mid_vertice.id, v)):
            self.half_edge_dict[v1, v2].twin = self.half_edge_dict[v2, v1]
            self.half_edge_dict[v2, v1].twin = self.half_edge_dict[v1, v2]
