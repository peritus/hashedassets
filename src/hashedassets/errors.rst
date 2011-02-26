Error handling
--------------

If try to use the software with no arguments the user is reminded to specify at
least the mapfile, the source and the destination directory:

>>> system("hashedassets", external=True)
Usage: ... [ options ] MAPFILE SOURCE [...] DEST
<BLANKLINE>
...: error: You need to specify at least MAPFILE, SOURCE and DEST

If the user specifies the --help option, detailed usage information is shown:

>>> system("hashedassets --help", external=True)
Usage: ... [ options ] MAPFILE SOURCE [...] DEST
<BLANKLINE>
Version: v... (Python ...)
<BLANKLINE>
Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -v, --verbose         increase verbosity level
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
  -s, --strip-extensions
                        Strip the file extensions from the hashed files
  --reference=REFERENCE
                        Paths in map will be relative to this directory
  -x EXCLUDES, --exclude=EXCLUDES
                        Excludes these files in the input directory

Generating maps with unguessable and unspecified types throw errors:

>>> system("hashedassets unguessable doesnot matter", external=True)
Usage: ... [ options ] MAPFILE SOURCE [...] DEST
<BLANKLINE>
...: error: Invalid map type: ''

>>> system("hashedassets unguessable.withextension doesnot matter", external=True)
Usage: ... [ options ] MAPFILE SOURCE [...] DEST
<BLANKLINE>
...: error: Invalid map type: 'withextension'
