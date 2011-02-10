from qsnake_run import extract_version, extract_name_version

def test1():
    assert extract_version("onlinelab-9934211") == "9934211"
    assert extract_version("termcap-1.3.1.p1") == "1.3.1.p1"

def test2():
    tests = {
            "onlinelab-9934211": "9934211",
            "termcap-1.3.1.p1": "1.3.1.p1",
            "zlib-1.2.5": "1.2.5",
            "python-2.6.4.p9": "2.6.4.p9",
            "cython-0.12.1": "0.12.1",
            "twisted-9.0.p2": "9.0.p2",
            "jinja-1.2.p0": "1.2.p0",
            "jinja2-2.1.1.p0": "2.1.1.p0",
            "python_gnutls-1.1.4.p7": "1.1.4.p7",
            "docutils-0.5.p0": "0.5.p0",
            "pygments-0.11.1.p0": "0.11.1.p0",
            "sphinx-0.6.3.p4": "0.6.3.p4",
            "lapack-20071123.p1": "20071123.p1",
            "blas-20070724": "20070724",
            "scipy-0.8": "0.8",
            "freetype-2.3.5.p2": "2.3.5.p2",
            "libpng-1.2.35.p2": "1.2.35.p2",
            "opencdk-0.6.6.p5": "0.6.6.p5",

            "ipython-bzr1174": "bzr1174",
            "readline-6.0": "6.0",
            "bzip2-1.0.5": "1.0.5",
            "pexpect-2.0.p3": "2.0.p3",
            "setuptools-0.6c11.p0": "0.6c11.p0",
            "libgpg_error-1.6.p2.f1": "1.6.p2.f1",
            "libgcrypt-1.4.3.p2": "1.4.3.p2",
            "gnutls-2.2.1.p3": "2.2.1.p3",

            "qsnake-lab-2ffaa67": "2ffaa67",
            "pyinotify-0.7.2": "0.7.2",
            "python_argparse-1.1": "1.1",
            "python_lockfile-0.8": "0.8",
            "python_daemon-1.5.5": "1.5.5",
            "python_psutil-0.1.3": "0.1.3",
            "python_tornado-f732f98": "f732f98",
            "onlinelab-9934211": "9934211",

            "py-1.3.1": "1.3.1",

            "fortran-814646f": "814646f",
            "f2py-9de8d45": "9de8d45",
            "numpy-1.5.0": "1.5.0",
            "matplotlib-0.99.1.p4": "0.99.1.p4",
            "sympy-5d78c29": "5d78c29",

            "cmake-2.8.1.p2": "2.8.1.p2",
            "judy-1.0.5.p1": "1.0.5.p1",
            "mesa-7.4.4.p3": "7.4.4.p3",
            "vtk-cvs-20090316-minimal.p6": "20090316-minimal.p6",
            "configobj-4.5.3": "4.5.3",
            "mayavi-3.3.1.p2": "3.3.1.p2",
            "pyparsing-1.5.2": "1.5.2",
            "swig-1.3.36": "1.3.36",
            "sfepy-2010.1": "2010.1",
            "hermes1d-fb8163f": "fb8163f",
            "hermes2d-ee3e3ab": "ee3e3ab",
            "pysparse-1.1-6301cea": "1.1-6301cea",
            "pysparse-1.1-b301cea": "1.1-b301cea",
            "pysparse-git-b301cea": "b301cea",
            "phaml-6932960": "6932960",
            "fipy-2.1-51f1360": "2.1-51f1360",
            "libqsnake-af1c401": "af1c401",
            "hdf5-1.6.9": "1.6.9",
            "h5py-1.2.1.p1": "1.2.1.p1",
            "pytables-2.1": "2.1",
            "nose-0.11.1.p0": "0.11.1.p0",
            "python_django-1.2.1": "1.2.1",
            "simplejson-2.1.1": "2.1.1",
            "sqlite-3.7.2": "3.7.2",
            "pysqlite-2.6.0": "2.6.0",
            "mesheditorflex-1.0.p1": "1.0.p1",
            "curl-7.21.1": "7.21.1",
            "python_pycurl-7.19.0": "7.19.0",
            "umfpack-5.5.0": "5.5.0",

            "onlinelab-201012090744_c4e10e9": "201012090744_c4e10e9",
            "phaml-201011190816_71974f0": "201011190816_71974f0",
            }
    for t in tests:
        assert extract_version(t) == tests[t]

def test3():
    assert extract_name_version("onlinelab-9934211") == ("onlinelab",
            "9934211")
    assert extract_name_version("termcap-1.3.1.p1") == ("termcap",
            "1.3.1.p1")
    assert extract_name_version("vtk-cvs-20090316-minimal.p6") == \
            ("vtk-cvs", "20090316-minimal.p6")
