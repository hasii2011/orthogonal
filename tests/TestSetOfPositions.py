from logging import Logger
from logging import getLogger
from typing import Set

from unittest import TestSuite
from unittest import main as unitTestMain

from tests.TestBase import TestBase


from orthogonal.mapping.EmbeddedTypes import Position


class TestSetOfPositions(TestBase):

    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestSetOfPositions.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestSetOfPositions.clsLogger

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
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestSetOfPositions))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
