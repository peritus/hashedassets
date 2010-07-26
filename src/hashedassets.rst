Preparations
------------

>>> import os
>>> import sys
>>> from subprocess import Popen, STDOUT, PIPE
>>> from shlex import split

>>> def system(cmd, env=None):
...     if env != None:
...         env.update(os.environ)
...     process = Popen(split(cmd), stderr=STDOUT, stdout=PIPE, env=env)
...     # from http://stackoverflow.com/questions/1388753/how-to-get-output-from-subprocess-popen
...     while True:
...         out = process.stdout.read(1)
...         if out == '' and process.poll() != None:
...             break
...         if out != '':
...             sys.stdout.write(out)
...             sys.stdout.flush()

First, we create a file to be hashed:

>>> system("mkdir input/")
>>> with open("input/foo.txt", "w") as file:
...     file.write("foo")

>>> def create_hash_map(ext=None):
...     if ext:
...         system("hashedassets -m output/map.%s -n my_callback input/*.txt output/" % ext)
...     else:
...         system("hashedassets input/*.txt output/")
...
...     if ext:
...         print open("output/map.%s" % ext).read()

>>> create_hash_map()
mkdir 'output'
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'

>>> create_hash_map('txt')
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
foo.txt: C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
<BLANKLINE>

>>> system("ls output/")
C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
map.txt

We can easily do this with multiple formats:

>>> create_hash_map("js")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
var my_callback = {"foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt"};

>>> create_hash_map("json")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
{"foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt"}

>>> create_hash_map("jsonp")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
my_callback({"foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt"});

>>> create_hash_map("scss")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
@mixin my_callback($directive, $path) {
         @if $path == "foo.txt" { #{$directive}: url("C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt"); }
    @else {
      @warn "Did not find "#{$path}" in list of assets";
      #{$directive}: url($path);
    }
}

>>> create_hash_map("php")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
$my_callback = array(
  "foo.txt" => "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
)

We can also generate a sed script that does the replacements for us:
>>> create_hash_map("sed")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
s/foo.txt/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt/g

We should also be able to use this directly with sed

>>> with open("replaceme.html", "w") as file:
...     file.write('<a href=foo.txt>bar</a>')

>>> system("sed -f output/map.sed replaceme.html")
<a href=C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt>bar</a>

The type of the map is guessed from the filename, but you can specify it as well:

>>> system("hashedassets -m cantguessmaptype -t js input/* output/")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'

However, if we run this with no arguments, it fails:

>>> system("hashedassets")
Usage: hashedassets [ -m MAPFILE [-t MAPTYPE] [-n MAPNAME]] SOURCE [...] DEST
<BLANKLINE>
hashedassets: error: You need to specify at least one file and a destination directory

>>> system("hashedassets -n doesnotmakesense input/*.txt output/")
Usage: hashedassets [ -m MAPFILE [-t MAPTYPE] [-n MAPNAME]] SOURCE [...] DEST
<BLANKLINE>
hashedassets: error: -n without -m does not make sense. Use -m to specify a map filename

