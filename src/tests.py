from shutil import rmtree
import doctest
import os
import unittest

def setUp(dir):
    if os.path.isdir(dir):
        rmtree(dir)
    os.mkdir(dir)
    os.chdir(dir)

def test_suite():
    setUp('work')
    return unittest.TestSuite(
        doctest.DocFileSuite('hashedassets.rst',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS|doctest.REPORT_UDIFF),
    )
