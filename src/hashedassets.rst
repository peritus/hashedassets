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


>>> system("mkdir input/")
>>> with open("input/foo.txt", "w") as file:
...     file.write("foo")
>>> system("hashedassets -i input -o output")
mkdir 'output'
cp 'input/foo.txt' 'output/C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt'

>>> system("ls output/")
C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt
hashedassets.map

>>> open("output/hashedassets.map").read()
'foo.txt: C-7Hteo_D9vJXQ3UfzxbwnXaijM.txt\n'
