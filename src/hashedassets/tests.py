from os import listdir, remove, mkdir, chdir
from os.path import isdir, join, abspath, dirname
from shutil import rmtree
import doctest
import unittest

EXECUTABLE = join(dirname(abspath(__file__)), '__init__.py')

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

        if cmdline[0] == 'hashedassets':
            cmdline[0:1] = [sys.executable, EXECUTABLE]

        if env == None:
            env = os.environ
        else:
            env.update(os.environ)

        env['PYTHONPATH'] = ':'.join(sys.path)

        process = Popen(cmdline, stderr=STDOUT, stdout=PIPE, env=env)
        # from http://stackoverflow.com/questions/1388753/how-to-get-output-from-subprocess-popen
        while True:
            out = process.stdout.read(1)
            if out == b'' and process.poll() != None:
                break
            if out != b'':
                sys.stdout.write(out.decode())

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

if __name__ == '__main__':
    import os, sys
    sys.path.insert(0, dirname(dirname(abspath(__file__))))
    sys.exit(unittest.TextTestRunner().run(test_suite()))
