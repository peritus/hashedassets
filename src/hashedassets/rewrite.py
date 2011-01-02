#!/usr/bin/env python

from os.path import abspath, dirname, join, splitext, split as path_split

try:
    from hashlib import sha1, md5  # Python 2.5
except ImportError:
    from sha import sha as sha1    # Python 2.4
    from md5 import md5

from base64 import urlsafe_b64encode


class Rewriter(object):

    def __init__(self, relpath, basedir=None):

        self._relpath = relpath # path, relative to basedir
        self._basedir = basedir or '.'

    def __repr__(self):
        '''
        >>> Rewriter('foo/bar')
        <Rewriter('foo/bar')>
        '''
        return "<Rewriter('%(relpath)s')>" % self

    def __getitem__(self, key):
        '''
        >>> Rewriter('path/file')['complete_filename|base64']
        'ZmlsZQ'
        >>> Rewriter('path/file')['complete_filename|md5|base64']
        'jH3ZIq1HSU_ALDiOEsAOrA'
        >>> Rewriter('path/file')['relpath|md5|base64|3']
        '3Hc'
        >>> Rewriter('path/pr0n.f')['extension|base64']
        'Zg'
        '''

        if '|' in key:
            splitted = key.split('|')

            head = '|'.join(splitted[:-1])
            tail = splitted[-1]

            item = getattr(self, tail, False)

            if callable(item):
                return item(self[head])

            if str(tail).isdigit():
                return self[head][:int(tail)]

            raise KeyError("Unable to format '%s'" % key)

        if not hasattr(self, key):
            raise KeyError('%s not in %s' % (key, self))

        item = getattr(self, key, False)

        if callable(item):
            return item()

        return str(item)

    @classmethod
    def compute_rewritestring(cls, strip_extensions=False, digestlength=None, keep_dirs=False, hashfun='sha1'):
        '''
        >>> Rewriter.compute_rewritestring()
        '%(abspath|content|sha1|base64)s%(suffix)s'
        >>> Rewriter.compute_rewritestring(strip_extensions=True)
        '%(abspath|content|sha1|base64)s'
        >>> Rewriter.compute_rewritestring(digestlength=3)
        '%(abspath|content|sha1|base64|3)s%(suffix)s'
        '''

        if hashfun == 'identity':
            return '%(relpath)s'

        initial = [ 'abspath', 'content', hashfun, 'base64', ]

        if digestlength:
            initial.append(str(digestlength))

        rewritestring = ("%(" + '|'.join(initial) + ")s")

        if keep_dirs:
            rewritestring = "%(reldir)s" + rewritestring

        if not strip_extensions:
            rewritestring += "%(suffix)s"

        return rewritestring

    @staticmethod
    def md5(data):
        return md5(data).digest()

    @staticmethod
    def sha1(data):
        return sha1(data).digest()

    hash = sha1

    @staticmethod
    def identity(data):
        '''
        >>> Rewriter('./').identity('onetwothree')
        'onetwothree'
        '''

        return data

    @staticmethod
    def base64(data):
        '''
        >>> Rewriter('./').base64('1')
        'MQ'
        >>> Rewriter('./').base64('123')
        'MTIz'
        >>> Rewriter('./').base64('12345')
        'MTIzNDU'
        '''
        return urlsafe_b64encode(data).strip("=")

    @staticmethod
    def content(filename):
        return open(filename).read()

    '''
    Naming conventions for path parts:

    /to/input/bar/baz.txt
    ..............^^^^^^^ .complete_filename
    ..............^^^.... .filename
    .................^^^^ .suffix
    ..................^^^ .extension
    ..........^^^^^^^^^^^ .relpath
    ..........^^^^....... .reldir
    ^^^^^^^^^^^^^^^^^^^^^ .abspath
    '''

    def abspath(self):
        '''
        >>> Rewriter('bar/baz.txt').abspath().startswith('/')
        True
        >>> Rewriter('bar/baz.txt').abspath().endswith('bar/baz.txt')
        True
        '''
        return abspath(join(self._basedir, self._relpath))

    def reldir(self):
        '''
        >>> Rewriter('bar/baz.txt').reldir()
        'bar/'
        '''
        reldir = dirname(self._relpath)
        if reldir:
            return reldir + '/'

        return ''

    def relpath(self):
        '''
        >>> Rewriter('bar/baz.txt').relpath()
        'bar/baz.txt'
        '''
        return self._relpath

    def complete_filename(self):
        '''
        >>> Rewriter('/foo/bar/baz.txt').complete_filename()
        'baz.txt'
        '''
        return path_split(self._relpath)[1]

    def filename(self):
        '''
        >>> Rewriter('/foo/bar/baz.txt').filename()
        'baz'
        '''
        return splitext(self.complete_filename())[0]

    def suffix(self):
        '''
        >>> Rewriter('foo').suffix()
        ''
        >>> Rewriter('foo.txt').suffix()
        '.txt'
        '''
        ext = self.extension()
        if ext:
            return '.%s' % ext
        else:
            return ext

    def extension(self):
        '''
        >>> Rewriter('./foo.txt').extension()
        'txt'
        '''
        return splitext(self._relpath)[1].lstrip('.')

