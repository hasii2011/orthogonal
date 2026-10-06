
from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from tests.ProjectTestBase import ProjectTestBase

from orthogonal.topologyShapeMetric.FlowNet import FlowNet


class TestFlowNet(ProjectTestBase):
    """
    Unit tests for FlowNet minimum-cost circulation network.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def testInitialization(self):
        """
        Verify that FlowNet initializes with default cost 0 and empty nodes and edges.
        """
        flowNet: FlowNet = FlowNet()

        self.assertEqual(0, flowNet.cost, 'Default cost should be 0')
        self.assertEqual(0, len(flowNet.nodes), 'Newly initialized flow network should have no nodes')
        self.assertEqual(0, len(flowNet.edges), 'Newly initialized flow network should have no edges')

    def testCostPropertyIsReadOnly(self):
        """
        Verify that the cost property cannot be mutated and raises AttributeError.
        """
        flowNet: FlowNet = FlowNet()

        with self.assertRaises(AttributeError):
            # noinspection PyPropertyAccess
            flowNet.cost = 10

    def testVertexNodeDemand(self):
        """
        Verify that addVertexNode configures supply demand of -4 (2pi).
        """
        flowNet: FlowNet = FlowNet()
        vertexId: str = 'v1'

        flowNet.addVertexNode(vertexId)

        self.assertIn(vertexId, flowNet.nodes, 'Vertex should be added to nodes')
        self.assertEqual(-4, flowNet.nodes[vertexId]['demand'], 'Vertex demand must be -4')

    def testFaceNodeDemand(self):
        """
        Verify that addFaceNode correctly calculates demand for internal and external faces.
        """
        flowNet: FlowNet = FlowNet()
        internalFaceId: str = 'f_int'
        externalFaceId: str = 'f_ext'
        degree: int = 4

        flowNet.addFaceNode(internalFaceId, degree=degree, isExternal=False)
        flowNet.addFaceNode(externalFaceId, degree=degree, isExternal=True)

        expectedInternalDemand: int = 2 * degree - 4
        expectedExternalDemand: int = 2 * degree + 4

        self.assertEqual(expectedInternalDemand, flowNet.nodes[internalFaceId]['demand'], 'Internal face demand must be 2*degree - 4')
        self.assertEqual(expectedExternalDemand, flowNet.nodes[externalFaceId]['demand'], 'External face demand must be 2*degree + 4')

    def testEdgeAttributes(self):
        """
        Verify lowerbound, capacity, and weight bounds for angle and bend edges.
        """
        flowNet: FlowNet = FlowNet()
        vertexId: str = 'v1'
        faceId1: str = 'f1'
        faceId2: str = 'f2'
        edgeKey1: str = 'e1'
        edgeKey2: str = 'e2'

        flowNet.addVertexToFaceEdge(vertexId, faceId1, edgeKey1)
        flowNet.addFaceToFaceEdge(faceId1, faceId2, edgeKey2)

        angleEdge: dict = flowNet[vertexId][faceId1][edgeKey1]
        self.assertEqual(1, angleEdge['lowerbound'], 'Angle edge must have lowerbound of 1')
        self.assertEqual(4, angleEdge['capacity'], 'Angle edge must have capacity of 4')
        self.assertEqual(0, angleEdge['weight'], 'Angle edge must have weight of 0')

        bendEdge: dict = flowNet[faceId1][faceId2][edgeKey2]
        self.assertEqual(0, bendEdge['lowerbound'], 'Bend edge must have lowerbound of 0')
        self.assertEqual(2**32, bendEdge['capacity'], 'Bend edge must have large capacity')
        self.assertEqual(1, bendEdge['weight'], 'Bend edge must have weight of 1')

    def testCostOfFlow(self):
        """
        Verify that costOfFlow calculates total circulation cost from edge weights.
        """
        flowNet: FlowNet = FlowNet()
        flowNet.addFaceToFaceEdge('f1', 'f2', 'e1')
        flowNet.addFaceToFaceEdge('f2', 'f3', 'e2')

        mockFlowDict: dict = {
            'f1': {'f2': {'e1': 3}},
            'f2': {'f3': {'e2': 2}}
        }
        calculatedCost: int = flowNet.costOfFlow(mockFlowDict)
        self.assertEqual(5, calculatedCost, 'Total cost should equal sum of flow times weight (3*1 + 2*1)')

    def testCanonicalSquareMinCostFlow(self):
        """
        Verify minimum-cost circulation for a canonical 4-cycle square graph requires zero bends.
        """
        flowNet: FlowNet = FlowNet()
        vertices: list[str] = ['v0', 'v1', 'v2', 'v3']

        for vertexId in vertices:
            flowNet.addVertexNode(vertexId)

        flowNet.addFaceNode('f0', degree=4, isExternal=False)
        flowNet.addFaceNode('f_ext', degree=4, isExternal=True)

        for vertexId in vertices:
            flowNet.addVertexToFaceEdge(vertexId, 'f0', f'{vertexId}->f0')
            flowNet.addVertexToFaceEdge(vertexId, 'f_ext', f'{vertexId}->f_ext')

        for idx, vertexId in enumerate(vertices):
            nextVertexId: str = vertices[(idx + 1) % 4]
            flowNet.addFaceToFaceEdge('f0', 'f_ext', f'({vertexId},{nextVertexId})')
            flowNet.addFaceToFaceEdge('f_ext', 'f0', f'({nextVertexId},{vertexId})')

        flowDict: dict = flowNet.minCostFlow()

        self.assertIsNotNone(flowDict, 'minCostFlow should return a flow dictionary')
        self.assertEqual(0, flowNet.cost, 'A 4-cycle square must embed with 0 bends')


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(TestFlowNet))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
