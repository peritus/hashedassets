
.. contents:: Table of Contents

Creating some source files
--------------------------

For this demo, we'll create a few files that will be used throughout the whole
process:

>>> system("mkdir maps/")

>>> system("mkdir input/")
>>> write("input/foo.txt", "foo")

We also create files that live in a sub- and subsubdirectories:

>>> system("mkdir input/subdir/")
>>> write("input/subdir/bar.txt", "bar")
>>> system("mkdir input/subdir/2nd/")
>>> write("input/subdir/2nd/baz.txt", "foofoofoo")

Simple usage
------------

>>> system("hashedassets maps/map.txt input/*.txt input/*/*.txt output/")
mkdir 'output'
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> system("ls maps/")
map.txt

>>> print open("maps/map.txt").read()
subdir/bar.txt: Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt
foo.txt: C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
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

Output formats
--------------

We can easily do this with multiple formats:

Sed
+++

This generates a sed script that does the replacements for us:

>>> system("hashedassets -n my_callback maps/map.sed input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open("maps/map.sed").read()
s/subdir\/bar\.txt/Ys23Ag_5IOWqZCw9QGaVDdHwH00\.txt/g
s/foo\.txt/C-7Hteo_D9vJXQ3UfzxbwnXaijM\.txt/g
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

>>> system("hashedassets -n my_callback maps/map.js input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open("maps/map.js").read()
var my_callback = {
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
};

JSON
++++

>>> system("hashedassets -n my_callback maps/map.json input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open("maps/map.json").read()
{
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
}

JSONP
+++++

>>> system("hashedassets -n my_callback maps/map.jsonp input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open("maps/map.jsonp").read()
my_callback({
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
});

SCSS
++++

`Sass <http://sass-lang.com/>`__ ("Syntactically Awesome Stylesheets") is a meta language on top of CSS.

>>> system("hashedassets -n my_callback maps/map.scss input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open("maps/map.scss").read()
@mixin my_callback($directive, $path) {
         @if $path == "subdir/bar.txt" { #{$directive}: url("Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"); }
    @else if $path == "foo.txt" { #{$directive}: url("C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt"); }
    @else {
      @warn "Did not find "#{$path}" in list of assets";
      #{$directive}: url($path);
    }
}

PHP
+++

>>> system("hashedassets -n my_callback maps/map.php input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open("maps/map.php").read()
$my_callback = array(
  "subdir/bar.txt" => "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt",
  "foo.txt" => "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
)


Options
-------

Specifying the type with -t
+++++++++++++++++++++++++++

The type of the map is guessed from the filename, but you can specify it as
well:

>>> system("hashedassets -t js cantguessmaptype input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

Specifying the length of the filename with -l
+++++++++++++++++++++++++++++++++++++++++++++

>>> system("hashedassets -l 10 maps/shortmap.json input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IO.txt'

>>> system("rm output/C-7Hteo_D9.txt output/Ys23Ag_5IO.txt")

Specifying the digest with -d
+++++++++++++++++++++++++++++

Hashedassets uses sha1 by default to hash the input files. You can change that
with the -d command line parameter, e.g. by specifying -d md5 to use the md5
digest method.

>>> system("hashedassets -d md5 maps/md5map.json input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/rL0Y20zC-Fzt72VPzMSk2A.txt'
cp 'input/subdir/bar.txt' 'output/N7UdGUp1E-RbVvZSTy1R8g.txt'

>>> system("rm output/rL0Y20zC-Fzt72VPzMSk2A.txt output/N7UdGUp1E-RbVvZSTy1R8g.txt")

Keep the directory structure with --keep-dirs
+++++++++++++++++++++++++++++++++++++++++++++

By default hashedassets copies all output files into the root level of the
output dir. You can turn this off, with the ''--keep-dirs'' option:

>>> system("hashedassets --keep-dirs maps/preserve.json input/*.txt input/*/*.txt input/*/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
mkdir -p output/subdir
cp 'input/subdir/bar.txt' 'output/subdir/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'
mkdir -p output/subdir/2nd
cp 'input/subdir/2nd/baz.txt' 'output/subdir/2nd/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt'

>>> system("rm -r output/subdir/")

Don't map anything with --identity
++++++++++++++++++++++++++++++++++

If you specify ''--identity'' the program will create a map that maps every
file to itself, similar to how the `identity function
<http://en.wikipedia.org/wiki/Identity_function>`__ is defined. You can use
this if you want to disable hashedassets temporarily, but don't want to alter
your build script heavily:

>>> system("hashedassets --identity maps/identitymap.json input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/foo.txt'
mkdir -p output/subdir
cp 'input/subdir/bar.txt' 'output/subdir/bar.txt'

>>> print open('maps/identitymap.json').read()
{
  "foo.txt": "foo.txt",
  "subdir/bar.txt": "subdir/bar.txt"
}

If you switch --identity off, all identity files get deleted:

>>> system("hashedassets maps/identitymap.json input/*.txt input/*/*.txt output/")
rm 'output/foo.txt'
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
rm 'output/subdir/bar.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open('maps/identitymap.json').read()
{
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
}

>>> system("rm -r output/subdir/")

Verbose mode with -v
++++++++++++++++++++

If we tell the command to be quiet, it does not print what it is doing:

>>> system("hashedassets -q maps/map2.txt input/*.txt input/*/*.txt output/")

If we tell the command to be more verbose, it logs more information:

>>> system("hashedassets -vvv maps/map3.txt input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

Advanced usage
--------------

Re-using a map
++++++++++++++

The program reads in maps it created in a prior run to only copy files that
haven't changed since. So, the following commands do not copy any files:

>>> system("hashedassets maps/map.scss input/*.txt input/*/*.txt output/")
>>> system("hashedassets maps/map.php input/*.txt input/*/*.txt output/")
>>> system("hashedassets maps/map.js input/*.txt input/*/*.txt output/")
>>> system("hashedassets maps/map.json input/*.txt input/*/*.txt output/")
>>> system("hashedassets maps/map.sed input/*.txt input/*/*.txt output/")
>>> system("hashedassets maps/map.jsonp input/*.txt input/*/*.txt output/")
>>> system("hashedassets maps/map.txt input/*.txt input/*/*.txt output/")

If we touch one of the input files in between, the file will be read but not
copied because the hashsum is the same:

>>> system('touch -t200504072214.12 input/foo.txt')
>>> system("hashedassets maps/map.json input/*.txt input/*/*.txt output/")

If we change the file's content, it will get a new name:

>>> write("input/foo.txt", "foofoo")

Then try again:

>>> system("hashedassets maps/map.json input/*.txt input/*/*.txt output/")
rm 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/foo.txt' 'output/QIDaFD7KLKQh0l5O6b8exdew3b0.txt'

If you then list the files in the directory, note that the old file
''output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'' is gone:

>>> system("ls output/")
QIDaFD7KLKQh0l5O6b8exdew3b0.txt
Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt

If we remove one of the created files, it gets recreated:

>>> system("rm output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt")
>>> system("hashedassets maps/map.json input/*.txt input/*/*.txt output/")
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> system("ls output/")
QIDaFD7KLKQh0l5O6b8exdew3b0.txt
Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt

If a file that is about to be removed because the original content changed, it
isn't recreated:

>>> system("rm output/QIDaFD7KLKQh0l5O6b8exdew3b0.txt")
>>> write("input/foo.txt", "foofoofoo")
>>> system("hashedassets maps/map.json input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt'

Using one directory as SOURCE and DEST
++++++++++++++++++++++++++++++++++++++

This works as well:

>>> system("hashedassets -vvvv maps/samedir.json input/*.txt input/")
cp 'input/foo.txt' 'input/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt'

Even after the command is invoked a second time:

>>> system("hashedassets -vvv maps/samedir.json input/*.txt input/")
Won't copy 'input/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt' to itself.

Notice, that the mapfile does not contain the self-reference:

>>> print open("maps/samedir.json").read()
{
  "foo.txt": "NdbmnXyjdY2paFzlDw9aJzCKH9w.txt"
}

>>> write("input/foo.txt", "barbarbar")
>>> system("hashedassets -vv maps/samedir.json input/*.txt input/")
rm 'input/NdbmnXyjdY2paFzlDw9aJzCKH9w.txt'
cp 'input/foo.txt' 'input/sWL19addVG2KRYJ02EDKXF4Oh8s.txt'

