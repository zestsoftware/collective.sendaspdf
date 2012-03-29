import unittest
import doctest

from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite

from collective.sendaspdf.tests.base import OPTIONFLAGS
from collective.sendaspdf.tests.base import SendAsPDFTestCase

def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite('utils.py',
                              optionflags=OPTIONFLAGS,
                              package='collective.sendaspdf'),

        ZopeDocFileSuite('utils.txt',
                         package='collective.sendaspdf.tests',
                         optionflags=OPTIONFLAGS,
                         test_class=SendAsPDFTestCase)
        ])
