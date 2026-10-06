from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from tests.ProjectTestBase import ProjectTestBase

from orthogonal.doublyConnectedEdgeList.Face import Face
from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdge
from orthogonal.doublyConnectedEdgeList.HalfEdge import HalfEdgeId
from orthogonal.doublyConnectedEdgeList.Vertex import Vertex


class TestHalfEdge(ProjectTestBase):
    """
    Unit tests for the HalfEdge class in the Doubly-Connected Edge List (DCEL).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def testInitialization(self):
        """
        Verify that a HalfEdge initializes with correct default pointers and identifier.
        """
        edgeName: HalfEdgeId = HalfEdgeId(('u', 'v'))
        halfEdge: HalfEdge = HalfEdge(edgeName)

        self.assertEqual(edgeName, halfEdge.id, 'Identifier should match initialization argument')
        self.assertIsNone(halfEdge.twin, 'Twin property should initially be None')
        self.assertIsNone(halfEdge.origin, 'Origin property should initially be None')
        self.assertIsNone(halfEdge.incidentFace, 'IncidentFace property should initially be None')
        self.assertIsNone(halfEdge.previous, 'Previous property should initially be None')
        self.assertIsNone(halfEdge.next, 'Next property should initially be None')

    def testTwinProperty(self):
        """
        Verify that twin getter and setter correctly update the twin edge.
        """
        halfEdge1: HalfEdge = HalfEdge(HalfEdgeId(('u', 'v')))
        halfEdge2: HalfEdge = HalfEdge(HalfEdgeId(('v', 'u')))

        halfEdge1.twin = halfEdge2
        self.assertIs(halfEdge2, halfEdge1.twin, 'twin getter should return the assigned twin edge')

        halfEdge1.twin = None
        self.assertIsNone(halfEdge1.twin, 'twin should be None after resetting')

    def testOriginProperty(self):
        """
        Verify that origin getter and setter correctly update the origin vertex.
        """
        halfEdge: HalfEdge = HalfEdge(HalfEdgeId(('u', 'v')))
        originVertex: Vertex = Vertex('u')

        halfEdge.origin = originVertex
        self.assertIs(originVertex, halfEdge.origin, 'origin getter should return the assigned origin vertex')

        halfEdge.origin = None
        self.assertIsNone(halfEdge.origin, 'origin should be None after resetting')

    def testIncidentFaceProperty(self):
        """
        Verify that incidentFace getter and setter correctly update the incident face.
        """
        halfEdge: HalfEdge = HalfEdge(HalfEdgeId(('u', 'v')))
        face: Face = Face('f0')

        halfEdge.incidentFace = face
        self.assertIs(face, halfEdge.incidentFace, 'incidentFace getter should return the assigned face')

        halfEdge.incidentFace = None
        self.assertIsNone(halfEdge.incidentFace, 'incidentFace should be None after resetting')

    def testPreviousProperty(self):
        """
        Verify that previous getter and setter correctly update the predecessor edge.
        """
        halfEdge: HalfEdge = HalfEdge(HalfEdgeId(('v', 'w')))
        previousEdge: HalfEdge = HalfEdge(HalfEdgeId(('u', 'v')))

        halfEdge.previous = previousEdge
        self.assertIs(previousEdge, halfEdge.previous, 'previous getter should return the assigned predecessor')

        halfEdge.previous = None
        self.assertIsNone(halfEdge.previous, 'previous should be None after resetting')

    def testNextProperty(self):
        """
        Verify that next getter and setter correctly update the successor edge.
        """
        halfEdge: HalfEdge = HalfEdge(HalfEdgeId(('u', 'v')))
        nextEdge: HalfEdge = HalfEdge(HalfEdgeId(('v', 'w')))

        halfEdge.next = nextEdge
        self.assertIs(nextEdge, halfEdge.next, 'next getter should return the assigned successor')

        halfEdge.next = None
        self.assertIsNone(halfEdge.next, 'next should be None after resetting')

    def testGetPoints(self):
        """
        Verify getPoints returns a HalfEdgeId tuple of origin vertex IDs from self and twin.
        """
        uVertex: Vertex = Vertex('u')
        vVertex: Vertex = Vertex('v')

        halfEdge1: HalfEdge = HalfEdge(HalfEdgeId(('u', 'v')))
        halfEdge2: HalfEdge = HalfEdge(HalfEdgeId(('v', 'u')))

        halfEdge1.origin = uVertex
        halfEdge2.origin = vVertex
        halfEdge1.twin = halfEdge2
        halfEdge2.twin = halfEdge1

        points1: HalfEdgeId = halfEdge1.getPoints()
        points2: HalfEdgeId = halfEdge2.getPoints()

        self.assertEqual(HalfEdgeId(('u', 'v')), points1, 'halfEdge1 points should be (u, v)')
        self.assertEqual(HalfEdgeId(('v', 'u')), points2, 'halfEdge2 points should be (v, u)')

    def testGetPointsWithoutTwinRaisesAssertion(self):
        """
        Verify getPoints asserts that twin must be initialized before retrieval.
        """
        halfEdge: HalfEdge = HalfEdge(HalfEdgeId(('u', 'v')))
        halfEdge.origin = Vertex('u')

        with self.assertRaises(AssertionError):
            halfEdge.getPoints()

    def testSetAll(self):
        """
        Verify setAll assigns twin, origin, previous, next, and incidentFace references correctly.
        """
        halfEdge: HalfEdge = HalfEdge(HalfEdgeId(('u', 'v')))
        twinEdge: HalfEdge = HalfEdge(HalfEdgeId(('v', 'u')))
        previousEdge: HalfEdge = HalfEdge(HalfEdgeId(('z', 'u')))
        nextEdge: HalfEdge = HalfEdge(HalfEdgeId(('v', 'w')))
        originVertex: Vertex = Vertex('u')
        incidentFace: Face = Face('f0')

        halfEdge.setAll(
            twinEdge=twinEdge,
            originVertex=originVertex,
            previousEdge=previousEdge,
            nextEdge=nextEdge,
            incidentFace=incidentFace,
        )

        self.assertIs(twinEdge, halfEdge.twin, 'twin should be assigned correctly')
        self.assertIs(originVertex, halfEdge.origin, 'origin should be assigned correctly')
        self.assertIs(previousEdge, halfEdge.previous, 'previous should be assigned correctly')
        self.assertIs(nextEdge, halfEdge.next, 'next should be assigned correctly')
        self.assertIs(incidentFace, halfEdge.incidentFace, 'incidentFace should be assigned correctly')


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestHalfEdge))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
