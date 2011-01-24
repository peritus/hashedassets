hashedassets regression tests
+++++++++++++++++++++++++++++

--reference with SOURCE != DEST
----------------------------

>>> system("mkdir -p regression/in/sub/subsub/")
>>> system("mkdir -p regression/out")
>>> write("regression/in/1.txt", "1")
>>> write("regression/in/sub/2.txt", "2")
>>> write("regression/in/sub/subsub/3.txt", "3")

>>> cmd = "hashedassets -v --keep-dirs --reference=regression/out/sub/ maps/reference_regression.txt regression/in/ regression/out/"
>>> system(cmd, external=True)
cp 'regression/in/1.txt' 'regression/out/NWoZK3kTsExUV00Ywo1G5jlUKKs.txt'
mkdir -p regression/out/sub
cp 'regression/in/sub/2.txt' 'regression/out/sub/2kuSN7rMzfGcB2DKt67EqDWQELA.txt'
mkdir -p regression/out/sub/subsub
cp 'regression/in/sub/subsub/3.txt' 'regression/out/sub/subsub/d95o2uzYI7q7tY7bHI4U1xBug7s.txt'

>>> print(open('maps/reference_regression.txt').read())
../1.txt: ../NWoZK3kTsExUV00Ywo1G5jlUKKs.txt
2.txt: 2kuSN7rMzfGcB2DKt67EqDWQELA.txt
subsub/3.txt: subsub/d95o2uzYI7q7tY7bHI4U1xBug7s.txt
<BLANKLINE>

If we execute this again, there is no work to do:

>>> system(cmd, external=True)

Absolute paths
--------------

We should be agnostic whether we get absolute or relative paths as input:

>>> from os.path import abspath
>>> system("hashedassets -v maps/abspath_regression_expected.txt %s %s" % ("regression/in/", "regression/out/"), external=True)
cp 'regression/in/1.txt' 'regression/out/NWoZK3kTsExUV00Ywo1G5jlUKKs.txt'
cp 'regression/in/sub/2.txt' 'regression/out/2kuSN7rMzfGcB2DKt67EqDWQELA.txt'
cp 'regression/in/sub/subsub/3.txt' 'regression/out/d95o2uzYI7q7tY7bHI4U1xBug7s.txt'

>>> print(open('maps/abspath_regression_expected.txt').read())
1.txt: NWoZK3kTsExUV00Ywo1G5jlUKKs.txt
sub/2.txt: 2kuSN7rMzfGcB2DKt67EqDWQELA.txt
sub/subsub/3.txt: d95o2uzYI7q7tY7bHI4U1xBug7s.txt
<BLANKLINE>

>>> from os.path import abspath
>>> system("hashedassets -v maps/abspath_regression.txt %s %s" % (abspath("regression/in/"), abspath("regression/out/")), external=True)
cp '.../regression/in/1.txt' '.../regression/out/NWoZK3kTsExUV00Ywo1G5jlUKKs.txt'
cp '.../regression/in/sub/2.txt' '.../regression/out/2kuSN7rMzfGcB2DKt67EqDWQELA.txt'
cp '.../regression/in/sub/subsub/3.txt' '.../regression/out/d95o2uzYI7q7tY7bHI4U1xBug7s.txt'

>>> print(open('maps/abspath_regression.txt').read())
1.txt: NWoZK3kTsExUV00Ywo1G5jlUKKs.txt
sub/2.txt: 2kuSN7rMzfGcB2DKt67EqDWQELA.txt
sub/subsub/3.txt: d95o2uzYI7q7tY7bHI4U1xBug7s.txt
<BLANKLINE>


