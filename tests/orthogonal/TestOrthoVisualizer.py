"""
Unit tests for OrthoVisualizer data structures, datasets, and integration with Orthogonalization and FlowNet.
"""

from typing import List
from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from wx import App
from wx.lib.ogl import OGLInitialize

from tests.ProjectTestBase import ProjectTestBase

from orthogonal.topologyShapeMetric.Orthogonalization import Orthogonalization
from orthogonal.topologyShapeMetric.Planarization import Planarization
from tests.demo.orthovisualizer.OrthoDataSet import OrthoDataSet
from tests.demo.orthovisualizer.OrthoDataSet import createDefaultDataSets
from tests.demo.orthovisualizer.OrthoTypes import AngleEntry
from tests.demo.orthovisualizer.OrthoTypes import FaceBalanceEntry
from tests.demo.orthovisualizer.OrthoTypes import FlowArcEntry
from tests.demo.orthovisualizer.OrthoVisualizerFrame import OrthoVisualizerFrame


class TestOrthoVisualizer(ProjectTestBase):
    """
    Unit tests verifying data models and visualizer preset integrity for OrthoVisualizer.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def testDefaultDataSetsAreNonEmpty(self):
        """
        Verify that createDefaultDataSets returns at least three standard planar graph presets.
        """
        dataSets: List[OrthoDataSet] = createDefaultDataSets()
        self.assertGreaterEqual(len(dataSets), 3, 'Expected at least 3 default datasets')

    def testDefaultDataSetsSolveOrthogonalization(self):
        """
        Verify that each default dataset planarizes and solves minimum-cost orthogonalization circulation.
        """
        dataSets: List[OrthoDataSet] = createDefaultDataSets()

        for dataSet in dataSets:
            planar: Planarization = Planarization(dataSet.graph.copy())
            orthogonal: Orthogonalization = Orthogonalization(planar)

            self.assertIsNotNone(orthogonal.flowNetwork, f'FlowNet must be created for {dataSet.name}')
            self.assertIsNotNone(orthogonal.flowDict, f'FlowDict must be solved for {dataSet.name}')
            self.assertGreaterEqual(orthogonal.flowNetwork.cost, 0, f'Circulation cost must be non-negative for {dataSet.name}')
            self.assertEqual(len(planar.dcel.faceDict), len(orthogonal.planar.dcel.faceDict))

    def testAngleEntryType(self):
        """
        Verify AngleEntry instantiation and typed field values.
        """
        entry: AngleEntry = AngleEntry(
            vertexId='v1',
            faceId=1,
            halfEdgeId=('v1', 'v2'),
            flowUnits=1,
            angleDegrees=90,
        )
        self.assertEqual('v1', entry.vertexId)
        self.assertEqual(1, entry.faceId)
        self.assertEqual(('v1', 'v2'), entry.halfEdgeId)
        self.assertEqual(1, entry.flowUnits)
        self.assertEqual(90, entry.angleDegrees)

    def testFaceBalanceEntryType(self):
        """
        Verify FaceBalanceEntry instantiation and typed field values.
        """
        entry: FaceBalanceEntry = FaceBalanceEntry(
            faceId=0,
            isExternal=False,
            degree=3,
            demand=2,
            vertexInflow=2,
            targetAngleSum=180,
            isBalanced=True,
        )
        self.assertEqual(0, entry.faceId)
        self.assertFalse(entry.isExternal)
        self.assertEqual(3, entry.degree)
        self.assertEqual(2, entry.demand)
        self.assertEqual(2, entry.vertexInflow)
        self.assertEqual(180, entry.targetAngleSum)
        self.assertTrue(entry.isBalanced)

    def testFlowArcEntryType(self):
        """
        Verify FlowArcEntry instantiation and typed field values.
        """
        entry: FlowArcEntry = FlowArcEntry(
            source='v1',
            target=0,
            arcType='Vertex->Face',
            key=('v1', 'v2'),
            lowerbound=1,
            capacity=4,
            weight=0,
            flow=1,
        )
        self.assertEqual('v1', entry.source)
        self.assertEqual(0, entry.target)
        self.assertEqual('Vertex->Face', entry.arcType)
        self.assertEqual(1, entry.flow)

    def testFrameInstantiationAndDataSetLoading(self):
        """
        Verify that OrthoVisualizerFrame initializes and switches presets cleanly.
        """
        wxApp: App = App(False)
        OGLInitialize()
        frame: OrthoVisualizerFrame = OrthoVisualizerFrame()
        self.assertIsNotNone(frame)
        self.assertIsNotNone(frame._orthogonal)
        self.assertEqual(0, frame._currentDataSetIndex)

        # Switch to Diamond (index 1)
        frame._loadDataSet(1)
        self.assertEqual(1, frame._currentDataSetIndex)
        self.assertIsNotNone(frame._orthogonal)
        assert frame._orthogonal is not None
        self.assertEqual(4, frame._orthogonal.planar.G.number_of_nodes())

        frame.Destroy()
        wxApp.Destroy()


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestOrthoVisualizer))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
