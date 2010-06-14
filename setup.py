#!/usr/bin/env python 
from setuptools import setup, find_packages

long_description="Serve your django webapp's static media by its hashsum"

name='hashedassets'
setup(
    name=name,
    version='0.0.1a',
    url='http://www.python.org/pypi/'+name,
    license='Beerware',
    description='THE BEER-WARE LICENSE',
    author='Filip Noetzel',
    author_email='filip+pypi@j03.de',
    long_description=long_description,

    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=[],
    include_package_data = True,
    install_requires=[
      'setuptools',
      'MacFSEvents==0.2.1',
    ],
    zip_safe = False,
    entry_points = {
        'console_scripts' : [
            'hashedassets = hashedassets:main',
            ]
        },
    )
