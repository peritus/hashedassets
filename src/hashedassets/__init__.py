#!/usr/bin/env python

'''
A command line tool that copies files to filenames based on their contents. It
also writes a map of what was renamed to what, so you can find your files.

Main purpose of this is that you can `add a far future Expires header to your
components <http://stevesouders.com/hpws/rule-expires.php>`__. Using hash based
filenames is a lot better than using your $VCS revision number, because users
only need to download files that didn't change.

'''

from hashedassets.rewrite import Rewriter
from hashedassets.serializer import SERIALIZERS

import logging
from glob import glob
from optparse import OptionParser
from os import remove, mkdir, makedirs, listdir, walk
from os.path import join, exists, isdir, relpath, \
                    splitext, normpath, dirname, commonprefix, \
                    split as path_split, samefile, abspath
from re import split as re_split
from shutil import copy2, Error as shutil_Error
import sys
from itertools import chain
import fnmatch

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


class AssetMap(object):
    def __init__(self, files, output_dir, name, format, reference, excludes):
        logger.debug('Incoming files: %s', files)

        basedir = commonprefix(files)
        logger.debug('Prefix is "%s"', basedir)

        if isdir(basedir):
            self.basedir = basedir
        else:
            self.basedir = dirname(basedir)

        logger.debug('Basedir is "%s"', self.basedir)

        self.output_dir = output_dir
        logger.debug('Output dir is "%s"', self.output_dir)

        globfiles = list(chain.from_iterable(list(map(glob, files))))

        logger.debug("Globfiles: %s", globfiles)

        for file_or_dir in globfiles:
            for walkroot, _, walkfiles in walk(file_or_dir):
                for walkfile in walkfiles:
                    globfiles.append(join(walkroot, walkfile))

        logger.debug('Resolved globfiles: %s', globfiles)

        for exclude in (excludes or []):

            if exclude[-1] is not '*':
                exclude += '*'

            evicts = fnmatch.filter(globfiles, exclude)
            logger.debug("exclude '%s' evicts => %s", exclude, evicts)

            globfiles = [ globfile for globfile in globfiles if globfile not in evicts ]

        relative_files = [
            r for r in [
                relpath(globfile, self.basedir)
                for globfile
                in globfiles
            ]
            if r is not '.'
        ]

        logger.debug('Resolved relative files: %s', relative_files)

        self._files = OrderedDict.fromkeys(relative_files)

        logger.debug("Initialized map, is now %s", self._files)

        self.name = name
        self.format = format

        if not reference:
            self.refdir = self.output_dir
        elif not isdir(reference):
            self.refdir = dirname(reference)
        else:
            self.refdir = reference

    def __setitem__(self, name, item):
        self._files[name] = item

    def __getitem__(self, item):
        return self._files[item]

    def __iter__(self):
        for file in self._files:
            yield file

    def items(self):
        return self._files.items()

    def read(self, filename):
        if not filename:
            return

        if not exists(filename):
            return

        content = open(filename).read()

        deserialized = SERIALIZERS[self.format].deserialize(content)

        for filename, hashed_filename in list(deserialized.items()):
            hashed_filename = relpath(join(self.refdir, hashed_filename), self.output_dir)
            filename = relpath(join(self.refdir, filename), self.output_dir)
            self[filename] = hashed_filename

        logger.debug("Read map, is now: %s", self._files)

    def write(self, filename):
        if not filename:
            return

        newmap = OrderedDict()

        for origin, target in self.items():
            if target != None:
                origin = relpath(join(self.output_dir, origin), self.refdir)
                target = relpath(join(self.output_dir, target), self.refdir)
                newmap[origin] = target

        serialized = SERIALIZERS[self.format].serialize(newmap, self.name)

        if filename == '-':
            outfile = sys.stdout
        else:
            outfile = open(filename, 'w')

        outfile.write(serialized)

        if filename != '-':
            outfile.close()


class AssetHasher(object):
    def __init__(self, assetmap, rewritestring, map_only):
        self.assetmap = assetmap
        self.rewritestring = rewritestring
        self.map_only = map_only

    def process_file(self, filename):
        logger.debug("Processing file '%s'", filename)

        try:
            hashed_filename = self.rewritestring % Rewriter(
              filename, self.assetmap.basedir)
        except IOError as e:
            logger.debug("'%s' does not exist, can't be hashed", filename, exc_info=e)
            return

        logger.debug("Determined new hashed filename: '%s'", hashed_filename)

        if self.assetmap[filename]:
            logger.debug("File has been processed in a previous run (hashed to '%s' then)",
                    self.assetmap[filename])

            outfile = join(self.assetmap.output_dir, self.assetmap[filename])

            if exists(outfile):
                logger.debug("%s still exists", outfile)

                if hashed_filename == self.assetmap[filename]:
                    # skip file
                    logger.debug("Skipping file '%s' -> '%s'", filename, self.assetmap[filename])
                    return

                # remove dangling file
                if not self.map_only:
                    remove(outfile)
                    logger.info("rm '%s'", outfile)


        infile = join(self.assetmap.basedir, filename).replace('/./', '/')
        outfile = join(self.assetmap.output_dir, hashed_filename).replace('/./', '/')

        try:
            if samefile(infile, outfile):
                logger.debug("Won't copy '%s' to itself.", filename)
                return
        except OSError as e:
            if not (e.strerror == 'No such file or directory' and e.filename == outfile):
                assert False,  (dir(e), e.message, e.errno, e.strerror, e.filename)
                raise

        try:
            if not self.map_only:
                copy2(infile, outfile)
        except IOError as e:
            if e.strerror == 'Is a directory':
                return # nothing to copy

            if not e.strerror == 'No such file or directory':
                raise

            # create parent dirs that are needed for the output file
            logger.debug(hashed_filename)
            create_dir, _ = path_split(hashed_filename)
            logger.info("mkdir -p %s" % join(self.assetmap.output_dir, create_dir))
            makedirs(join(self.assetmap.output_dir, create_dir))

            # try again
            copy2(infile, outfile)

        self.assetmap[filename] = hashed_filename

        if not self.map_only:
            logger.info("cp '%s' '%s'", infile, outfile)

    def process_all_files(self):
        for f in self.assetmap:
            self.process_file(f)

    def run(self, filename):
        self.assetmap.read(filename)
        self.process_all_files()
        self.assetmap.write(filename)

def main(args=None):
    if args == None:
        args = sys.argv[1:]

    version = open(join(dirname(__file__), 'RELEASE-VERSION')).read().strip() + \
              ' (Python %d.%d.%d)' % sys.version_info[0:3]

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
      choices=list(SERIALIZERS.keys()),
      dest="map_format",
      help=("type of the map. one of "
          + ", ".join(list(SERIALIZERS.keys()))
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

    parser.add_option(
      "--reference",
      dest="reference",
      default=None,
      type="string",
      help="Paths in map will be relative to this directory",
    )

    parser.add_option(
      "-x",
      "--exclude",
      dest="excludes",
      default=None,
      type="string",
      action="append",
      help="Excludes these files in the input directory",
    )

    (options, args) = parser.parse_args(args)

    if options.identity:
        options.hashfun = 'identity'
        options.keep_dirs = True

    if options.verbosity == None:
        options.verbosity = 0

    if len(logger.handlers) == 0:
        ch = logging.StreamHandler(sys.stderr)
        logger.addHandler(ch)

    log_level = {
        0: logging.ERROR,
        1: logging.INFO,
        2: logging.DEBUG,
    }.get(options.verbosity, logging.DEBUG)
    logger.setLevel(log_level)

    if len(args) < 2 and options.map_only:
        print(args)
        parser.error("In --map-only mode, you need to specify at least MAPFILE and SOURCE")

    if len(args) < 3 and not options.map_only:
        parser.error("You need to specify at least MAPFILE, SOURCE and DEST")

    map_filename = args[0]

    if not options.map_format and map_filename:
        options.map_format = splitext(map_filename)[1].lstrip(".")

    if not options.map_format in list(SERIALIZERS.keys()):
        parser.error("Invalid map type: '%s'" % options.map_format)

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

    rewritestring = Rewriter.compute_rewritestring(options.strip_extensions,
            options.digestlength, options.keep_dirs, options.hashfun)

    assetmap = AssetMap(
      files=files,
      output_dir=output_dir,
      name=options.map_name,
      format=options.map_format,
      reference=options.reference,
      excludes=options.excludes,
    )

    AssetHasher(assetmap, rewritestring, options.map_only).run(map_filename)

if __name__ == '__main__':
    main(sys.argv[1:])
