
from logging import Logger
from logging import getLogger
import logging.config

import json

from os import sep as osSep

import networkx as nx
import matplotlib.pyplot as plt

import unittest

from pkg_resources import resource_filename

from orthogonal.topologyShapeMetric.Compaction import Compaction
from orthogonal.topologyShapeMetric.Orthogonalization import Orthogonalization
from orthogonal.topologyShapeMetric.Planarization import Planarization


class TestGML(unittest.TestCase):

    RESOURCES_PACKAGE_NAME: str = 'tests.testdata'
    RESOURCES_PATH:         str = f'tests{osSep}testdata'

    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'
    JSON_LOGGING_CONFIG_FILENAME = "testLoggingConfig.json"

    clsLogger: Logger = None

    @classmethod
    def setUpLogging(cls):
        """"""
        fqFileName: str = TestGML.retrieveResourcePath(TestGML.JSON_LOGGING_CONFIG_FILENAME)
        with open(fqFileName, 'r') as loggingConfigurationFile:
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

    def testCase1(self):
        fqFileName: str = TestGML.retrieveResourcePath("case1.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        compact: Compaction = self.generate(G, {node: eval(node) for node in G})

        compact.draw()
        plt.savefig("case1.png")

    def testCase1BiConnected(self):
        fqFileName: str = TestGML.retrieveResourcePath("case1_biconnected.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        compact: Compaction = self.generate(G, {node: eval(node) for node in G})

        compact.draw()
        plt.savefig("case1_biconnected.png")

    def testCase2(self):
        fqFileName: str = TestGML.retrieveResourcePath("case2.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        compact: Compaction = self.generate(G, {node: eval(node) for node in G})

        compact.draw()
        plt.savefig("case2.png")

        for flowKey in compact.flow_dict.keys():
            self.logger.info(f'flowKey: {flowKey} - value: {compact.flow_dict[flowKey]}')

    def testCase2BiConnected(self):
        fqFileName: str = TestGML.retrieveResourcePath("case2_biconnected.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        compact: Compaction = self.generate(G, {node: eval(node) for node in G})
        compact.draw()
        plt.savefig("case2_biconnected.png")

    def testSimple(self):

        fqFileName: str = TestGML.retrieveResourcePath("simple.gml")
        G = nx.Graph(nx.read_gml(fqFileName))
        compact: Compaction = self.generate(G, {node: eval(node) for node in G})

        for flowKey in compact.flow_dict.keys():
            valueDict = compact.flow_dict[flowKey]
            self.logger.info(f'flowKey: {flowKey} - valueDict: {valueDict}')
            for valueKey in valueDict.keys():
                self.logger.info(f'\t\t{valueKey} value: {valueDict[valueKey]}')

        compact.draw(with_labels=True)
        plt.savefig("simple.png")

    def generate(self, G, pos=None) -> Compaction:

        planar:     Planarization     = Planarization(G, pos)
        orthogonal: Orthogonalization = Orthogonalization(planar)
        compact:    Compaction        = Compaction(orthogonal)

        return compact

    @classmethod
    def retrieveResourcePath(cls, bareFileName: str) -> str:

        # Use this method in Python 3.9
        # from importlib_resources import files
        # configFilePath: str  = files('org.pyut.resources').joinpath(Pyut.JSON_LOGGING_CONFIG_FILENAME)

        try:
            fqFileName: str = resource_filename(TestGML.RESOURCES_PACKAGE_NAME, bareFileName)
        except (ValueError, Exception):
            #
            # Maybe we are in an app
            #
            from os import environ
            pathToResources: str = environ.get(f'{TestGML.RESOURCE_ENV_VAR}')
            fqFileName:      str = f'{pathToResources}/{TestGML.RESOURCES_PATH}/{bareFileName}'

        return fqFileName


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
