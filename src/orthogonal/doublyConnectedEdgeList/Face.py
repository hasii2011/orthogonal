
from orthogonal.doublyConnectedEdgeList.GraphElement import GraphElement


class Face(GraphElement):
    def __init__(self, name):
        super().__init__(name)
        self.inc = None  # the first half-edge incident to the face from left
        self.nodes_id = []

    def __len__(self):
        return len(self.nodes_id)

    def __repr__(self):
        return f'FaceView{repr(self.nodes_id)}'

    def update_nodes(self):
        self.nodes_id = [vertex.id for vertex in self.surround_vertices()]

    def surround_faces(self):  # clockwise, duplicated!!
        for he in self.surround_half_edges():
            yield he.twin.inc

    def surround_half_edges(self):  # clockwise
        yield self.inc
        he = self.inc.succ
        while he is not self.inc:
            yield he
            he = he.succ

    def surround_vertices(self):
        for he in self.surround_half_edges():
            yield he.ori
