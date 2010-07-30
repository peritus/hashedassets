from shutil import rmtree
import doctest
import os
import unittest

def setUp():
    for file in os.listdir('.'):
        if os.path.isdir(file):
            rmtree(file)
        else:
            os.remove(file)

def test_globs():
    import os
    import sys
    from subprocess import Popen, STDOUT, PIPE
    from shlex import split

    def system(cmd, env=None):
        if env != None:
            env.update(os.environ)
        process = Popen(split(cmd), stderr=STDOUT, stdout=PIPE, env=env)
        # from http://stackoverflow.com/questions/1388753/how-to-get-output-from-subprocess-popen
        while True:
            out = process.stdout.read(1)
            if out == '' and process.poll() != None:
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()

    return locals()

def test_suite():
    setUp()

    return unittest.TestSuite(
        doctest.DocFileSuite(
            'hashedassets.rst',
            globs=test_globs(),
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS|doctest.REPORT_UDIFF),
    )
