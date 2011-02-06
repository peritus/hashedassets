#!/usr/bin/env python
# vim: set filencoding=utf-8

from os.path import abspath, dirname, join, splitext, split as path_split

from hashlib import sha1, md5  # Python 2.5

from base64 import urlsafe_b64encode as urlsafe_b64encode
from sys import version_info
from functools import wraps

def encodedata(fun):
    @wraps(fun)
    def _encodestrings(data):
        return fun(data)
    return _encodestrings

if version_info[0] >= 3:
    def encodedata(fun):
        @wraps(fun)
        def _encodestrings(data):
            if isinstance(data, str):
                data = data.encode()
            return fun(data)
        return _encodestrings


    _urlsafe_b64encode = urlsafe_b64encode

    @encodedata
    def urlsafe_b64encode(data):
        return _urlsafe_b64encode(data).decode()

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

            if hasattr(item, '__call__'):
                return item(self[head])

            if str(tail).isdigit():
                return self[head][:int(tail)]

            raise KeyError("Unable to format '%s'" % key)

        if not hasattr(self, key):
            raise KeyError('%s not in %s' % (key, self))

        item = getattr(self, key, False)

        if hasattr(item, '__call__'):
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
    @encodedata
    def md5(data):
        return md5(data).digest()

    @staticmethod
    @encodedata
    def sha1(data):
        '''
        >>> print(repr(Rewriter.sha1('abc')).lstrip('b'))
        '\\xa9\\x99>6G\\x06\\x81j\\xba>%qxP\\xc2l\\x9c\\xd0\\xd8\\x9d'
        >>> print(repr(Rewriter.sha1('服部 半蔵')).lstrip('b'))
        '|\\xa6\\xcd0%\\xef\\x08\\xd1+6iV\\x92\\xbb\\x826W~\\x170'
        '''
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
        return open(filename, 'rb').read()

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

