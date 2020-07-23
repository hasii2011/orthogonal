
from typing import Dict
from typing import Tuple

from logging import Logger
from logging import getLogger
from logging import DEBUG

from unittest import TestSuite
from unittest import main as unitTestMain

import networkx as nx
import matplotlib.pyplot as plt

from orthogonal.topologyShapeMetric.Compaction import Compaction
from orthogonal.topologyShapeMetric.Orthogonalization import Orthogonalization
from orthogonal.topologyShapeMetric.Planarization import Planarization

from tests.TestBase import TestBase


class TestGML(TestBase):

    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestGML.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestGML.clsLogger

    def testCase1(self):
        fqFileName: str = TestGML.retrieveResourcePath("case1.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        compact: Compaction = self.generate(G, {node: eval(node) for node in G})

        compact.draw()
        plt.savefig("case1.png")

    def testCase1BiConnected(self):
        fqFileName: str = TestGML.retrieveResourcePath("case1BiConnected.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        compact: Compaction = self.generate(G, {node: eval(node) for node in G})

        compact.draw()
        plt.savefig("case1BiConnected.png")

    def testCase2(self):
        fqFileName: str = TestGML.retrieveResourcePath("case2.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        compact: Compaction = self.generate(G, {node: eval(node) for node in G})

        compact.draw()
        plt.savefig("case2.png")

        if self.logger.level == DEBUG:
            for flowKey in compact.flow_dict.keys():
                self.logger.debug(f'{flowKey=} - {compact.flow_dict[flowKey]=}')

    def testCase2BiConnected(self):
        fqFileName: str = TestGML.retrieveResourcePath("case2BiConnected.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        compact: Compaction = self.generate(G, {node: eval(node) for node in G})
        compact.draw()
        plt.savefig("case2BiConnected.png")

    def testSimple(self):

        fqFileName: str = TestGML.retrieveResourcePath("simple.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        if self.logger.level == DEBUG:
            for node in G:
                self.logger.debug(f'{node=}')

        compact: Compaction = self.generate(G, {node: eval(node) for node in G})

        for flowKey in compact.flow_dict.keys():
            valueDict = compact.flow_dict[flowKey]
            self.logger.debug(f'{flowKey=} - {valueDict}=')
            if self.logger.level == DEBUG:
                for valueKey in valueDict.keys():
                    self.logger.info(f'\t\t{valueKey=} {valueDict[valueKey]=}')

        compact.draw(with_labels=True)
        plt.savefig("simple.png")

    def testTranslationGraphSimple(self):
        fqFileName: str = TestGML.retrieveResourcePath("translationGraphSimple.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        self.logger.debug(f'{G.nodes=}')
        positionDictionary: Dict[str, Tuple] = {}
        for node in G:
            self.logger.debug(f'{node=}')
            x: int = G.nodes[node]['graphics']['x']
            y: int = G.nodes[node]['graphics']['y']
            positionDictionary[node] = (x, y)

        plt.xkcd()
        compact: Compaction = self.generate(G, positionDictionary)

        compact.draw(with_labels=True)
        plt.savefig("translationGraphSimple.png")

    def testTranslationGraphComplex(self):
        fqFileName: str = TestGML.retrieveResourcePath("translationGraphComplex.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        positionDictionary: Dict[str, Tuple] = {}
        for node in G:
            self.logger.debug(f'{node=}')
            x: int = G.nodes[node]['graphics']['x']
            y: int = G.nodes[node]['graphics']['y']
            positionDictionary[node] = (x, y)

        plt.xkcd()
        compact: Compaction = self.generate(G, positionDictionary)
        compact.draw(with_labels=True)

        plt.savefig("translationGraphComplex.png")

    def testTranslationGraphMedium(self):
        fqFileName: str = TestGML.retrieveResourcePath("translationGraphMedium.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        positionDictionary: Dict[str, Tuple] = {}
        for node in G:
            self.logger.debug(f'{node=}')
            x: int = G.nodes[node]['graphics']['x']
            y: int = G.nodes[node]['graphics']['y']
            positionDictionary[node] = (x, y)

        plt.xkcd()
        compact: Compaction = self.generate(G, positionDictionary)
        compact.draw(with_labels=True)
        plt.savefig("translationGraphMedium.png")

    def generate(self, G, pos=None) -> Compaction:

        planar:     Planarization     = Planarization(G, pos)
        orthogonal: Orthogonalization = Orthogonalization(planar)
        compact:    Compaction        = Compaction(orthogonal)

        return compact


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestGML))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
