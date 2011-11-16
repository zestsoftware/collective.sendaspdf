import unittest
from zope.testing import doctest

from collective.sendaspdf.tests.base import OPTIONFLAGS

def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite('utils.py',
                              optionflags=OPTIONFLAGS,
                              package='collective.sendaspdf'),
        ])
