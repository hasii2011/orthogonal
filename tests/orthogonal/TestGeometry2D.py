
from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from tests.ProjectTestBase import ProjectTestBase

from orthogonal.geometry.Geometry2D import Geometry2D
from orthogonal.geometry.Geometry2D import NodeCoordinate


class TestGeometry2D(ProjectTestBase):
    """
    Unit tests for Geometry2D classmethods: crossProduct, orientation, and isCross.
    """

    def testCrossProductOrthogonalUnitVectors(self):
        """
        Verify cross product of orthogonal unit vectors.
        """
        vectorX: NodeCoordinate = NodeCoordinate(1, 0)
        vectorY: NodeCoordinate = NodeCoordinate(0, 1)

        result: int = Geometry2D.crossProduct(vectorX, vectorY)
        self.assertEqual(1, result, 'Unit X cross Unit Y must equal 1')

        reverseResult: int = Geometry2D.crossProduct(vectorY, vectorX)
        self.assertEqual(-1, reverseResult, 'Unit Y cross Unit X must equal -1')

    def testCrossProductCollinearVectors(self):
        """
        Verify cross product of parallel/collinear vectors is zero.
        """
        vectorA: NodeCoordinate = NodeCoordinate(2, 3)
        vectorB: NodeCoordinate = NodeCoordinate(4, 6)

        result: int = Geometry2D.crossProduct(vectorA, vectorB)
        self.assertEqual(0, result, 'Cross product of parallel vectors must equal 0')

    def testOrientationCollinear(self):
        """
        Verify orientation returns 0 when point lies on the line segment.
        """
        pointA: NodeCoordinate = NodeCoordinate(0, 0)
        pointB: NodeCoordinate = NodeCoordinate(4, 4)
        collinearPoint: NodeCoordinate = NodeCoordinate(2, 2)

        result: int = Geometry2D.orientation(pointA, pointB, collinearPoint)
        self.assertEqual(0, result, 'Collinear points must return orientation 0')

    def testOrientationCounterClockwise(self):
        """
        Verify orientation returns positive value for counter-clockwise turn (left).
        """
        pointA: NodeCoordinate = NodeCoordinate(0, 0)
        pointB: NodeCoordinate = NodeCoordinate(4, 0)
        leftPoint: NodeCoordinate = NodeCoordinate(2, 2)

        result: int = Geometry2D.orientation(pointA, pointB, leftPoint)
        self.assertGreater(result, 0, 'Counter-clockwise point must have positive orientation')

    def testOrientationClockwise(self):
        """
        Verify orientation returns negative value for clockwise turn (right).
        """
        pointA: NodeCoordinate = NodeCoordinate(0, 0)
        pointB: NodeCoordinate = NodeCoordinate(4, 0)
        rightPoint: NodeCoordinate = NodeCoordinate(2, -2)

        result: int = Geometry2D.orientation(pointA, pointB, rightPoint)
        self.assertLess(result, 0, 'Clockwise point must have negative orientation')

    def testIsCrossIntersectingSegments(self):
        """
        Verify isCross detects intersecting line segments.
        """
        pointA: NodeCoordinate = NodeCoordinate(0, 1)
        pointB: NodeCoordinate = NodeCoordinate(2, 1)
        pointC: NodeCoordinate = NodeCoordinate(1, 2)
        pointD: NodeCoordinate = NodeCoordinate(1, 0)

        crossDetected: bool = Geometry2D.isCross(pointA, pointB, pointC, pointD)
        self.assertTrue(crossDetected, 'Perpendicular intersecting segments must be detected as crossing')

    def testIsCrossParallelDisjointSegments(self):
        """
        Verify isCross returns False for parallel disjoint segments.
        """
        pointA: NodeCoordinate = NodeCoordinate(0, 0)
        pointB: NodeCoordinate = NodeCoordinate(4, 0)
        pointC: NodeCoordinate = NodeCoordinate(0, 2)
        pointD: NodeCoordinate = NodeCoordinate(4, 2)

        crossDetected: bool = Geometry2D.isCross(pointA, pointB, pointC, pointD)
        self.assertFalse(crossDetected, 'Parallel disjoint segments must not cross')

    def testIsCrossCollinearDisjointSegments(self):
        """
        Verify isCross returns False for collinear non-overlapping segments.
        """
        pointA: NodeCoordinate = NodeCoordinate(0, 0)
        pointB: NodeCoordinate = NodeCoordinate(2, 0)
        pointC: NodeCoordinate = NodeCoordinate(4, 0)
        pointD: NodeCoordinate = NodeCoordinate(6, 0)

        crossDetected: bool = Geometry2D.isCross(pointA, pointB, pointC, pointD)
        self.assertFalse(crossDetected, 'Collinear non-overlapping segments must not cross')


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(TestGeometry2D))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
