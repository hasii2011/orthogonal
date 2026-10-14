from typing import NamedTuple


class NodeCoordinate(NamedTuple):
    x: int
    y: int


class Geometry2D:
    """
    2D computational geometry utilities.
    """

    @classmethod
    def crossProduct(cls, v1: NodeCoordinate, v2: NodeCoordinate) -> int:
        """
        Compute the 2D cross product (determinant) of vectors v1 and v2.

        Args:
            v1: First vector as a NodeCoordinate (dx, dy).
            v2: Second vector as a NodeCoordinate (dx, dy).

        Returns:
            Signed area of the parallelogram spanned by v1 and v2.
        """
        return v1.x * v2.y - v1.y * v2.x

    @classmethod
    def orientation(cls, pa: NodeCoordinate, pb: NodeCoordinate, p: NodeCoordinate) -> int:
        """
        Compute the signed orientation of point p relative to the directed line segment pa -> pb.

        Args:
            pa: Origin point of the directed line segment.
            pb: Destination point of the directed line segment.
            p: Query point to evaluate orientation for.

        Returns:
            0 if pa, pb, and p are collinear (all 3 lie on the same straight line).
            Positive integer (> 0) if p lies to the left of directed segment pa -> pb (counter-clockwise).
            Negative integer (< 0) if p lies to the right of directed segment pa -> pb (clockwise).
        """
        segmentDeltaY: int = pa.y - pb.y
        segmentDeltaX: int = pa.x - pb.x

        pointDeltaX: int = p.x - pb.x
        pointDeltaY: int = p.y - pb.y

        crossTerm1: int = segmentDeltaY * pointDeltaX
        crossTerm2: int = pointDeltaY * segmentDeltaX

        return crossTerm1 - crossTerm2

    @classmethod
    def isCross(cls, pa: NodeCoordinate, pb: NodeCoordinate, pc: NodeCoordinate, pd: NodeCoordinate) -> bool:
        """
        Determine whether line segment (pa, pb) intersects line segment (pc, pd).

        Args:
            pa: First endpoint of segment AB.
            pb: Second endpoint of segment AB.
            pc: First endpoint of segment CD.
            pd: Second endpoint of segment CD.

        Returns:
            True if the two line segments cross, False otherwise.
        """
        ca: NodeCoordinate = NodeCoordinate(pa.x - pc.x, pa.y - pc.y)
        cb: NodeCoordinate = NodeCoordinate(pb.x - pc.x, pb.y - pc.y)
        cd: NodeCoordinate = NodeCoordinate(pd.x - pc.x, pd.y - pc.y)

        crossCaCd: int = cls.crossProduct(ca, cd)
        crossCdCb: int = cls.crossProduct(cd, cb)

        orientationC: int = cls.orientation(pa, pb, pc)
        orientationD: int = cls.orientation(pa, pb, pd)
        pointsStraddleAB: bool = (orientationC * orientationD) < 0

        endpointsStraddleCD: bool = (crossCaCd >= 0) and (crossCdCb >= 0)

        return endpointsStraddleCD and pointsStraddleAB
