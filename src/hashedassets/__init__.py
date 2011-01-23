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


class AssetHasher(object):
    def __init__(self, files, output_dir, map_filename, map_name, map_type, rewritestring, map_only=False, reference=None):
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

        relative_files = [relpath(path, self.basedir) for path in chain.from_iterable(list(map(glob, files)))]

        logger.debug('Relative files: %s', relative_files)

        for file_or_dir in relative_files:
            for walkroot, _, walkfiles in walk(join(self.basedir, file_or_dir)):
                for walkfile in walkfiles:
                    relative_files.append(normpath(join(relpath(walkroot, self.basedir), walkfile)))

        logger.debug('Resolved subdir files: %s', relative_files)

        self.files = OrderedDict.fromkeys(relative_files)

        logger.debug("Initialized map, is now %s", self.files)

        self.map_filename = map_filename
        self.map_name = map_name
        self.map_type = map_type
        self.map_only = map_only

        if not reference:
            self.refdir = self.output_dir
        elif not isdir(reference):
            self.refdir = dirname(reference)
        else:
            self.refdir = reference

        self.rewritestring = rewritestring

    def process_file(self, filename):
        logger.debug("Processing file '%s'", filename)

        try:
            hashed_filename = self.rewritestring % Rewriter(
              filename, self.basedir)
        except IOError as e:
            logger.debug("'%s' does not exist, can't be hashed", filename, exc_info=e)
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


        infile = join(self.basedir, filename).replace('/./', '/')
        outfile = join(self.output_dir, hashed_filename).replace('/./', '/')

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
            logger.info("mkdir -p %s" % join(self.output_dir, create_dir))
            makedirs(join(self.output_dir, create_dir))

            # try again
            copy2(infile, outfile)

        self.files[filename] = hashed_filename

        if not self.map_only:
            logger.info("cp '%s' '%s'", infile, outfile)

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

        for filename, hashed_filename in list(deserialized.items()):
            hashed_filename = relpath(join(self.refdir, hashed_filename), self.output_dir)
            filename = relpath(join(self.refdir, filename), self.output_dir)
            self.files[filename] = hashed_filename

        logger.debug("Read map, is now: %s", self.files)

    def write_map(self):
        if not self.map_filename:
            return

        newmap = OrderedDict()

        for origin, target in list(self.files.items()):
            if target != None:
                origin = relpath(join(self.output_dir, origin), self.refdir)
                target = relpath(join(self.output_dir, target), self.refdir)
                newmap[origin] = target

        serialized = SERIALIZERS[self.map_type].serialize(newmap, self.map_name)

        if self.map_filename == '-':
            outfile = sys.stdout
        else:
            outfile = open(self.map_filename, 'w')

        outfile.write(serialized)

        if self.map_filename != '-':
            outfile.close()

    def run(self):
        self.read_map()
        self.process_all_files()
        self.write_map()

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
      dest="map_type",
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

    if not options.map_type and map_filename:
        options.map_type = splitext(map_filename)[1].lstrip(".")

    if not options.map_type in list(SERIALIZERS.keys()):
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


    rewritestring = Rewriter.compute_rewritestring(options.strip_extensions, options.digestlength, options.keep_dirs, options.hashfun)

    AssetHasher(
      files=files,
      output_dir=output_dir,
      map_filename=map_filename,
      map_name=options.map_name,
      map_type=options.map_type,
      map_only=options.map_only,
      rewritestring=rewritestring,
      reference=options.reference,
    ).run()

if __name__ == '__main__':
    main(sys.argv[1:])
