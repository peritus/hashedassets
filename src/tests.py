import unittest
import doctest
from shutil import rmtree

import os


def setUp(dir):
    if os.path.isdir(dir):
        rmtree(dir)
    os.mkdir(dir)
    os.chdir(dir)

def test_suite():
    setUp('work')
    suite = unittest.TestSuite(
        doctest.DocFileSuite('hashedassets.rst',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS|doctest.REPORT_UDIFF),
    )
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
