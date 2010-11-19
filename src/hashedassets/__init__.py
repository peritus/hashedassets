#!/usr/bin/env python

'''
A command line tool that copies files to filenames based on their contents. It
also writes a map of what was renamed to what, so you can find your files.

Main purpose of this is that you can `add a far future Expires header to your
components <http://stevesouders.com/hpws/rule-expires.php>`__. Using hash based
filenames is a lot better than using your $VCS revision number, because users
only need to download files that didn't change.

'''

from base64 import urlsafe_b64encode
import logging
from glob import glob
from optparse import OptionParser
from os import remove, mkdir, makedirs
from os.path import join, exists, isdir, relpath, \
                    splitext, normpath, dirname, commonprefix, \
                    split as path_split, samefile
from re import split as re_split
from shutil import copy2, Error as shutil_Error
import sys
from itertools import chain

try:
    from hashlib import sha1, md5  # Python 2.5
except ImportError:
    from sha import sha as sha1    # Python 2.4
    from md5 import md5

try:
    # Python 2.7
    from collections import OrderedDict  # pylint: disable=E0611
except ImportError:
    try:
        # Python 2.6
        from odict import odict as OrderedDict
    except ImportError:
        pass

logger = logging.getLogger("hashedassets")

__version__ = 0, 2, 2

SERIALIZERS = {}


class SimpleSerializer(object):
    @classmethod
    def serialize(cls, items, _):
        return "\n".join([
            "%s: %s" % item
            for item
            in items.iteritems()]) + "\n"

    @classmethod
    def deserialize(cls, string):
        result = {}
        for line in string.split("\n"):
            if line == '':
                continue
            key, value = line.split(":")
            result[key.strip()] = value.strip()
        return result

SERIALIZERS['txt'] = SimpleSerializer

try:
    from json import loads, dumps
except ImportError:
    try:
        from simplejson import loads, dumps
    except ImportError:
        loads, dumps = (None, None)

if loads and dumps:

    class JSONSerializer(object):
        @classmethod
        def serialize(cls, items, _):
            return dumps(items, sort_keys=True, indent=2)

        @classmethod
        def deserialize(cls, string):
            return loads(string)

    SERIALIZERS['json'] = JSONSerializer

    class JSONPSerializer(object):
        @classmethod
        def serialize(cls, items, map_name):
            return "%(map_name)s(%(dump)s);" % {
                    'map_name': map_name,
                    'dump': dumps(items, sort_keys=True, indent=2)}

        @classmethod
        def deserialize(cls, string):
            return loads(string[string.index("(") + 1:string.rfind(")")])

    SERIALIZERS['jsonp'] = JSONPSerializer

    class JavaScriptSerializer(object):
        @classmethod
        def serialize(cls, items, map_name):
            return (
                "var %s = " % map_name
                + dumps(items, sort_keys=True, indent=2)
                + ";")

        @classmethod
        def deserialize(cls, string):
            return loads(string[string.index("=") + 1:string.rfind(";")])

    SERIALIZERS['js'] = JavaScriptSerializer


class PreambleEntryEpiloqueSerializer(object):  # pylint: disable=R0903
    PREAMBLE = ''
    ENTRY = ''
    EPILOQUE = ''

    @classmethod
    def serialize(cls, items, map_name):
        return (
            (cls.PREAMBLE % map_name) + "".join([
                cls.ENTRY % item
                for item
                in items.iteritems()]) +
            cls.EPILOQUE)


class SassSerializer(PreambleEntryEpiloqueSerializer):
    PREAMBLE = (
    '@mixin %s($directive, $path) {\n'
    '         @')

    ENTRY = (
    'if $path == "%s" { #{$directive}: url("%s"); }\n'
    '    @else ')

    EPILOQUE = (
    '{\n'
    '      @warn "Did not find "#{$path}" in list of assets";\n'
    '      #{$directive}: url($path);\n'
    '    }\n'
    '}')

    @classmethod
    def deserialize(cls, string):
        result = {}
        for line in string.split(";")[:-3]:
            _, key, _, value, _ = line.split('"')
            result[key] = value
        return result

SERIALIZERS['scss'] = SassSerializer


class PHPSerializer(PreambleEntryEpiloqueSerializer):
    PREAMBLE = '$%s = array(\n'
    ENTRY = '  "%s" => "%s",\n'
    EPILOQUE = ')'

    @classmethod
    def deserialize(cls, string):
        result = {}
        for line in string.split("\n")[1:-1]:
            _, key, _, value, _ = line.split('"')
            result[key] = value
        return result

SERIALIZERS['php'] = PHPSerializer


class SedSerializer(object):
    '''
    Writes a sed script, use like this:

    sed -f map.sed FILE_NEEDING_REPLACEMENTS
    '''
    ENTRY = 's/%s/%s/g'

    REPLACEMENTS = {
        '/': '\\/',
        '.': '\\.',
    }

    @classmethod
    def _escape_filename(cls, filename, reverse=False):
        for key, value in cls.REPLACEMENTS.iteritems():
            if reverse:
                key, value = value, key
            filename = filename.replace(key, value)
        return filename

    @classmethod
    def serialize(cls, items, _):
        return "\n".join([
            (cls.ENTRY % (cls._escape_filename(key),
                cls._escape_filename(value)))
            for key, value
            in items.iteritems()]) + '\n'

    @classmethod
    def deserialize(cls, string):
        result = {}
        for line in string.split("\n"):
            if line == '':
                continue

            _, key, value, _ = re_split("(?<=[^\\\])/", line)
            key = cls._escape_filename(key.strip(), True)
            value = cls._escape_filename(value.strip(), True)
            result[key] = value
        return result

SERIALIZERS['sed'] = SedSerializer


class AssetHasher(object):
    def __init__(self, files, output_dir, map_filename, map_name, map_type,
            keep_dirs=False,
            map_only=False,
            strip_extensions=False,
            digestlength=9999,  # don't truncate
            hashfun='sha1',
            ):

        self.input_dir = dirname(commonprefix(files))

        self.files = OrderedDict.fromkeys(  # python is lisp!
                         map(lambda l: relpath(l, self.input_dir),
                             chain.from_iterable(map(glob, files))))

        logger.debug("Initialized map, is now %s", self.files)

        self.output_dir = output_dir
        self.map_filename = map_filename
        self.map_name = map_name
        self.map_type = map_type
        self.map_only = map_only
        self.strip_extensions = strip_extensions
        self.digestlength = digestlength
        self.keep_dirs = keep_dirs

        if hashfun == None:
            hashfun = 'sha1'

        self.hashfun = hashfun

    def digest(self, fun, filename):
        _, extension = splitext(filename)

        if fun == 'identity':
            _, hashed_filename = path_split(filename)
        else:
            fun = {'md5': md5, 'sha1': sha1}[fun]
            hashed_filename = urlsafe_b64encode(
                    fun(open(join(self.input_dir, filename)).read()).digest()).strip("=")\
                            [:self.digestlength]
            if extension and not self.strip_extensions:
                hashed_filename = "%s%s" % (hashed_filename, extension)

        extra_dirs = ''

        if self.keep_dirs:
            extra_dirs, _ = path_split(filename)

        return join(extra_dirs, hashed_filename)

    def process_file(self, filename):
        logger.debug("Processing file '%s'", filename)

        try:
            hashed_filename = self.digest(self.hashfun, filename)
        except IOError, e:
            logger.debug("'%s' does not exist, can't be hashed", filename)
            return

        logger.debug("Determined new hashed filename: '%s'", hashed_filename)

        if self.files[filename]:
            logger.debug("File has been processed in a previous run (hashed to '%s' then)",
                    self.files[filename])

            outfile = join(self.output_dir, self.files[filename])

            if exists(outfile):
                logger.debug("%s still exists", outfile)

                if hashed_filename == self.files[filename]:
                    # skip file
                    logger.debug("Skipping file '%s' -> '%s'", filename, self.files[filename])
                    return

                # remove dangling file
                if not self.map_only:
                    remove(outfile)
                    logger.info("rm '%s'", outfile)


        infile = join(self.input_dir, filename)
        outfile = join(self.output_dir, hashed_filename)

        try:
            if samefile(infile, outfile):
               logger.debug("Won't copy '%s' to itself.", filename)
               return
        except OSError, e:
            if not (e.strerror == 'No such file or directory' and e.filename == outfile):
                assert False,  (dir(e), e.message, e.errno, e.strerror, e.filename)
                raise

        try:
            if not self.map_only:
                copy2(infile, outfile)
        except IOError, e:
            if not e.strerror == 'No such file or directory':
                raise

            # create parent dirs that are needed for the output file
            logger.debug(hashed_filename)
            create_dir, _ = path_split(hashed_filename)
            logger.info("mkdir -p %s" % join(self.output_dir, create_dir))
            makedirs(join(self.output_dir, create_dir))

            # try again
            copy2(join(self.input_dir, filename), join(self.output_dir,
                hashed_filename))

        self.files[filename] = hashed_filename

        if not self.map_only:
            logger.info(
                "cp '%s' '%s'",
                join(self.input_dir, filename),
                join(self.output_dir, hashed_filename))

    def process_all_files(self):
        for f in self.files:
            self.process_file(f)

    def read_map(self):
        if not self.map_filename:
            return

        if not exists(self.map_filename):
            return

        content = open(self.map_filename).read()

        deserialized = SERIALIZERS[self.map_type].deserialize(content)

        for filename, hashed_filename in deserialized.iteritems():
            self.files[filename] = hashed_filename

        logger.debug("Read map, is now: %s", self.files)

    def write_map(self):
        if not self.map_filename:
            return

        serialized = SERIALIZERS[self.map_type].serialize(OrderedDict(
            (k,v) for k, v in self.files.iteritems() if v != None
            ), self.map_name)

        f = open(self.map_filename, "w")
        f.write(serialized)
        f.close()

    def run(self):
        self.read_map()
        self.process_all_files()
        self.write_map()

def main(args=None):
    if args == None:
        args = sys.argv[1:]

    version = ".".join(str(n) for n in __version__)

    parser = OptionParser(
      usage="%prog [ options ] MAPFILE SOURCE [...] DEST",
      version="%prog " + version,
      description='Version: %s' % version,
    )

    parser.add_option(
      "-v",
      "--verbose",
      action="count",
      dest="verbosity",
      help="increase verbosity level",
    )

    parser.add_option(
      "-q",
      "--quiet",
      action="store_const",
      const=0,
      dest="verbosity",
      help="don't print status messages to stdout",
    )

    parser.add_option(
      "-n",
      "--map-name",
      default="hashedassets",
      dest="map_name",
      help="name of the map [default: %default]",
      metavar="MAPNAME",
      type="string",
    )

    parser.add_option(
      "-t",
      "--map-type",
      choices=SERIALIZERS.keys(),
      dest="map_type",
      help=("type of the map. one of "
          + ", ".join(SERIALIZERS.keys())
          + " [default: guessed from MAPFILE]"),
      metavar="MAPTYPE",
      type="choice",
    )

    parser.add_option(
      "-l",
      "--digest-length",
      default=27,
      dest="digestlength",
      help=("length of the generated filenames "
            "(without extension) [default: %default]"),
      metavar="LENGTH",
      type="int",
    )

    parser.add_option(
      "-d",
      "--digest",
      choices=('sha1', 'md5'),
      default='sha1',
      dest="hashfun",
      help="hash function to use. One of sha1, md5 [default: %default]",
      metavar="HASHFUN",
      type="choice",
    )

    parser.add_option(
      "-k",
      "--keep-dirs",
      action="store_true",
      dest="keep_dirs",
      default=False,
      help="Mirror SOURCE dir structure to DEST [default: false]",
    )

    parser.add_option(
      "-i",
      "--identity",
      action="store_true",
      dest="identity",
      default=False,
      help="Don't actually map, keep all file names",
    )

    parser.add_option(
      "-o",
      "--map-only",
      action="store_true",
      dest="map_only",
      default=False,
      help="Don't move files, only generate a map",
    )

    parser.add_option(
      "-s",
      "--strip-extensions",
      action="store_true",
      dest="strip_extensions",
      default=False,
      help="Strip the file extensions from the hashed files",
    )

    (options, args) = parser.parse_args(args)

    if options.identity:
        options.hashfun = 'identity'
        options.keep_dirs = True

    if options.verbosity == None:
        options.verbosity = 1

    if len(logger.handlers) == 0:
        ch = logging.StreamHandler(sys.stdout)
        logger.addHandler(ch)

    log_level = {
        0: logging.ERROR,
        1: logging.INFO,
        2: logging.DEBUG,
    }.get(options.verbosity, logging.DEBUG)
    logger.setLevel(log_level)

    if len(args) < 2 and options.map_only:
        print args
        parser.error("In --map-only mode, you need to specify at least MAPFILE and SOURCE")

    if len(args) < 3 and not options.map_only:
        parser.error("You need to specify at least MAPFILE, SOURCE and DEST")

    map_filename = args[0]

    if not options.map_type and map_filename:
        options.map_type = splitext(map_filename)[1].lstrip(".")

    if not options.map_type in SERIALIZERS.keys():
        parser.error("Invalid map type: '%s'" % options.map_type)

    if options.map_only:
        files = args[1:]
        output_dir = '.'
    else:
        files = args[1:-1]
        output_dir = normpath(args[-1])
        if not exists(output_dir):
            mkdir(output_dir)
            logger.info("mkdir '%s'", output_dir)
        elif not isdir(output_dir):
            parser.error("Output dir at '%s' is not a directory" % output_dir)

    AssetHasher(
      files=files,
      output_dir=output_dir,
      map_filename=map_filename,
      map_name=options.map_name,
      map_type=options.map_type,
      map_only=options.map_only,
      strip_extensions=options.strip_extensions,
      digestlength=options.digestlength,
      hashfun=options.hashfun,
      keep_dirs=options.keep_dirs,
    ).run()

if __name__ == '__main__':
    main(sys.argv[1:])
