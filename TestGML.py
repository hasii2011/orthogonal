
from logging import Logger
from logging import getLogger
import logging.config

import json

import networkx as nx
from orthogonal.topologyShapeMetric import TSM
import matplotlib.pyplot as plt

import unittest

JSON_LOGGING_CONFIG_FILENAME = "testLoggingConfig.json"


class TestGML(unittest.TestCase):

    clsLogger: Logger = None

    @classmethod
    def setUpLogging(cls):
        """"""
        with open(JSON_LOGGING_CONFIG_FILENAME, 'r') as loggingConfigurationFile:
            configurationDictionary = json.load(loggingConfigurationFile)

        logging.config.dictConfig(configurationDictionary)
        logging.logProcesses = False
        logging.logThreads = False

    @classmethod
    def setUpClass(cls):
        TestGML.setUpLogging()
        TestGML.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestGML.clsLogger

    def test_01(self):
        G = nx.Graph(nx.read_gml("test_data/case1.gml"))
        compact: TSM.Compaction = self.generate(G, {node: eval(node) for node in G})

        compact.draw()
        plt.savefig("case1.png")

    def test_02(self):
        G = nx.Graph(nx.read_gml("test_data/case1_biconnected.gml"))
        compact: TSM.Compaction = self.generate(G, {node: eval(node) for node in G})

        compact.draw()
        plt.savefig("case1_biconnected.png")

    def test_03(self):
        G = nx.Graph(nx.read_gml("test_data/case2.gml"))
        compact: TSM.Compaction = self.generate(G, {node: eval(node) for node in G})

        compact.draw()
        plt.savefig("case2.png")

        for flowKey in compact.flow_dict.keys():
            self.logger.info(f'flowKey: {flowKey} - value: {compact.flow_dict[flowKey]}')

    def test_04(self):
        G = nx.Graph(nx.read_gml("test_data/case2_biconnected.gml"))
        compact: TSM.Compaction = self.generate(G, {node: eval(node) for node in G})
        compact.draw()
        plt.savefig("case2_biconnected.png")

    def testSimple(self):

        G = nx.Graph(nx.read_gml("test_data/simple.gml"))
        compact: TSM.Compaction = self.generate(G, {node: eval(node) for node in G})

        for flowKey in compact.flow_dict.keys():
            valueDict = compact.flow_dict[flowKey]
            self.logger.info(f'flowKey: {flowKey} - valueDict: {valueDict}')
            for valueKey in valueDict.keys():
                self.logger.info(f'\t\t{valueKey} value: {valueDict[valueKey]}')

        compact.draw(with_labels=True)
        plt.savefig("simple.png")

    def generate(self, G, pos=None) -> TSM.Compaction:
        planar = TSM.Planarization(G, pos)
        orthogonal = TSM.Orthogonalization(planar)
        compact: TSM.Compaction = TSM.Compaction(orthogonal)

        return compact


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
