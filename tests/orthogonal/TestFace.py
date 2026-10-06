from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from tests.ProjectTestBase import ProjectTestBase

from orthogonal.doublyConnectedEdgeList.DcelExceptions import UninitializedDcelError
from orthogonal.doublyConnectedEdgeList.Face import Face
from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdge
from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdgeId
from orthogonal.doublyConnectedEdgeList.Vertex import Vertex


class TestFace(ProjectTestBase):
    """
    Unit tests for the Face class in the Doubly-Connected Edge List (DCEL).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def testInitialization(self):
        """
        Verify that a Face initializes with the correct identifier, empty node list, and raises on uninitialized incidentEdge.
        """
        faceName: str = 'f0'
        face: Face = Face(faceName)

        self.assertEqual(faceName, face.id, 'Identifier should match initialization argument')
        self.assertFalse(face.hasIncidentEdge, 'hasIncidentEdge should initially be False')
        with self.assertRaises(UninitializedDcelError):
            _ = face.incidentEdge

        self.assertEqual([], face.nodes_id, 'nodes_id should initially be an empty list')
        self.assertEqual(0, len(face), 'Length of a newly initialized face should be 0')
        self.assertEqual('FaceView[]', repr(face), 'String representation should reflect empty nodes_id')

    def testIncidentEdgeProperty(self):
        """
        Verify that incidentEdge getter and setter correctly update the incident half-edge and raise when uninitialized.
        """
        face: Face = Face('f1')
        halfEdge: HalfEdge = HalfEdge(HalfEdgeId(('u', 'v')))

        self.assertFalse(face.hasIncidentEdge, 'hasIncidentEdge should be False before assignment')
        face.incidentEdge = halfEdge
        self.assertTrue(face.hasIncidentEdge, 'hasIncidentEdge should be True after assignment')
        self.assertIs(halfEdge, face.incidentEdge, 'incidentEdge getter should return the assigned half-edge')

        face.incidentEdge = None
        self.assertFalse(face.hasIncidentEdge, 'hasIncidentEdge should be False after reset')
        with self.assertRaises(UninitializedDcelError):
            _ = face.incidentEdge

    def testSurroundHalfEdgesWhenNone(self):
        """
        Verify that surround_half_edges yields nothing when incidentEdge is not set.
        """
        face: Face = Face('f2')
        edges: list[HalfEdge] = list(face.surround_half_edges())

        self.assertEqual([], edges, 'surround_half_edges should yield an empty sequence when incidentEdge is not set')

    def testSurroundHalfEdgesCycle(self):
        """
        Verify that surround_half_edges cycles through all boundary half-edges in order.
        """
        face: Face = Face('f3')

        vertex1: Vertex = Vertex('v1')
        vertex2: Vertex = Vertex('v2')
        vertex3: Vertex = Vertex('v3')

        edge1: HalfEdge = HalfEdge(HalfEdgeId(('v1', 'v2')))
        edge2: HalfEdge = HalfEdge(HalfEdgeId(('v2', 'v3')))
        edge3: HalfEdge = HalfEdge(HalfEdgeId(('v3', 'v1')))

        edge1.origin = vertex1
        edge2.origin = vertex2
        edge3.origin = vertex3

        edge1.next = edge2
        edge2.next = edge3
        edge3.next = edge1

        edge1.incidentFace = face
        edge2.incidentFace = face
        edge3.incidentFace = face

        face.incidentEdge = edge1

        surroundingEdges: list[HalfEdge] = list(face.surround_half_edges())
        self.assertEqual([edge1, edge2, edge3], surroundingEdges, 'Boundary edges should match clockwise order')

        surroundingVertices: list[Vertex] = list(face.surround_vertices())
        self.assertEqual([vertex1, vertex2, vertex3], surroundingVertices, 'Boundary vertices should match origin order')

        face.update_nodes()
        self.assertEqual(['v1', 'v2', 'v3'], face.nodes_id, 'nodes_id should contain vertex identifiers')
        self.assertEqual(3, len(face), 'len(face) should return the count of bounding nodes')
        self.assertEqual("FaceView['v1', 'v2', 'v3']", repr(face), 'repr should reflect updated nodes_id')

    def testSurroundFaces(self):
        """
        Verify that surround_faces correctly yields adjacent faces via twin half-edges.
        """
        face1: Face = Face('f_inner')
        face2: Face = Face('f_outer1')
        face3: Face = Face('f_outer2')

        edge1: HalfEdge = HalfEdge(HalfEdgeId(('a', 'b')))
        edge2: HalfEdge = HalfEdge(HalfEdgeId(('b', 'a')))
        twin1: HalfEdge = HalfEdge(HalfEdgeId(('b', 'a')))
        twin2: HalfEdge = HalfEdge(HalfEdgeId(('a', 'b')))

        edge1.next = edge2
        edge2.next = edge1
        edge1.twin = twin1
        edge2.twin = twin2

        twin1.incidentFace = face2
        twin2.incidentFace = face3

        face1.incidentEdge = edge1

        neighborFaces: list[Face] = list(face1.surround_faces())
        self.assertEqual([face2, face3], neighborFaces, 'surround_faces should yield adjacent faces of twin edges')


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(TestFace))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
