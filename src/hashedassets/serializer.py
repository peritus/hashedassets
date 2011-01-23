#!/usr/bin/env python

from re import split as re_split

SERIALIZERS = {}

class SimpleSerializer(object):
    @classmethod
    def serialize(cls, items, _):
        return "\n".join([
            "%s: %s" % item
            for item
            in list(items.items())]) + "\n"

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
                in list(items.items())]) +
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
        for key, value in list(cls.REPLACEMENTS.items()):
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
            in list(items.items())]) + '\n'

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

