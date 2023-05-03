#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
from setuptools import find_packages, setup


# Package meta-data.
NAME = 'paow'
DESCRIPTION = 'Symbolic music generation'
KEYWORDS = 'generation midi score'
URL = "https://github.com/cpjku/paow"
AUTHOR = 'Silvan Peter'
REQUIRES_PYTHON = '>=3.7'
VERSION = '0.0.1'

# What packages are required for this module to be executed?
REQUIRED = [
    'numpy',
    'partitura>=1.1.0'
    ]

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=KEYWORDS,
    author=AUTHOR,
    url=URL,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(exclude=('tests',)),
        package_data={
        "paow": [
            "assets/dummy.txt",
        ]
        },
    install_requires=REQUIRED,
    extras_require={},
    include_package_data=True,
    license="Apache 2.0",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
