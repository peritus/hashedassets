#!/usr/bin/env python 

from setuptools import setup, find_packages
from os.path import join, dirname

import sys
sys.path.append(join(dirname(__file__), 'src'))
import hashedassets

long_description=(
    hashedassets.__doc__ + \
    '\n' + \
    open(join(dirname(__file__),
         'src',
         'hashedassets',
         'hashedassets.rst')).read())

name='hashedassets'

install_requires=[
      'setuptools',
    ]

try:
    from collections import OrderedDict
except ImportError:
    install_requires.append("odict==1.3.2")

from version import get_git_version

setup(
    name=name,
    version=get_git_version().lstrip('v'),
    url='http://www.python.org/pypi/'+name,
    license='Beerware',
    description='Copies files to filenames based on their contents',
    long_description=long_description,
    author='Filip Noetzel',
    author_email='filip+pypi@j03.de',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=[],
    include_package_data = True,
    install_requires=install_requires,
    zip_safe = False,
    classifiers = [
      "Programming Language :: Python",
      "Programming Language :: Python :: 3",
      "Development Status :: 4 - Beta",
      "Environment :: Other Environment",
      "Intended Audience :: Developers",
      "Operating System :: OS Independent",
      "Topic :: Software Development :: Libraries :: Python Modules",
    ],
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
