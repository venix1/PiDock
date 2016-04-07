"""Distutils PyDRM setup.py."""
from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='PyDRM',
    ext_modules=cythonize('libdrm.pyx')
)
