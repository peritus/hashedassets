
import logging
logger = logging.getLogger("hashedassets.map")

from os import walk
from glob import glob
from itertools import chain
from os.path import join, exists, isdir, relpath, \
    dirname, commonprefix

from hashedassets.serializer import SERIALIZERS
import sys
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

            globfiles = [globfile for globfile in globfiles if globfile not in evicts]

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
