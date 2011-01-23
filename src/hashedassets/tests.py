from os import listdir, remove, mkdir, chdir
from os.path import isdir, join, abspath, dirname
from shutil import rmtree
import doctest
import unittest

def setUp():
    try:
        mkdir('./__hashedassets_tests')
    except:
        pass

    chdir('./__hashedassets_tests')

    for afile in listdir('.'):
        if isdir(afile):
            rmtree(afile)
        else:
            remove(afile)

def test_globs():
    import os
    import sys
    from subprocess import Popen, STDOUT, PIPE
    from shlex import split
    from hashedassets import main

    def system(cmd, env=None, external=False):  # pylint: disable=W0612
        cmdline = split(cmd)

        if not external and cmdline[0] == 'hashedassets':
            _stderr = sys.stderr
            sys.stderr = sys.stdout
            try:
                return main(cmdline[1:])
            finally:
                sys.stderr = _stderr

        if env != None:
            env.update(os.environ)
        process = Popen(cmdline, stderr=STDOUT, stdout=PIPE, env=env)
        # from http://stackoverflow.com/questions/1388753/how-to-get-output-from-subprocess-popen
        while True:
            out = process.stdout.read(1)
            if out == '' and process.poll() != None:
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()

    def write(filename, content):  # pylint: disable=W0612
        f = open(filename, "w")
        f.write(content)
        f.close()

    return locals()

def test_suite():

    opts = dict(
      module_relative=False,
      globs=test_globs(),
      optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS|doctest.REPORT_UDIFF,
    )

    suite = unittest.TestSuite([
        doctest.DocTestSuite('hashedassets'),
        doctest.DocTestSuite('hashedassets.rewrite'),
        doctest.DocTestSuite('hashedassets.serializer'),

        doctest.DocFileSuite(join(dirname(abspath(__file__)), 'hashedassets.rst'), **opts),
        doctest.DocFileSuite(join(dirname(abspath(__file__)), 'errors.rst'), **opts),
        doctest.DocFileSuite(join(dirname(abspath(__file__)), 'regressions.rst'), **opts),
    ])

    setUp()

    return suite
