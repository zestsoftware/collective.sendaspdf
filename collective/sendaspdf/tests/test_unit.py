import unittest
import doctest

from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite

from collective.sendaspdf.tests.base import OPTIONFLAGS
from collective.sendaspdf.tests.base import SendAsPDFTestCase


def test_suite():
    utils_py = doctest.DocFileSuite('utils.py',
                                    optionflags=OPTIONFLAGS,
                                    package='collective.sendaspdf')
    utils_txt = ZopeDocFileSuite('utils.txt',
                                 package='collective.sendaspdf.tests',
                                 optionflags=OPTIONFLAGS,
                                 test_class=SendAsPDFTestCase)
    return unittest.TestSuite([utils_py, utils_txt])
