
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from networkx import Graph
from networkx import PlanarEmbedding
from networkx import check_planarity
from networkx import complete_graph

from tests.ProjectTestBase import ProjectTestBase

from orthogonal.TopologyTypes import FaceId
from orthogonal.TopologyTypes import HalfEdgeId
from orthogonal.TopologyTypes import NodeId
from orthogonal.doublyConnectedEdgeList.DoublyConnectedEdgeList import DoublyConnectedEdgeList
from orthogonal.doublyConnectedEdgeList.Face import Face
from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdge
from orthogonal.doublyConnectedEdgeList.Vertex import Vertex


class TestDoublyConnectedEdgeList(ProjectTestBase):
    """
    Unit tests for DoublyConnectedEdgeList (DCEL).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def testEmptyGraph(self):
        """
        Verify that an empty graph initializes an empty DCEL with a default face.
        """
        emptyGraph: Graph = Graph()
        isPlanar:   bool
        embedding:  PlanarEmbedding
        isPlanar, embedding = check_planarity(emptyGraph)
        self.assertTrue(isPlanar, 'Empty graph should be planar')

        dcel: DoublyConnectedEdgeList = DoublyConnectedEdgeList(emptyGraph, embedding)

        self.assertEqual(0, len(dcel.vertexDict), 'Vertex dictionary should be empty')
        self.assertEqual(0, len(dcel.halfEdgeDict), 'Half-edge dictionary should be empty')
        self.assertEqual(1, len(dcel.faceDict), 'Face dictionary should contain default face f0')
        self.assertIn('f0', dcel.faceDict, 'Default face f0 should be present')

    def testInitializationTriangle(self):
        """
        Verify DCEL initialization for a planar 3-cycle graph.
        """
        triangleGraph: Graph = Graph()
        triangleGraph.add_edges_from([('v1', 'v2'), ('v2', 'v3'), ('v3', 'v1')])

        isPlanar: bool
        embedding: PlanarEmbedding
        isPlanar, embedding = check_planarity(triangleGraph)
        self.assertTrue(isPlanar, 'Triangle graph should be planar')

        dcel: DoublyConnectedEdgeList = DoublyConnectedEdgeList(triangleGraph, embedding)

        self.assertEqual(3, len(dcel.vertexDict), 'Should contain 3 vertices')
        nodeName: str
        for nodeName in ('v1', 'v2', 'v3'):
            self.assertIn(nodeName, dcel.vertexDict, f'Vertex {nodeName} should exist')
            vertexInstance: Vertex = dcel.vertexDict[nodeName]
            self.assertEqual(nodeName, vertexInstance.id, 'Vertex ID should match node name')
            self.assertIsNotNone(vertexInstance.incidentEdge, 'Vertex should have an incident edge')
            self.assertEqual(nodeName, vertexInstance.incidentEdge.origin.id, 'Incident edge origin should match vertex')

        self.assertEqual(6, len(dcel.halfEdgeDict), 'Should contain 6 directed half-edges')
        edgeTuple: Tuple[str, str]
        for edgeTuple in (
            ('v1', 'v2'), ('v2', 'v1'),
            ('v2', 'v3'), ('v3', 'v2'),
            ('v3', 'v1'), ('v1', 'v3'),
        ):
            originId: str = edgeTuple[0]
            destId: str = edgeTuple[1]
            halfEdgeKey: HalfEdgeId = HalfEdgeId((originId, destId))
            self.assertIn(halfEdgeKey, dcel.halfEdgeDict, f'HalfEdge {halfEdgeKey} should exist')
            halfEdge: HalfEdge = dcel.halfEdgeDict[halfEdgeKey]
            twinKey: HalfEdgeId = HalfEdgeId((destId, originId))
            self.assertEqual(twinKey, halfEdge.twin.id, 'Twin edge ID should be reverse of half edge')
            self.assertIs(dcel.halfEdgeDict[twinKey], halfEdge.twin, 'Twin should reference the twin HalfEdge instance')
            self.assertIs(halfEdge, halfEdge.twin.twin, 'Twin of twin should be self')
            self.assertEqual(originId, halfEdge.origin.id, 'Origin ID should match')
            self.assertTrue(halfEdge.hasIncidentFace, 'Half-edge should have an incident face')
            self.assertIsNotNone(halfEdge.next, 'Half-edge should have a next edge')
            self.assertIsNotNone(halfEdge.previous, 'Half-edge should have a previous edge')
            self.assertIs(halfEdge, halfEdge.next.previous, 'Next edge previous should be self')
            self.assertIs(halfEdge, halfEdge.previous.next, 'Previous edge next should be self')

        self.assertEqual(2, len(dcel.faceDict), 'A 3-cycle planar graph should have 2 faces')
        faceId: FaceId
        faceInstance: Face
        for faceId, faceInstance in dcel.faceDict.items():
            self.assertEqual(faceId, faceInstance.id, 'Face ID should match key')
            self.assertTrue(faceInstance.hasIncidentEdge, 'Face should have an incident edge')
            self.assertEqual(3, len(faceInstance), 'Each face of a triangle should have 3 boundary vertices')
            surroundingEdges: List[HalfEdge] = list(faceInstance.surroundHalfEdges())
            self.assertEqual(3, len(surroundingEdges), 'Face should be bounded by 3 half-edges')
            edgeInFace: HalfEdge
            for edgeInFace in surroundingEdges:
                self.assertIs(faceInstance, edgeInFace.incidentFace, 'Boundary half-edge incidentFace should match')

    def testAddNodeBetween(self):
        """
        Verify inserting a node between two existing connected vertices splits edges and updates DCEL.
        """
        triangleGraph: Graph = Graph()
        triangleGraph.add_edges_from([('v1', 'v2'), ('v2', 'v3'), ('v3', 'v1')])

        isPlanar: bool
        embedding: PlanarEmbedding
        isPlanar, embedding = check_planarity(triangleGraph)
        self.assertTrue(isPlanar, 'Triangle graph should be planar')

        dcel: DoublyConnectedEdgeList = DoublyConnectedEdgeList(triangleGraph, embedding)

        oldEdgeKey: HalfEdgeId = HalfEdgeId(('v1', 'v2'))
        oldTwinKey: HalfEdgeId = HalfEdgeId(('v2', 'v1'))
        oldEdgeFace: Face = dcel.halfEdgeDict[oldEdgeKey].incidentFace
        oldTwinFace: Face = dcel.halfEdgeDict[oldTwinKey].incidentFace

        dcel.addNodeBetween('v1', 'v2', 'vIntermediate')

        self.assertEqual(4, len(dcel.vertexDict), 'Vertex count should increase to 4')
        self.assertIn('vIntermediate', dcel.vertexDict, 'New vertex should be present in vertexDict')
        self.assertEqual('vIntermediate', dcel.vertexDict['vIntermediate'].id, 'New vertex ID should match')

        self.assertNotIn(oldEdgeKey, dcel.halfEdgeDict, 'Old directed edge should be removed')
        self.assertNotIn(oldTwinKey, dcel.halfEdgeDict, 'Old twin directed edge should be removed')

        newEdgeKey1: HalfEdgeId = HalfEdgeId(('v1', 'vIntermediate'))
        newEdgeKey2: HalfEdgeId = HalfEdgeId(('vIntermediate', 'v2'))
        newTwinKey1: HalfEdgeId = HalfEdgeId(('v2', 'vIntermediate'))
        newTwinKey2: HalfEdgeId = HalfEdgeId(('vIntermediate', 'v1'))

        self.assertIn(newEdgeKey1, dcel.halfEdgeDict, 'Edge (v1, vIntermediate) should exist')
        self.assertIn(newEdgeKey2, dcel.halfEdgeDict, 'Edge (vIntermediate, v2) should exist')
        self.assertIn(newTwinKey1, dcel.halfEdgeDict, 'Edge (v2, vIntermediate) should exist')
        self.assertIn(newTwinKey2, dcel.halfEdgeDict, 'Edge (vIntermediate, v1) should exist')

        self.assertEqual(8, len(dcel.halfEdgeDict), 'Half-edge count should increase from 6 to 8')

        edge1: HalfEdge = dcel.halfEdgeDict[newEdgeKey1]
        edge2: HalfEdge = dcel.halfEdgeDict[newEdgeKey2]
        twin1: HalfEdge = dcel.halfEdgeDict[newTwinKey1]
        twin2: HalfEdge = dcel.halfEdgeDict[newTwinKey2]

        self.assertIs(twin2, edge1.twin, 'Twin of (v1, vIntermediate) should be (vIntermediate, v1)')
        self.assertIs(edge1, twin2.twin, 'Twin of (vIntermediate, v1) should be (v1, vIntermediate)')
        self.assertIs(twin1, edge2.twin, 'Twin of (vIntermediate, v2) should be (v2, vIntermediate)')
        self.assertIs(edge2, twin1.twin, 'Twin of (v2, vIntermediate) should be (vIntermediate, v2)')

        self.assertIs(edge2, edge1.next, 'Next edge of (v1, vIntermediate) should be (vIntermediate, v2)')
        self.assertIs(edge1, edge2.previous, 'Previous edge of (vIntermediate, v2) should be (v1, vIntermediate)')
        self.assertIs(twin2, twin1.next, 'Next edge of (v2, vIntermediate) should be (vIntermediate, v1)')
        self.assertIs(twin1, twin2.previous, 'Previous edge of (vIntermediate, v1) should be (v2, vIntermediate)')

        self.assertIs(oldEdgeFace, edge1.incidentFace, 'Incident face of edge1 should match original face')
        self.assertIs(oldEdgeFace, edge2.incidentFace, 'Incident face of edge2 should match original face')
        self.assertIs(oldTwinFace, twin1.incidentFace, 'Incident face of twin1 should match original twin face')
        self.assertIs(oldTwinFace, twin2.incidentFace, 'Incident face of twin2 should match original twin face')

        self.assertIn('vIntermediate', oldEdgeFace.nodes_id, 'Intermediate node should be in face boundary nodes')
        self.assertIn('vIntermediate', oldTwinFace.nodes_id, 'Intermediate node should be in twin face boundary nodes')

    def testNonPlanarGraphRaisesAssertionError(self):
        """
        Verify that attempting to construct a DCEL from a non-planar graph raises AssertionError.
        """
        k5Graph: Graph = complete_graph(5)
        dummyEmbedding: PlanarEmbedding = PlanarEmbedding()

        with self.assertRaises(AssertionError):
            DoublyConnectedEdgeList(k5Graph, dummyEmbedding)

    def testPropertiesAccess(self):
        """
        Verify vertexDict, halfEdgeDict, and faceDict properties expose internal mappings.
        """
        cycleGraph: Graph = Graph()
        cycleGraph.add_edges_from([('n1', 'n2'), ('n2', 'n3'), ('n3', 'n1')])

        isPlanar: bool
        embedding: PlanarEmbedding
        isPlanar, embedding = check_planarity(cycleGraph)
        self.assertTrue(isPlanar, 'Cycle graph should be planar')

        dcel: DoublyConnectedEdgeList = DoublyConnectedEdgeList(cycleGraph, embedding)

        vertexMapping: Dict[NodeId, Vertex] = dcel.vertexDict
        halfEdgeMapping: Dict[Any, HalfEdge] = dcel.halfEdgeDict
        faceMapping: Dict[FaceId, Face] = dcel.faceDict

        self.assertIsInstance(vertexMapping, dict, 'vertexDict should be a dict')
        self.assertIsInstance(halfEdgeMapping, dict, 'halfEdgeDict should be a dict')
        self.assertIsInstance(faceMapping, dict, 'faceDict should be a dict')
        self.assertEqual(3, len(vertexMapping), 'vertexDict should contain 3 entries')
        self.assertEqual(6, len(halfEdgeMapping), 'halfEdgeDict should contain 6 entries')
        self.assertEqual(2, len(faceMapping), 'faceDict should contain 2 entries')


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(TestDoublyConnectedEdgeList))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
