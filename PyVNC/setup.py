"""Distutils setup.py for PyVNC."""
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

setup(
    name='PyVNC',
    ext_modules=cythonize([
        Extension("rfb", ["rfb.pyx"],
                  libraries=["vncserver", 'vncclient'],
                  extra_compile_args=["-g"],
                  extra_link_args=["-g"])
    ], gdb_debug=True)
)
