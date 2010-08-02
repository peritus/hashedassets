hashedassets
============

Creating some source files
--------------------------

First, we create a file to be hashed:

>>> system("mkdir input/")
>>> system("mkdir input/subdir/")
>>> system("mkdir maps/")
>>> with open("input/foo.txt", "w") as file:
...     file.write("foo")

>>> with open("input/subdir/bar.txt", "w") as file:
...     file.write("bar")

>>> system('touch -t200504072213.12 input/foo.txt')

Simple usage
------------

>>> system("hashedassets input/*.txt input/*/*.txt output/")
mkdir 'output'
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> system("hashedassets -m maps/map.txt -n my_callback input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open("maps/map.txt").read()
subdir/bar.txt: Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt
foo.txt: C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
<BLANKLINE>

>>> system("ls output/")
C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt

>>> system("ls maps/")
map.txt

Modification time is also preserved:

>>> old_stat = os.stat("input/foo.txt")
>>> new_stat = os.stat("output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt")
>>> [(getattr(old_stat, prop) == getattr(new_stat, prop))
...   for prop in ('st_mtime', 'st_atime', 'st_ino',)]
[True, True, False]

We can easily do this with multiple formats:

JavaScript
++++++++++

>>> system("hashedassets -m maps/map.js -n my_callback input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open("maps/map.js").read()
var my_callback = {
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
};

JSON
++++

>>> system("hashedassets -m maps/map.json -n my_callback input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open("maps/map.json").read()
{
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
}

JSONP
+++++

>>> system("hashedassets -m maps/map.jsonp -n my_callback input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open("maps/map.jsonp").read()
my_callback({
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
});

Sass
++++

`Sass <http://sass-lang.com/>`_  is a meta language on top of CSS.

>>> system("hashedassets -m maps/map.scss -n my_callback input/*.txt input/*/*.txt output/")
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

>>> system("hashedassets -m maps/map.php -n my_callback input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open("maps/map.php").read()
$my_callback = array(
  "subdir/bar.txt" => "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt",
  "foo.txt" => "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
)

Sed
+++

We can also generate a sed script that does the replacements for us:

>>> system("hashedassets -m maps/map.sed -n my_callback input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> print open("maps/map.sed").read()
s/subdir\/bar\.txt/Ys23Ag_5IOWqZCw9QGaVDdHwH00\.txt/g
s/foo\.txt/C-7Hteo_D9vJXQ3UfzxbwnXaijM\.txt/g
<BLANKLINE>

We should also be able to use this directly with sed

>>> with open("replaceme.html", "w") as file:
...     file.write('<a href=foo.txt>bar</a>')

The script is then applied like this:

>>> system("sed -f maps/map.sed replaceme.html")
<a href=C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt>bar</a>

However, '.' is not treated as wildcard, so the following does not work

>>> with open("replaceme2.html", "w") as file:
...     file.write('<a href=fooAtxt>bar</a>')

>>> system("sed -f maps/map.sed replaceme2.html")
<a href=fooAtxt>bar</a>

Specifying the type via -t
++++++++++++++++++++++++++

The type of the map is guessed from the filename, but you can specify it as well:

>>> system("hashedassets -m cantguessmaptype -t js input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

Re-using a map
++++++++++++++

The program reads in maps it created in a prior run to only copy files that
haven't changed since. So, the following commands do not copy any files:

>>> system("hashedassets -m maps/map.scss input/*.txt input/*/*.txt output/")
>>> system("hashedassets -m maps/map.php input/*.txt input/*/*.txt output/")
>>> system("hashedassets -m maps/map.js input/*.txt input/*/*.txt output/")
>>> system("hashedassets -m maps/map.json input/*.txt input/*/*.txt output/")
>>> system("hashedassets -m maps/map.sed input/*.txt input/*/*.txt output/")
>>> system("hashedassets -m maps/map.jsonp input/*.txt input/*/*.txt output/")
>>> system("hashedassets -m maps/map.txt input/*.txt input/*/*.txt output/")

If we touch one of the input files in between, the file will be read but not
copied because the hashsum is the same:

>>> system('touch -t200504072214.12 input/foo.txt')
>>> system("hashedassets -m maps/map.json input/*.txt input/*/*.txt output/")

If we change the file's content, it will get a new name:

>>> with open("input/foo.txt", "w") as file:
...     file.write("foofoo")

>>> system("hashedassets -m maps/map.json input/*.txt input/*/*.txt output/")
rm 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/foo.txt' 'output/QIDaFD7KLKQh0l5O6b8exdew3b0.txt'

If you then list the files in the directory, note that the old file
''output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'' is gone:

>>> system("ls output/")
QIDaFD7KLKQh0l5O6b8exdew3b0.txt
Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt


Error handling
--------------

However, if we run this with no arguments, it fails:

>>> system("hashedassets")
Usage: hashedassets [ -m MAPFILE [-t MAPTYPE] [-n MAPNAME]] SOURCE [...] DEST
<BLANKLINE>
hashedassets: error: You need to specify at least one file and a destination directory

>>> system("hashedassets -n doesnotmakesense input/*.txt output/")
Usage: hashedassets [ -m MAPFILE [-t MAPTYPE] [-n MAPNAME]] SOURCE [...] DEST
<BLANKLINE>
hashedassets: error: -n without -m does not make sense. Use -m to specify a map filename

