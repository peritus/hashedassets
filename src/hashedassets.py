#!/usr/bin/env

import threading
from os.path import getmtime, join
from os import remove
from shutil import copy
from base64 import urlsafe_b64encode
from fsevents import Observer, Stream, \
    IN_MODIFY, IN_ATTRIB, IN_CREATE, \
    IN_DELETE, IN_MOVED_FROM, IN_MOVED_TO

try:
    # Python 2.5
    from hashlib import sha1
except ImportError:
    # Python 2.4
    from sha import sha as sha1

class AssetHasher(threading.Thread):

    hashfun = sha1
    digestlength = 9999 # all letters

    def __init__(self, input_dir, output_dir, pattern):
        threading.Thread.__init__(self)

        self._hash_map = {} # actually, a map for hashes

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.observer = Observer()

        self.stream = Stream(self.file_event, input_dir, file_events=True)
        self.observer.schedule(self.stream)

    @classmethod
    def digest(cls, content):
        return urlsafe_b64encode(cls.hashfun(content).digest()[:cls.digestlength]).strip("=")

    def process_file(self, filename, moved=False):

        if filename.find(".") == -1:
            extension = ""
        else:
            extension = filename.split(".")[-1]

        hashed_filename = self.digest(open(filename).read())

        if extension:
            hashed_filename = "%s.%s" % (hashed_filename, extension)

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

        self._hash_map[filename] = (hashed_filename, mtime)
        copy(filename, hashed_filename)
        print "cp '%s' '%s'"  % (filename, hashed_filename)

    def file_event(self, event):
        if event.mask in (IN_MODIFY, IN_ATTRIB, IN_CREATE):
            self.process_file(event.name)
        if event.mask == IN_MOVED_FROM:
            self.process_file(event.name, moved=True)
        elif event.mask == IN_DELETE:
            del self._hash_map[event.name]

    def stop(self):
        self.observer.unschedule(self.stream)
        self.observer.stop()

    def run(self):
        print "Observing", self.input_dir
        self.observer.start()
        self.observer.join()

def main():
    from optparse import OptionParser
    from signal import signal, SIGTERM, SIGHUP
    from time import sleep

    parser = OptionParser(usage="%prog -i DIR -o DIR")
    parser.add_option("-i", "--input-dir", dest="input_dir", type="string",
                  help="Where to look for input", metavar="DIR")
    parser.add_option("-o", "--output-dir", dest="output_dir", type="string",
                  help="Where to write", metavar="DIR")

    (options, args) = parser.parse_args()

    if len(args) == 2:
        (options.input_dir, options.output_dir) = args

    if options.input_dir == None or options.output_dir == None:
        parser.error("-i and -o are required")

    from os.path import isdir

    if not isdir(options.input_dir):
        parser.error("Input dir at '%s' does not exists or is not a directory")

    if not isdir(options.output_dir):
        parser.error("Output dir at '%s' does not exists or is not a directory")

    ah = AssetHasher(
            input_dir=options.input_dir,
            output_dir=options.output_dir,
            pattern=[]
    )

    ah.start()

    signal(SIGTERM, ah.stop)
    signal(SIGHUP, ah.stop)

    try:
        while True:
            sleep(1000)
    except KeyboardInterrupt:
        print "Shut down"
        ah.stop()

if __name__ == '__main__':
    main()
