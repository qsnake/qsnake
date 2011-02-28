"""
Old style package database. This is now converted to packages.json by
the script at the end of the module. This module is not used anymore.
"""

dependency_graph = {
        "python": ["termcap", "zlib", "readline", "bzip2", "gnutls",
            "libpng"],
        "ipython": ["python"],
        "libpng": ["zlib"],
        "cython": ["python"],
        "sympy": ["python"],
        "lapack": ["fortran"],
        "arpack": ["fortran"],
        "blas": ["fortran", "lapack"],
        "numpy": ["python", "lapack", "blas"],
        "scipy": ["numpy"],
        "matplotlib": ["freetype", "libpng", "python", "numpy"],
        "hermes1d": ["cmake", "scipy", "cython", "matplotlib"],
        "hermes2d": ["cmake", "scipy", "judy", "cython", "matplotlib"],
        "vtk-cvs": ["mesa", "cmake"],
        "mayavi": ["python", "configobj", "vtk-cvs", "setuptools"],
        "pyparsing": ["python"],
        "pysparse": ["python"],
        "swig": ["python"],
        "sfepy": ["swig", "scipy"],
        "py": ["setuptools"],
        "setuptools": ["python"],
        "fipy": ["pysparse", "setuptools"],
        "libqsnake": ["python", "matplotlib"],
        "libgcrypt": ["libgpg_error"],
        "opencdk": ["zlib", "libgcrypt"],
        "gnutls": ["libgcrypt", "opencdk"],
        "python_gnutls": ["gnutls"],
        "python_django": ["python",],
        "simplejson": ["python", "setuptools"],
        "sqlite": ["python",],
        "pysqlite": ["python", "sqlite",],
        "python_tornado": ["python_pycurl"],
        "python_pycurl": ["curl"],
        "onlinelab": ["python", "python_django", "simplejson", "pysqlite",
            "pyinotify", "python_argparse", "python_lockfile", "python_daemon", "python_psutil",
            "python_tornado", "docutils", "pygments",
            ],
        "trilinos": ["python", "blas"],
        "proteus": ["numpy", "cython"],
        "phaml": ["blas", "lapack", "cmake", "numpy", "arpack"],
        "umfpack": ["blas"],
        "jinja2": ["setuptools"],
        "sphinx": ["docutils", "pygments", "jinja2"],
        }

def get_standard_packages():
    """
    Returns the list of standard packages.

    just_names ... if True, only the names of the packages are returned

    Packages are copied from various sources (see the *_STANDARD variables
    below).

    """

    QSNAKE_STANDARD = "http://qsnake.googlecode.com/files"

    qsnake_packages = [
            "termcap-1.3.1.p1",
            "zlib-1.2.5",
            "python-2.6.4.p9",
            "cython-201012090206_a60b316",
            "twisted-9.0.p2",
            "jinja-1.2.p0",
            "jinja2-2.1.1.p0",
            "python_gnutls-1.1.4.p7",
            "docutils-0.5.p0",
            "pygments-0.11.1.p0",
            "sphinx-0.6.3.p4",
            "lapack-20071123.p1",
            "blas-20070724",
            "scipy-0.8",
            "freetype-2.3.5.p2",
            "libpng-1.2.35.p2",
            "opencdk-0.6.6.p5",

            "ipython-bzr1174",
            "readline-6.0",
            "bzip2-1.0.5",
            "pexpect-2.0.p3",
            "setuptools-0.6c11.p0",
            "libgpg_error-1.6.p2.f1",
            "libgcrypt-1.4.3.p2",
            "gnutls-2.2.1.p3",

            "pyinotify-0.7.2",
            "python_argparse-1.1",
            "python_lockfile-0.8",
            "python_daemon-1.5.5",
            "python_psutil-0.1.3",
            "python_tornado-f732f98",
            #"onlinelab-201012222506_c4b2eea",

            "py-1.3.1",

            "fortran-814646f",
            "f2py-9de8d45",
            "numpy-1.5.0",
            "matplotlib-0.99.1.p4",
            "sympy-5d78c29",

            "cmake-2.8.1.p2",
            "judy-1.0.5.p1",
            "mesa-7.4.4.p3",
            "vtk-cvs-20090316-minimal.p6",
            "configobj-4.5.3",
            "mayavi-3.3.1.p2",
            "pyparsing-1.5.2",
            "swig-1.3.36",
            "sfepy-2010.1",
            "hermes1d-fb8163f",
            "hermes2d-201012090547_4c365d1",
            "pysparse-1.1-6301cea",
            "phaml-201011190816_71974f0",
            "arpack-201011191133_0ea3296",
            "fipy-2.1-51f1360",
            "libfemhub-201011294106_6e289eb",
            "hdf5-1.6.9",
            "h5py-1.2.1.p1",
            "pytables-2.1",
            "nose-0.11.1.p0",
            "python_django-1.2.1",
            "simplejson-2.1.1",
            "sqlite-3.7.2",
            "pysqlite-2.6.0",
            "mesheditorflex-201012223301_aabc985",
            "curl-7.21.1",
            "python_pycurl-7.19.0",
            "umfpack-5.5.0",
            ]

    packages = [QSNAKE_STANDARD + "/" + p + ".spkg" for p in qsnake_packages]
    return packages

from os.path import split, splitext
from qsnake_run import extract_name_version
g = []
for p in get_standard_packages():
    _, p = split(p)
    p, _ = splitext(p)
    p, version = extract_name_version(p)
    pkg = {
            "name": p,
            "dependencies": dependency_graph.get(p, []),
            "version": version,
            }
    g.append(pkg)

from json import dump
from StringIO import StringIO
s = StringIO()
dump(g, s, sort_keys=True, indent=4)
s.seek(0)
s = s.read()
# Remove the trailing space
s = s.replace(" \n", "\n")
f = open("packages.json", "w")
f.write(s)
