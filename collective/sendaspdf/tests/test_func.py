import doctest
from unittest import TestSuite
from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite

from collective.sendaspdf.tests.base import SendAsPDFTestCase

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    func = ZopeDocFileSuite('func.txt',
                         package='collective.sendaspdf.tests',
                         optionflags=OPTIONFLAGS,
                         test_class=SendAsPDFTestCase)
    adapter = ZopeDocFileSuite('adapter.txt',
                         package='collective.sendaspdf.tests',
                         optionflags=OPTIONFLAGS,
                         test_class=SendAsPDFTestCase)

    return TestSuite((func, adapter, ))
