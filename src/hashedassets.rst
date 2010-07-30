hashedassets
============

Creating some source files
--------------------------

First, we create a file to be hashed:

>>> system("mkdir input/")
>>> system("mkdir input/subdir/")
>>> with open("input/foo.txt", "w") as file:
...     file.write("foo")

>>> with open("input/subdir/bar.txt", "w") as file:
...     file.write("bar")

>>> system('touch -t200504072213.12 input/foo.txt')

>>> def create_hash_map(ext=None):
...     if ext:
...         system("hashedassets -m output/map.%s -n my_callback input/*.txt input/*/*.txt output/" % ext)
...     else:
...         system("hashedassets input/*.txt input/*/*.txt output/")
...
...     if ext:
...         print open("output/map.%s" % ext).read()

Simple usage
------------

>>> create_hash_map()
mkdir 'output'
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

>>> create_hash_map('txt')
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'
subdir/bar.txt: Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt
foo.txt: C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
<BLANKLINE>

>>> system("ls output/")
C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt
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

>>> create_hash_map("js")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'
var my_callback = {
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
};

JSON
++++

>>> create_hash_map("json")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'
{
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
}

JSONP
+++++

>>> create_hash_map("jsonp")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'
my_callback({
  "foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
  "subdir/bar.txt": "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt"
});

Sass
++++

`Sass <http://sass-lang.com/>`_  is a meta language on top of CSS.

>>> create_hash_map("scss")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'
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

>>> create_hash_map("php")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'
$my_callback = array(
  "subdir/bar.txt" => "Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt",
  "foo.txt" => "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
)

Sed
+++

We can also generate a sed script that does the replacements for us:

>>> create_hash_map("sed")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'
s/subdir\/bar\.txt/Ys23Ag_5IOWqZCw9QGaVDdHwH00\.txt/g
s/foo\.txt/C-7Hteo_D9vJXQ3UfzxbwnXaijM\.txt/g
<BLANKLINE>

We should also be able to use this directly with sed

>>> with open("replaceme.html", "w") as file:
...     file.write('<a href=foo.txt>bar</a>')

The script is then applied like this:

>>> system("sed -f output/map.sed replaceme.html")
<a href=C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt>bar</a>

However, '.' is not treated as wildcard, so the following does not work

>>> with open("replaceme2.html", "w") as file:
...     file.write('<a href=fooAtxt>bar</a>')

>>> system("sed -f output/map.sed replaceme2.html")
<a href=fooAtxt>bar</a>

Specifying the type via -t
++++++++++++++++++++++++++

The type of the map is guessed from the filename, but you can specify it as well:

>>> system("hashedassets -m cantguessmaptype -t js input/*.txt input/*/*.txt output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
cp 'input/subdir/bar.txt' 'output/Ys23Ag_5IOWqZCw9QGaVDdHwH00.txt'

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

