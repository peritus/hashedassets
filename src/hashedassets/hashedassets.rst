
.. contents:: Table of Contents

Creating some source files
--------------------------

For this demo, we'll create a few directories, one for the maps to live, one
for the input files:

>>> system("mkdir maps/")
>>> system("mkdir -p input/subdir/2nd/")

We also create files that live in a sub- and subsubdirectories:

>>> write("input/foo.txt", "foo")
>>> write("input/subdir/bar.txt", "bar")
>>> write("input/subdir/2nd/baz.txt", "foofoofoo")

Simple usage
------------

>>> system("hashedassets -v maps/map.txt input/*.txt input/*/*.txt output/")
mkdir 'output'
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> system("ls maps/")
map.txt

>>> print(open("maps/map.txt").read())
foo.txt: C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
subdir/bar.txt: Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt
<BLANKLINE>

>>> system("ls output/")
C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt

Modification time is also preserved:

>>> old_stat = os.stat("input/foo.txt")
>>> new_stat = os.stat("output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt")
>>> [(getattr(old_stat, prop) == getattr(new_stat, prop))
...   for prop in ('st_mtime', 'st_atime', 'st_ino',)]
[True, True, False]

If you specify a directory as source, all files and subdirectories will be processed:

>>> system("hashedassets -v maps/dirmap.txt input/ output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'
cp 'input/subdir/2nd/baz.txt' 'output/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt'

>>> system("rm output/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt")


Output formats
--------------

We can easily do this with multiple formats:

Sed
+++

This generates a sed script that does the replacements for us:

>>> system("hashedassets -v -n my_callback maps/map.sed input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print(open("maps/map.sed").read())
s/foo\.txt/C-7Hteo_D9vJXQ3UfzxbwnXaijM\.txt/g
s/subdir\/bar\.txt/Ys23Ag_5IOWqZCw9QGaVDdHwH00\.txt/g
<BLANKLINE>

We should be able to use this with sed on this file:

>>> write("replaceme.html", "<a href=foo.txt>bar</a>")

The script is then applied like this:

>>> system("sed -f maps/map.sed replaceme.html")
<a href=C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt>bar</a>

Note '.' is not treated as wildcard, so the following does not work

>>> write("replaceme2.html", "<a href=fooAtxt>bar</a>")
>>> system("sed -f maps/map.sed replaceme2.html")
<a href=fooAtxt>bar</a>

JavaScript
++++++++++

>>> system("hashedassets -v -n my_callback maps/map.js input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print(open("maps/map.js").read())
var my_callback = {
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
};

JSON
++++

>>> system("hashedassets -v -n my_callback maps/map.json input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print(open("maps/map.json").read())
{
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
}

JSONP
+++++

>>> system("hashedassets -v -n my_callback maps/map.jsonp input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print(open("maps/map.jsonp").read())
my_callback({
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
});

SCSS
++++

`Sass <http://sass-lang.com/>`__ ("Syntactically Awesome Stylesheets") is a meta language on top of CSS.

>>> system("hashedassets -v -n my_callback maps/map.scss input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print(open("maps/map.scss").read())
@mixin my_callback($directive, $path) {
         @if $path == "foo.txt" { #{$directive}: url("C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt"); }
    @else if $path == "subdir/bar.txt" { #{$directive}: url("Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"); }
    @else {
      @warn "Did not find "#{$path}" in list of assets";
      #{$directive}: url($path);
    }
}

PHP
+++

>>> system("hashedassets -v -n my_callback maps/map.php input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print(open("maps/map.php").read())
$my_callback = array(
  "foo.txt" => "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt" => "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt",
)


Options
-------

Specifying the type with -t
+++++++++++++++++++++++++++

The type of the map is guessed from the filename, but you can specify it as
well:

>>> system("hashedassets -v -t js cantguessmaptype input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

Specifying the length of the filename with -l
+++++++++++++++++++++++++++++++++++++++++++++

>>> system("hashedassets -v -l 10 maps/shortmap.json input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IO.txt'

>>> system("rm output/C-7Hteo_D9.txt output/Ys23Ag_5IO.txt")

Specifying the digest with -d
+++++++++++++++++++++++++++++

Hashedassets uses sha1 by default to hash the input files. You can change that
with the -d command line parameter, e.g. by specifying -d md5 to use the md5
digest method.

>>> system("hashedassets -v -d md5 maps/md5map.json input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/rL0Y20zC-Fzt72VPzMSk2A.txt'
cp 'input/subdir/bar.txt' 'output/N7UdGUp1E-RbVvZSTy1R8g.txt'

>>> system("rm output/rL0Y20zC-Fzt72VPzMSk2A.txt output/N7UdGUp1E-RbVvZSTy1R8g.txt")

Keep the directory structure with --keep-dirs
+++++++++++++++++++++++++++++++++++++++++++++

By default hashedassets copies all output files into the root level of the
output dir. You can turn this off, with the ''--keep-dirs'' option:

>>> system("hashedassets -v --keep-dirs maps/preserve.json input/*.txt input/*/*.txt input/*/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
mkdir -p output/subdir
cp 'input/subdir/bar.txt' 'output/subdir/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'
mkdir -p output/subdir/2nd
cp 'input/subdir/2nd/baz.txt' 'output/subdir/2nd/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt'

>>> system("rm -r output/subdir/")

Don't move anything with --map-only
+++++++++++++++++++++++++++++++++++

If you specify ''--map-only'', the program will create a map but it won't move
any files. This is useful, if you want to use the hashed name as part of the
path ('''http://static.example.com/aYs23A/subdir/bar.txt''') that is dropped by
the webserver during url rewriting.

>>> system("hashedassets -v --map-only maps/maponly.txt input/*.txt")
>>> print(open('maps/maponly.txt').read())
foo.txt: C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
<BLANKLINE>

Don't map anything with --identity
++++++++++++++++++++++++++++++++++

If you specify ''--identity'' the program will create a map that maps every
file to itself, similar to how the `identity function
<http://en.wikipedia.org/wiki/Identity_function>`__ is defined. You can use
this if you want to disable hashedassets temporarily, but don't want to alter
your build script heavily:

>>> system("hashedassets -v --identity maps/identitymap.json input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/foo.txt'
mkdir -p output/subdir
cp 'input/subdir/bar.txt' 'output/subdir/bar.txt'

>>> print(open('maps/identitymap.json').read())
{
  "foo.txt": "foo.txt",
  "subdir/bar.txt": "subdir/bar.txt"
}

If you switch --identity off, all identity files get deleted:

>>> system("hashedassets -v maps/identitymap.json input/*.txt input/*/*.txt output/")
rm 'output/foo.txt'
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
rm 'output/subdir/bar.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print(open('maps/identitymap.json').read())
{
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
}

>>> system("rm -r output/subdir/")

Strip file extensions with --strip-extensions
+++++++++++++++++++++++++++++++++++++++++++++

If you want to strip the file extensions of the resulting hashed files, this
option is for you! This is particularly useful in combination with the
''--map-only'' option with the hashed name becoming part of the path of the url.

>>> system("hashedassets -v --strip-extensions maps/noextensions.json input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00'

>>> print(open('maps/noextensions.json').read())
{
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00"
}

>>> system("rm -r output/C-7Hteo_D9vJXQ3UfzxbwnXaijM output/Ys23Ag_5IOWqZCw9QGaVDdHwH00")

Verbose mode with -v
++++++++++++++++++++

Usually the program does not print anything if it everything works as expected:

>>> system("hashedassets maps/map2.txt input/*.txt input/*/*.txt output/")

You can tell the program to log more information (using ``-v``), optionally
multiple times to see what's going on inside:

>>> system("hashedassets -v maps/map3.txt input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

Exclude files with --exclude
++++++++++++++++++++++++++++

You can exclude dirs and files from being hashed, using the ``--exclude``
option, both using patterns and directories:

>>> system("hashedassets -v maps/xmap.txt --exclude input/*/2nd input/ output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> system("hashedassets -v maps/xmap2.txt --exclude input/subdir/ input/ output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'

>>> system("hashedassets -v maps/xmap3.txt --exclude input/subdir/2nd/baz.txt input/ output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

Relative paths with --reference
+++++++++++++++++++++++++++++++

If you need all paths relative to a specific file or directory, ``--reference`` is your friend:

>>> system("hashedassets -v --keep-dirs --reference=output/subdir/style.css maps/refmap.txt input/ output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
mkdir -p output/subdir
cp 'input/subdir/bar.txt' 'output/subdir/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'
mkdir -p output/subdir/2nd
cp 'input/subdir/2nd/baz.txt' 'output/subdir/2nd/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt'

>>> print(open('maps/refmap.txt').read())
../foo.txt: ../C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
bar.txt: Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt
2nd/baz.txt: 2nd/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt

If we execute this again, there is no work to do:

>>> system("hashedassets -v --keep-dirs --reference=output/subdir/ maps/refmap.txt input/ output/")
>>> system("rm -r output/subdir/")

Advanced usage
--------------

Writing the map to stdout
+++++++++++++++++++++++++

>>> system("hashedassets --map-type=txt - input/*.txt input/*/*.txt output/")
foo.txt: C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
subdir/bar.txt: Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt
<BLANKLINE>


Re-using a map
++++++++++++++

The program reads in maps it created in a prior run to only copy files that
haven't changed since. So, the following commands do not copy any files:

>>> system("hashedassets -v maps/map.scss input/*.txt input/*/*.txt output/")
>>> system("hashedassets -v maps/map.php input/*.txt input/*/*.txt output/")
>>> system("hashedassets -v maps/map.js input/*.txt input/*/*.txt output/")
>>> system("hashedassets -v maps/map.json input/*.txt input/*/*.txt output/")
>>> system("hashedassets -v maps/map.sed input/*.txt input/*/*.txt output/")
>>> system("hashedassets -v maps/map.jsonp input/*.txt input/*/*.txt output/")
>>> system("hashedassets -v maps/map.txt input/*.txt input/*/*.txt output/")

If we touch one of the input files in between, the file will be read but not
copied because the hashsum is the same:

>>> system('touch -t200504072214.12 input/foo.txt')
>>> system("hashedassets -v maps/map.json input/*.txt input/*/*.txt output/")

If we change the file's content, it will get a new name:

>>> write("input/foo.txt", "foofoo")

Then try again:

>>> system("hashedassets -v maps/map.json input/*.txt input/*/*.txt output/")
rm 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/foo.txt' 'output/QIDaFD7KLKQh0l5O6b8exdew3b0.txt'

If you then list the files in the directory, note that the old file
''output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'' is gone:

>>> system("ls output/")
QIDaFD7KLKQh0l5O6b8exdew3b0.txt
Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt

If we remove one of the created files, it gets recreated:

>>> system("rm output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt")
>>> system("hashedassets -v maps/map.json input/*.txt input/*/*.txt output/")
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> system("ls output/")
QIDaFD7KLKQh0l5O6b8exdew3b0.txt
Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt

If a file that is about to be removed because the original content changed, it
isn't recreated:

>>> system("rm output/QIDaFD7KLKQh0l5O6b8exdew3b0.txt")
>>> write("input/foo.txt", "foofoofoo")
>>> system("hashedassets -v maps/map.json input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt'

Using the same directory for SOURCE and DEST
++++++++++++++++++++++++++++++++++++++++++++

This works as well:

>>> system("hashedassets -v maps/samedir.json input/*.txt input/")
cp 'input/foo.txt' 'input/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt'

Even after the command is invoked a second time:

>>> system("hashedassets -v maps/samedir.json input/*.txt input/")

Notice, that the mapfile does not contain the self-reference:

>>> print(open("maps/samedir.json").read())
{
  "foo.txt": "NdbmnXyjdY2paFzlDw9aJzCKH9w.txt"
}

>>> write("input/foo.txt", "barbarbar")
>>> system("hashedassets -v maps/samedir.json input/*.txt input/")
rm 'input/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt'
cp 'input/foo.txt' 'input/sWL19addVG2KRYJ02EDKXF4Oh8s.txt'

