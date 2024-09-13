
from orthogonal.doublyConnectedEdgeList.GraphElement import GraphElement


class Hedge(GraphElement):

    def __init__(self, name):
        super().__init__(name)
        self.inc = None # the incident face'
        self.twin = None
        self.ori  = None
        self.pred = None
        self.succ = None

    def get_points(self):
        return self.ori.id, self.twin.ori.id

    def set_all(self, twin, ori, pred, succ, inc):
        self.twin = twin
        self.ori = ori
        self.pred = pred
        self.succ = succ
        self.inc = inc
