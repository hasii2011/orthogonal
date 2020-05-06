import networkx as nx
from orthogonal.topologyShapeMetric import TSM
import unittest


def generate(G, pos=None):
    planar = TSM.Planarization(G, pos)
    orthogonal = TSM.Orthogonalization(planar)
    compact = TSM.Compaction(orthogonal)


class TestGML(unittest.TestCase):
    def test_01(self):
        G = nx.Graph(nx.read_gml("testdata/case1.gml"))
        generate(G, {node: eval(node) for node in G})

    def test_02(self):
        G = nx.Graph(nx.read_gml("testdata/case1BiConnected.gml"))
        generate(G, {node: eval(node) for node in G})

    def test_03(self):
        G = nx.Graph(nx.read_gml("testdata/case2.gml"))
        generate(G, {node: eval(node) for node in G})

    def test_04(self):
        G = nx.Graph(nx.read_gml("testdata/case2BiConnected.gml"))
        generate(G, {node: eval(node) for node in G})


class TestGrid(unittest.TestCase):

    def _test_grid(self, i, j):
        G = nx.grid_2d_graph(i, j)
        generate(G, pos={node: node for node in G})
        generate(G)

    def test_01(self):
        self._test_grid(1, 2)

    def test_02(self):
        self._test_grid(2, 1)

    def test_03(self):
        self._test_grid(1, 5)

    def test_04(self):
        self._test_grid(5, 1)

    def test_05(self):
        self._test_grid(5, 5)

    def test_06(self):
        self._test_grid(3, 3)

    def test_07(self):
        self._test_grid(9, 9)


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
