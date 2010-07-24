#!/usr/bin/env

from base64 import urlsafe_b64encode
from glob import glob
from optparse import OptionParser
from os import remove, mkdir, walk
from os.path import getmtime, join, exists, isdir, relpath,\
                    splitext, normpath, dirname, commonprefix
from shutil import copy
from signal import signal, SIGTERM, SIGHUP
from sys import exit
from time import sleep
from itertools import chain

try:
    # Python 2.5
    from hashlib import sha1
except ImportError:
    # Python 2.4
    from sha import sha as sha1

SERIALIZERS = {}

def _simple_serialize(map):
    return "\n".join(["%s: %s" % item for item in map.iteritems()]) + "\n"

SERIALIZERS['.txt'] = (_simple_serialize, None)

try:
    from json import loads, dumps
except ImportError:
    try:
        from simplejson import loads, dumps
    except ImportError:
        loads, dumps = (None, None)

if loads and dumps:
    SERIALIZERS['.json'] = (dumps, loads)

    SERIALIZERS['.js'] = (
            lambda s: "var hashedassets = " + dumps(s) + ";",
            lambda s: s[s.find("=")+1:],
            )

    SERIALIZERS['.jsonp'] = (
            lambda s: "hashedassets(" + dumps(s) + ");",
            lambda s: s[s.find("(")+1:s.rfind(")")],
            )

class SassSerializer(object):
    PREAMBLE = (
    '@mixin hashedassets($directive, $path) {\n'
    '         @'
    )

    ENTRY = (
    'if $path == "%s" { #{$directive}: url("%s"); }\n'
    '    @else '
    )

    EPILOQUE = (
    '{\n'
    '      @warn "Did not find "#{$path}" in list of assets";\n'
    '      #{$directive}: url($path);\n'
    '    }\n'
    '}'
    )

    @classmethod
    def serialize(cls, items):
        return (
            cls.PREAMBLE + "".join([
                cls.ENTRY % item
                for item
                in items.iteritems()
                ]) +
            cls.EPILOQUE
            )

SERIALIZERS['.scss'] = (SassSerializer.serialize, None)

class PHPSerializer(SassSerializer):
    PREAMBLE = '$hashedassets = array(\n'
    ENTRY = '  "%s" => "%s",\n'
    EPILOQUE = ')'

SERIALIZERS['.php'] = (PHPSerializer.serialize, None)

class AssetHasher(object):
    hashfun = sha1
    digestlength = 9999 # "don't truncate"

    def __init__(self, files, output_dir, map_filename=None):
        self._hash_map = {} # actually, a map for hashes
        self.output_dir = output_dir

        if not map_filename:
            map_filename = join(self.output_dir, "hashedassets.txt")

        self.files = chain.from_iterable([glob(path) for path in files])
        self.input_dir = dirname(commonprefix(files))


        self.map_filename = map_filename

    @classmethod
    def digest(cls, content):
        return urlsafe_b64encode(cls.hashfun(content).digest()[:cls.digestlength]).strip("=")

    def process_file(self, filename):
        _, extension = splitext(filename)

        hashed_filename = self.digest(open(filename).read())

        if extension:
            hashed_filename = "%s%s" % (hashed_filename, extension)

        mtime = getmtime(filename)
        hashed_filename = join(self.output_dir, hashed_filename)

        try:
            old_hashed_filename, old_mtime = self._hash_map[filename]
            if(hashed_filename == old_hashed_filename):
                return

            print "rm '%s'" % old_hashed_filename
            remove(old_hashed_filename)
        except KeyError: # file not under surveillance
            pass

        self._hash_map[relpath(filename, self.input_dir)] = \
            (relpath(hashed_filename, self.output_dir), mtime)

        copy(filename, hashed_filename)
        print "cp '%s' '%s'"  % (filename, hashed_filename)

    def process_all_files(self):
        for file in self.files:
            self.process_file(file)

    def read_map(self):
        pass

    def write_map(self):
        _, map_ext = splitext(self.map_filename)
        serialize, _ = SERIALIZERS[map_ext]
        with open(self.map_filename, "w") as file:
            file.write(serialize(dict(
                (filename, hashed_filename_mtime[0])
                for filename, hashed_filename_mtime
                in self._hash_map.iteritems()
            )))

    def run(self):
        self.read_map()
        self.process_all_files()
        self.write_map()

def main():
    parser = OptionParser(usage="%prog [ -m MAPFILE ] SOURCE [...] DEST")
    parser.add_option("-m", "--map-file", dest="map_filename", type="string",
                  help="Write from-to-map", metavar="MAPFILE")

    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.error("You need to specify at least one file and a destination directory")

    output_dir = normpath(args[-1])
    files = args[:-1]

    if not exists(output_dir):
        mkdir(output_dir)
        print "mkdir '%s'" % output_dir
    elif not isdir(output_dir):
        parser.error("Output dir at '%s' is not a directory" % output_dir)

    AssetHasher(
      files=files,
      output_dir=output_dir,
      map_filename=options.map_filename,
    ).run()

if __name__ == '__main__':
    main()
