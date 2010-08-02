#!/usr/bin/env

from base64 import urlsafe_b64encode
from glob import glob
from optparse import OptionParser
from os import remove, mkdir, walk, stat
from os.path import getmtime, join, exists, isdir, relpath,\
                    splitext, normpath, dirname, commonprefix
from re import split as re_split
from shutil import copy2
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

class SimpleSerializer(object):
    @classmethod
    def serialize(cls, items, _):
        return "\n".join(["%s: %s" % item for item in items.iteritems()]) + "\n"

    @classmethod
    def deserialize(cls, string):
        map = {}
        for line in string.split("\n"):
            if line == '':
                continue
            key, value = line.split(":")
            map[key.strip()] = value.strip()
        return map

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
                    'dump': dumps(items, sort_keys=True, indent=2)
                    }

        @classmethod
        def deserialize(cls, string):
            return loads(string[string.index("(")+1:string.rfind(")")])

    SERIALIZERS['jsonp'] = JSONPSerializer

    class JavaScriptSerializer(object):
        @classmethod
        def serialize(cls, items, map_name):
            return ("var %s = " % map_name) + dumps(items, sort_keys=True, indent=2) + ";"

        @classmethod
        def deserialize(cls, string):
            return loads(string[string.index("=")+1:string.rfind(";")])

    SERIALIZERS['js'] = JavaScriptSerializer

class PreambleEntryEpiloqueSerializer(object):
    @classmethod
    def serialize(cls, items, map_name):
        return (
            (cls.PREAMBLE % map_name) + "".join([
                cls.ENTRY % item
                for item
                in items.iteritems()
                ]) +
            cls.EPILOQUE
            )

class SassSerializer(PreambleEntryEpiloqueSerializer):
    PREAMBLE = (
    '@mixin %s($directive, $path) {\n'
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
    def deserialize(cls, string):
        map = {}
        for line in string.split(";")[:-3]:
            _, key, _, value, _ = line.split('"')
            map[key] = value
        return map

SERIALIZERS['scss'] = SassSerializer

class PHPSerializer(PreambleEntryEpiloqueSerializer):
    PREAMBLE = '$%s = array(\n'
    ENTRY = '  "%s" => "%s",\n'
    EPILOQUE = ')'

    @classmethod
    def deserialize(cls, string):
        map = {}
        for line in string.split("\n")[1:-1]:
            _, key, _, value, _ = line.split('"')
            map[key] = value
        return map

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
            if reverse: key, value = value, key
            filename = filename.replace(key, value)
        return filename

    @classmethod
    def serialize(cls, items, map_name):
        return "\n".join([
            (cls.ENTRY % (cls._escape_filename(key),
                cls._escape_filename(value)))
            for key, value
            in items.iteritems()
            ]) + '\n'

    @classmethod
    def deserialize(cls, string):
        map = {}
        for line in string.split("\n"):
            if line == '':
                continue

            _, key, value, _ = re_split("(?<=[^\\\])/", line)
            key = cls._escape_filename(key.strip(), True)
            value = cls._escape_filename(value.strip(), True)
            map[key] = value
        return map

SERIALIZERS['sed'] = SedSerializer

class AssetHasher(object):
    hashfun = sha1
    digestlength = 9999 # "don't truncate"

    def __init__(self, files, output_dir, map_filename, map_name, map_type):
        self._hash_map = {} # actually, a map for hashes

        if not map_type and map_filename:
            map_type = splitext(map_filename)[1].lstrip(".")

        self.output_dir = output_dir
        self.map_filename = map_filename
        self.map_name = map_name
        self.map_type = map_type
        self.files = chain.from_iterable([glob(path) for path in files])
        self.input_dir = dirname(commonprefix(files))

    @classmethod
    def digest(cls, content):
        return urlsafe_b64encode(cls.hashfun(content).digest()[:cls.digestlength]).strip("=")

    def process_file(self, filename):
        # hash the file
        _, extension = splitext(filename)

        hashed_filename = self.digest(open(filename).read())

        if extension:
            hashed_filename = "%s%s" % (hashed_filename, extension)

        mtime = getmtime(filename)
        hashed_filename = join(self.output_dir, hashed_filename)

        map_key = relpath(filename, self.input_dir)
        map_value = relpath(hashed_filename, self.output_dir)

        if map_key in self._hash_map:
            old_hashed_filename, old_mtime = self._hash_map[map_key]
            old_hashed_filename = join(self.output_dir, old_hashed_filename)

            if(hashed_filename == old_hashed_filename):
                return

            remove(old_hashed_filename)
            print "rm '%s'" % old_hashed_filename
            del self._hash_map[map_key]

        # no work to do
        if map_key in self._hash_map:
            return

        # actually copy the file
        self._hash_map[map_key] = (map_value, mtime)
        copy2(filename, hashed_filename)
        print "cp '%s' '%s'"  % (filename, hashed_filename)

    def process_all_files(self):
        for file in self.files:
            self.process_file(file)

    def read_map(self):
        if not self.map_filename:
            return

        if not exists(self.map_filename):
            return

        content = open(self.map_filename).read()

        deserialized = SERIALIZERS[self.map_type].deserialize(content)

        self._hash_map = dict(
            (filename, (hashed_filename, stat(join(self.output_dir, hashed_filename)).st_mtime))
            for filename, hashed_filename
            in deserialized.iteritems()
        )

    def write_map(self):
        if not self.map_filename:
            return

        items = dict(
                  (filename, hashed_filename_mtime[0])
                  for filename, hashed_filename_mtime
                  in self._hash_map.iteritems()
                )

        serialized = SERIALIZERS[self.map_type].serialize(items, self.map_name)

        with open(self.map_filename, "w") as file:
            file.write(serialized)

    def run(self):
        self.read_map()
        self.process_all_files()
        self.write_map()

def main():
    parser = OptionParser(usage=
            "%prog [ -m MAPFILE [-t MAPTYPE] [-n MAPNAME]] SOURCE [...] DEST")
    parser.add_option("-m", "--map-file", dest="map_filename", type="string",
                  help="Write from-to-map", metavar="MAPFILE")
    parser.add_option("-n", "--map-name", dest="map_name", type="string",
                  help="Name of the map [default: %default]", metavar="MAPNAME",
                  default="hashedassets")
    parser.add_option("-t", "--map-type", dest="map_type", type="choice",
                  help="One of " +
                       ", ".join(SERIALIZERS.keys()) +
                       " [default: guessed from MAPFILE]", metavar="MAPTYPE",
                  choices=SERIALIZERS.keys())

    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.error("You need to specify at least one file and a destination directory")

    if options.map_name and \
        parser.defaults['map_name'] != options.map_name and\
        not options.map_filename:
        parser.error("-n without -m does not make sense. Use -m to specify a map filename")

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
      map_name=options.map_name,
      map_type=options.map_type,
    ).run()

if __name__ == '__main__':
    main()
