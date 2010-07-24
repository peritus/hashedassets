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

>>> def create_hash_map(format):
...     system("hashedassets -m output/map.%s input/*.txt output/" % format)
...     print open("output/map.%s" % format).read()

>>> create_hash_map('txt')
mkdir 'output'
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
foo.txt: C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
<BLANKLINE>

>>> system("ls output/")
C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
map.txt

We can easily do this with multiple formats:

>>> create_hash_map("js")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
var hashedassets = {"foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt"};

>>> create_hash_map("json")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
{"foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt"}

>>> create_hash_map("jsonp")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
hashedassets({"foo.txt": "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt"});

>>> create_hash_map("scss")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
@mixin hashedassets($directive, $path) {
         @if $path == "foo.txt" { #{$directive}: url("C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt"); }
    @else {
      @warn "Did not find "#{$path}" in list of assets";
      #{$directive}: url($path);
    }
}

>>> create_hash_map("php")
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'
$hashedassets = array(
  "foo.txt" => "C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt",
)


However, if we run this with no arguments, it fails:

>>> system("hashedassets")
Usage: hashedassets [ -m MAPFILE ] SOURCE [...] DEST
<BLANKLINE>
hashedassets: error: You need to specify at least one file and a destination directory

