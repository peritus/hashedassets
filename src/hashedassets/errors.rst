Error handling
--------------

If try to use the software with no arguments the user is reminded to specify at
least the mapfile, the source and the destination directory:

>>> system("hashedassets", external=True)
Usage: hashedassets [ options ] MAPFILE SOURCE [...] DEST
<BLANKLINE>
hashedassets: error: You need to specify at least MAPFILE SOURCE and DEST

If the user specifies the --help option, detailed usage information is shown:

>>> system("hashedassets --help", external=True)
Usage: hashedassets [ options ] MAPFILE SOURCE [...] DEST
<BLANKLINE>
Version: ...
<BLANKLINE>
Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -v, --verbose         increase verbosity level
  -q, --quiet           don't print status messages to stdout
  -n MAPNAME, --map-name=MAPNAME
                        name of the map [default: hashedassets]
  -t MAPTYPE, --map-type=MAPTYPE
                        type of the map. one of scss, php, js, json, sed,
                        jsonp, txt [default: guessed from MAPFILE]
  -l LENGTH, --digest-length=LENGTH
                        length of the generated filenames (without extension)
                        [default: 27]
  -d HASHFUN, --digest=HASHFUN
                        hash function to use. One of sha1, md5
                        [default: sha1]
  -k, --keep-dirs       Mirror SOURCE dir structure to DEST [default: false]
  -i, --identity        Don't actually map, keep all file names
  -o, --map-only        Don't move files, only generate a map

Generating maps with unguessable and unspecified types throw errors:

>>> system("hashedassets unguessable doesnot matter", external=True)
Usage: hashedassets [ options ] MAPFILE SOURCE [...] DEST
<BLANKLINE>
hashedassets: error: Invalid map type: ''

>>> system("hashedassets unguessable.withextension doesnot matter", external=True)
Usage: hashedassets [ options ] MAPFILE SOURCE [...] DEST
<BLANKLINE>
hashedassets: error: Invalid map type: 'withextension'
