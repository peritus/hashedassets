#!/usr/bin/env python 

from setuptools import setup, find_packages
from os.path import join, dirname

import sys
sys.path.append(join(dirname(__file__), 'src'))
from hashedassets import __version__

name='hashedassets'

setup(
    name=name,
    version = ".".join(str(n) for n in __version__),
    url='http://www.python.org/pypi/'+name,
    license='Beerware',
    description='Copies files to filenames based on their contents',
    author='Filip Noetzel',
    author_email='filip+pypi@j03.de',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    long_description=\
      open(join(dirname(__file__), 'src', 'hashedassets', 'hashedassets.rst')).read(),
    namespace_packages=[],
    include_package_data = True,
    install_requires=[
      'setuptools',
    ],
    zip_safe = False,
    extras_require = dict(
        test=[
            'zope.testing',
            'python-subunit==0.0.6',
            'junitxml==0.5',
            ],
        ),
    entry_points = dict(
        console_scripts=[
            'hashedassets = hashedassets:main',
            ],
        ),
    )
