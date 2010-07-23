#!/usr/bin/env

from base64 import urlsafe_b64encode
from optparse import OptionParser
from os import remove, mkdir, walk
from os.path import getmtime, join, exists, isdir, relpath, splitext
from shutil import copy
from signal import signal, SIGTERM, SIGHUP
from time import sleep

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
    '    @'
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

    def __init__(self, input_dir, output_dir, map_filename=None):
        self._hash_map = {} # actually, a map for hashes
        self.input_dir = input_dir
        self.output_dir = output_dir

        if not map_filename:
            map_filename = join(self.output_dir, "hashedassets.map")


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
        for pos, dirs, files in walk(self.input_dir):
            for file in files:
                self.process_file(join(pos, file))

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
    parser = OptionParser(usage="%prog -i DIR -o DIR -m MAPFILE")
    parser.add_option("-i", "--input-dir", dest="input_dir", type="string",
                  help="Where to look for input", metavar="DIR")
    parser.add_option("-o", "--output-dir", dest="output_dir", type="string",
                  help="Where to write", metavar="DIR")
    parser.add_option("-m", "--map-file", dest="map_filename", type="string",
                  help="Write from-to-map", metavar="MAPFILE")

    (options, args) = parser.parse_args()

    if len(args) == 2:
        (options.input_dir, options.output_dir) = args

    if options.input_dir == None or options.output_dir == None:
        parser.error("-i and -o are required")

    if not isdir(options.input_dir):
        parser.error("Input dir at '%s' does not exists or is not a directory" % options.input_dir)

    if not exists(options.output_dir):
        mkdir(options.output_dir)
        print "mkdir '%s'" % options.output_dir
    elif not isdir(options.output_dir):
        parser.error("Output dir at '%s' is not a directory" % options.output_dir)

    AssetHasher(
      input_dir=options.input_dir,
      output_dir=options.output_dir,
      map_filename=options.map_filename,
    ).run()

if __name__ == '__main__':
    main()
