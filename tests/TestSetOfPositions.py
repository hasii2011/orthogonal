
from typing import Set

from unittest import TestSuite
from unittest import main as unitTestMain

from tests.ProjectTestBase import ProjectTestBase


from orthogonal.mapping.EmbeddedTypes import Position


class TestSetOfPositions(ProjectTestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def testInSet(self):

        pos1: Position = Position(4, 4)
        pos2: Position = Position(5, 5)

        aSet: Set = set()
        aSet.add(pos1)
        aSet.add(pos2)

        self.assertTrue(pos1 in aSet, 'But, but I AM in the set')

    def testNotInSet(self):

        pos1: Position = Position(23, 23)
        pos2: Position = Position(42, 42)

        aSet: Set = {pos1, pos2}

        notInSet: Position = Position(7, 7)

        self.assertFalse(notInSet in aSet, 'But, but I am NOT in the set')


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()

    testSuite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestSetOfPositions))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
