#! /usr/bin/env python

import os
import sys
from time import sleep
from glob import glob
from os.path import expandvars
from optparse import OptionParser
import tempfile
import subprocess
import time

version = "0.9.10.beta1"
release_date = "November 21, 2010"

class CmdException(Exception):
    pass

class PackageBuildFailed(Exception):
    pass

class PackageNotFound(Exception):
    pass

def main():
    systemwide_python = (os.environ["QSNAKE_SYSTEMWIDE_PYTHON"] == "yes")
    if systemwide_python:
        print """\
***************************************************
Qsnake is not installed. Running systemwide Python.
Only use this mode to install Qsnake.
***************************************************"""

    parser = OptionParser(usage="[options] args")
    parser.add_option("-i", "--install",
            action="store", type="str", dest="install", metavar="PACKAGE",
            default="", help="install a spkg package")
    parser.add_option("-f", "--force",
            action="store_true", dest="force",
            default=False, help="force the installation")
    parser.add_option("-d", "--download_packages",
            action="store_true", dest="download",
            default=False, help="download standard spkg packages")
    parser.add_option("-b", "--build",
            action="store_true", dest="build",
            default=False, help="build Qsnake")
    parser.add_option("-j",
            action="store", type="int", dest="cpu_count", metavar="NCPU",
            default=0, help="number of cpu to use (0 = all)")
    parser.add_option("--shell",
            action="store_true", dest="shell",
            default=False, help="starts a Qsnake shell")
    parser.add_option("-s", "--script",
            action="store", type="str", dest="script", metavar="SCRIPT",
            default=None, help="runs '/bin/bash SCRIPT' in a Qsnake shell")
    parser.add_option("--python",
            action="store", type="str", dest="python", metavar="SCRIPT",
            default=None, help="runs 'python SCRIPT' in a Qsnake shell")
    parser.add_option("--unpack",
            action="store", type="str", dest="unpack", metavar="PACKAGE",
            default=None, help="unpacks the PACKAGE into the 'devel/' dir")
    parser.add_option("--pack",
            action="store", type="str", dest="pack", metavar="PACKAGE",
            default=None, help="creates 'devel/PACKAGE.spkg' from 'devel/PACKAGE'")
    parser.add_option("--devel-install",
            action="store", type="str", dest="devel_install", metavar="PACKAGE",
            default=None, help="installs 'devel/PACKAGE' into Qsnake directly")
    parser.add_option("--create-package",
            action="store", type="str", dest="create_package",
            metavar="PACKAGE", default=None,
            help="creates 'PACKAGE.spkg' in the current directory using the official git repository sources")
    parser.add_option("--upload-package",
            action="store", type="str", dest="upload_package",
            metavar="PACKAGE", default=None,
            help="upload 'PACKAGE.spkg' from the current directory to the server (for Qsnake developers only)")
    parser.add_option("--release-binary",
            action="store_true", dest="release_binary",
            default=False, help="Creates a binary release using the current state (for Qsnake developers only)")
    parser.add_option("--lab",
            action="store_true", dest="run_lab",
            default=False, help="Runs lab(auth=False)")
    options, args = parser.parse_args()
    if len(args) == 1:
        arg, = args
        if arg == "update":
            command_update()
            return
        elif arg == "list":
            command_list()
            return
        print "Unknown command"
        sys.exit(1)
    elif len(args) == 2:
        arg1, arg2 = args
        if arg1 == "install":
            try:
                install_package(arg2, cpu_count=options.cpu_count,
                        force_install=options.force)
            except PackageBuildFailed:
                print "Package build failed"
            return
        print "Unknown command"
        sys.exit(1)
    elif len(args) == 0:
        pass
    else:
        print "Too many arguments"
        sys.exit(1)


    if options.download:
        download_packages()
        return
    if options.install:
        try:
            install_package(options.install, cpu_count=options.cpu_count,
                    force_install=options.force)
        except PackageBuildFailed:
            pass
        return
    if options.build:
        build(cpu_count=options.cpu_count)
        return
    if options.shell:
        print "Type CTRL-D to exit the Qsnake shell."
        cmd("cd $CUR; /bin/bash --rcfile $QSNAKE_ROOT/spkg/base/qsnake-shell-rc")
        return
    if options.script:
        setup_cpu(options.cpu_count)
        try:
            cmd("cd $CUR; /bin/bash " + options.script)
        except CmdException:
            print "Qsnake script exited with an error."
        return
    if options.python:
        cmd("cd $CUR; /usr/bin/env python " + options.python)
        return
    if options.unpack:
        pkg = pkg_make_absolute(options.unpack)
        print "Unpacking '%(pkg)s' into 'devel/'" % {"pkg": pkg}
        cmd("mkdir -p $QSNAKE_ROOT/devel")
        cmd("cd $QSNAKE_ROOT/devel; tar xjf %s" % pkg)
        return
    if options.pack:
        dir = options.pack
        if not os.path.exists(dir):
            dir = expandvars("$QSNAKE_ROOT/devel/%s" % dir)
        if not os.path.exists(dir):
            raise Exception("Unknown package to pack")
        dir = os.path.split(dir)[1]
        print "Creating devel/%(dir)s.spkg from devel/%(dir)s" % {"dir": dir}
        cmd("cd $QSNAKE_ROOT/devel; tar cjf %(dir)s.spkg %(dir)s" % \
                {"dir": dir})
        return
    if options.devel_install:
        dir = options.devel_install
        if not os.path.exists(dir):
            dir = expandvars("$QSNAKE_ROOT/devel/%s" % dir)
        if not os.path.exists(dir):
            raise Exception("Unknown package to pack")
        dir = os.path.normpath(dir)
        dir = os.path.split(dir)[1]
        print "Installing devel/%(dir)s into Qsnake" % {"dir": dir}
        cmd("mkdir -p $QSNAKE_ROOT/spkg/build/")
        cmd("rm -rf $QSNAKE_ROOT/spkg/build/%(dir)s" % {"dir": dir})
        cmd("cp -r $QSNAKE_ROOT/devel/%(dir)s $QSNAKE_ROOT/spkg/build/" % \
                {"dir": dir})
        setup_cpu(options.cpu_count)
        cmd("cd $QSNAKE_ROOT/spkg/build/%(dir)s; /bin/bash spkg-install" % \
                {"dir": dir})
        cmd("rm -rf $QSNAKE_ROOT/spkg/build/%(dir)s" % {"dir": dir})
        return
    if options.create_package:
        create_package(options.create_package)
        return
    if options.upload_package:
        upload_package(options.upload_package)
        return
    if options.release_binary:
        release_binary()
        return
    if options.run_lab:
        run_lab(auth=False)
        return

    if systemwide_python:
        parser.print_help()
    else:
        start_qsnake()

def setup_cpu(cpu_count):
    if cpu_count == 0:
        try:
            import multiprocessing
            cpu_count = multiprocessing.cpu_count() + 1
        except ImportError:
            cpu_count = 1
    if cpu_count > 1:
        os.environ["MAKEFLAGS"] = "-j %d" % cpu_count

def cmd(s, capture=False):
    s = expandvars(s)
    if capture:
        p = subprocess.Popen(s, shell=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        output = p.communicate()[0]
        r = p.returncode
    else:
        output = None
        r = os.system(s)
    if r != 0:
        raise CmdException("Command '%s' failed with err=%d." % (s, r))
    return output

def create_package(package):
    packages = {
        "libqsnake":      "git://github.com/hpfem/libqsnake.git",
        "onlinelab":      "git://github.com/hpfem/qsnake-online-lab.git",
        "phaml":          "git://github.com/hpfem/phaml.git",
        "arpack":         "git://github.com/hpfem/arpack.git",
        "mesheditorflex": "git://github.com/hpfem/mesheditor-flex.git",
        "cython":         "git://github.com/hpfem/cython.git",
        "hermes2d":       "git://github.com/hpfem/hermes.git",
            }
    if package not in packages:
        raise Exception("Unknown package")
    git_repo = packages[package]
    a = git_repo.rfind("/") + 1
    b = git_repo.rfind(".git")
    dir_name = git_repo[a:b]
    print "Creating a package in the current directory."
    print "Package name:", package
    print "Git repository:", git_repo
    tmp = tempfile.mkdtemp()
    print "Using temporary directory:", tmp
    cur = cmd("echo $CUR", capture=True).strip()
    cmd("cd %s; git clone %s" % (tmp, git_repo))
    commit = cmd("cd %s/%s; git rev-parse HEAD" % (tmp, dir_name),
            capture=True).strip()
    sha = commit[:7]
    if os.path.exists("%s/%s/spkg-prepare" % (tmp, dir_name)):
        print "spkg-prepare found, running it..."
        cmd("cd %s/%s; sh spkg-prepare" % (tmp, dir_name))
    # hermes packages require special handling:
    if package == "hermes2d":
        # The spkg-prepare script is in the "hermes2d" subdirectory:
        print "Preparing the hermes2d package..."
        cmd("cd %s/%s; rm -rf hermes1d hermes3d doc .git" % (tmp, dir_name))
        cmd("cd %s/%s; cp hermes2d/spkg-install ." % (tmp, dir_name))
    datetimestr = time.strftime("%Y%m%d%M%S")
    new_dir_name = "%s-%s_%s" % (package, datetimestr, sha)
    pkg_filename = "%s.spkg" % (new_dir_name)
    cmd("cd %s; mv %s %s" % (tmp, dir_name, new_dir_name))
    print "Creating the spkg package..."
    cmd("cd %s; tar cjf %s %s" % (tmp, pkg_filename, new_dir_name))
    cmd("cp %s/%s %s/%s" % (tmp, pkg_filename, cur, pkg_filename))
    print
    print "Package created: %s" % (pkg_filename)

def upload_package(package):
    cmd("cd $CUR; scp %s spilka.math.unr.edu:/var/www3/qsnake.org/packages/qsnake_st/" % (package))
    print "Package uploaded: %s" % (package)

def release_binary():
    tmp = tempfile.mkdtemp()
    qsnake_dir = "qsnake-%s" % version
    print "Using temporary directory:", tmp
    cur = cmd("echo $CUR", capture=True).strip()
    cmd("mkdir %s/%s" % (tmp, qsnake_dir))
    print "Copying qsnake into the temporary directory..."
    cmd("cp -r * %s/%s/" % (tmp, qsnake_dir))
    print "Removing source SPKG packages"
    cmd("rm -f %s/%s/spkg/standard/*" % (tmp, qsnake_dir))
    print "Creating a binary tarball"
    cmd("cd %s; tar czf %s.tar.gz %s" % (tmp, qsnake_dir, qsnake_dir))
    cmd("cp %s/%s.tar.gz ." % (tmp, qsnake_dir))
    print
    print "Package created: %s.tar.gz" % (qsnake_dir)

def start_qsnake(debug=False):
    if debug:
        print "Loading IPython..."
    try:
        import IPython
    except ImportError:
        raise Exception("You need to install 'ipython'")
    if debug:
        print "  Done."
    banner_length = 70
    l = "| Qsnake Version %s, Release Date: %s" % (version, release_date)
    l += " " * (banner_length - len(l) - 1) + "|"
    banner = "-" * banner_length + "\n" + l + "\n"
    l = "| Type lab() for the GUI."
    l += " " * (banner_length - len(l) - 1) + "|"
    banner += l + "\n" + "-" * banner_length + "\n"

    def lab_wrapper(old = False, auth=True, *args, **kwargs):
        if old:
            from sagenb.notebook.notebook_object import lab
            lab(*args, **kwargs)
        else:
            run_lab(auth=auth)
    namespace = {"lab": lab_wrapper}

    os.environ["IPYTHONDIR"] = expandvars("$DOT_SAGE/ipython")
    os.environ["IPYTHONRC"] = "ipythonrc"
    if not os.path.exists(os.environ["IPYTHONRC"]):
        cmd('mkdir -p "$DOT_SAGE"')
        cmd('cp -r "$QSNAKE_ROOT/spkg/base/ipython" "$DOT_SAGE/"')
    os.environ["MPLCONFIGDIR"] = expandvars("$DOT_SAGE/matplotlib")
    if not os.path.exists(os.environ["MPLCONFIGDIR"]):
        cmd('cp -r "$QSNAKE_ROOT/spkg/base/matplotlib" "$DOT_SAGE/"')

    if debug:
        print "Starting the main loop..."
    IPython.Shell.start(user_ns=namespace).mainloop(banner=banner)

def download_packages():
    print "Downloading standard spkg packages"
    cmd("mkdir -p $QSNAKE_ROOT/spkg/standard")
    packages = get_standard_packages()
    for p in packages:
        cmd("cd $QSNAKE_ROOT/spkg/standard; ../base/qsnake-wget %s" % p)

def install_package_spkg(pkg):
    print "Installing %s..." % pkg
    cmd("mkdir -p $QSNAKE_ROOT/spkg/build")
    cmd("mkdir -p $QSNAKE_ROOT/spkg/installed")
    try:
        cmd("cd $QSNAKE_ROOT/spkg/build; tar xjf %s" % pkg)
    except CmdException:
        print "Not a bz2 archive, trying gzip..."
        try:
            cmd("cd $QSNAKE_ROOT/spkg/build; tar xzf %s" % pkg)
        except CmdException:
            print "Not a bz2 nor gzip archive, trying tar..."
            cmd("cd $QSNAKE_ROOT/spkg/build; tar xf %s" % pkg)
    name, version = extract_name_version_from_path(pkg)
    cmd("cd $QSNAKE_ROOT/spkg/build/%s-%s; chmod +x spkg-install" % (name, version))
    cmd("cd $QSNAKE_ROOT/spkg/build/%s-%s; . $QSNAKE_ROOT/local/bin/qsnake-env; ./spkg-install" % (name, version))
    #raise PackageBuildFailed()

def install_package(pkg, install_dependencies=True, force_install=False,
        cpu_count=0):
    """
    Installs the package "pkg".

    "pkg" can be either a full path, or just the name of the package (with or
    without a version).

    "install_dependencies" ... if True, it will also install all dependencies

    "force_install" ... if True, it will install the package even if it has
                    been already installed

    "cpu_count" ... number of processors to use (0 means the number of
            processors in the  machine)

    Examples:
    >>> install_package("http://qsnake.org/stpack/python-2.6.4.p9.spkg")
    >>> install_package("spkg/standard/readline-6.0.spkg")
    >>> install_package("readline-6.0.spkg")
    >>> install_package("readline")

    """
    if pkg.startswith("http") or pkg.startswith("www"):
        remote = True
        import tempfile
        tmpdir = tempfile.mkdtemp()
        cmd("wget --directory-prefix=" + tmpdir + " " + pkg)
        pkg_name = os.path.split(pkg)
        pkg = os.path.join(tmpdir,pkg_name[1])
    else:
        remote = False
        try:
            pkg = pkg_make_absolute(pkg)
        except PackageNotFound, p:
            print p
            sys.exit(1)

    if is_installed(pkg):
        if not force_install:
            print "Package '%s' is already installed" % pkg_make_relative(pkg)
            return
    if install_dependencies:
        print "Installing dependencies for %s..." % pkg
        for dep in get_dependencies(pkg):
            install_package(dep, install_dependencies=False,
                    cpu_count=cpu_count)
    qsnake_scripts = ["qsnake-env"]
    setup_cpu(cpu_count)
    # Create the standard POSIX directories:
    for d in ["bin", "doc", "include", "lib", "man", "share"]:
        cmd("mkdir -p $QSNAKE_ROOT/local/%s" % d)
    for script in qsnake_scripts:
        cmd("cp $QSNAKE_ROOT/spkg/base/%s $QSNAKE_ROOT/local/bin/" % script)
    install_package_spkg(pkg)
    cmd("touch $QSNAKE_ROOT/spkg/installed/%s" % pkg_make_relative(pkg))

    if remote:
        from shutil import rmtree
        rmtree(tmpdir)

def is_installed(pkg):
    pkg = pkg_make_relative(pkg)
    candidates = glob(expandvars("$QSNAKE_ROOT/spkg/installed/%s" % pkg))
    if len(candidates) == 1:
        return True
    elif len(candidates) == 0:
        return False
    else:
        raise Exception("Internal error: got more candidates in is_installed")

def pkg_make_absolute(pkg):
    if pkg.endswith(".spkg"):
        if os.path.exists(pkg):
            return os.path.abspath(pkg)

        pkg_current = expandvars("$CUR/%s" % pkg)
        if os.path.exists(pkg_current):
            return pkg_current

        raise PackageNotFound("Package '%s' not found in the current directory" % pkg)

    candidates = glob(expandvars("$QSNAKE_ROOT/spkg/standard/*.spkg"))
    if len(candidates) == 0:
        raise PackageNotFound("Package '%s' not found" % pkg)
    cands = []
    for p in candidates:
        name, version = extract_name_version_from_path(p)
        if name == pkg:
            return p
        if pkg in name:
            cands.append(p)
    if len(cands) == 0:
        raise PackageNotFound("Package '%s' not found" % pkg)
    elif len(cands) == 1:
        return cands[0]

    print "Too many candidates:"
    print "    " + "\n    ".join(cands)

    raise PackageNotFound("Ambiguous package name.")

def pkg_make_relative(pkg):
    pkg = pkg_make_absolute(pkg)
    name, version = extract_name_version_from_path(pkg)
    return name

def make_unique(l):
    m = []
    for item in l:
        if item not in m:
            m.append(item)
    return m

def get_dependencies(pkg):
    """
    Gets all (including indirect) dependencies for the package "pkg".

    For simplicity, the dependency graph is currently hardwired in this
    function.
    """
    pkg_name = pkg_make_relative(pkg)
    dependency_graph = {
            "python": ["termcap", "zlib", "readline", "bzip2", "gnutls",
                "libpng"],
            "ipython": ["python"],
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
            }
    deps = []
    for dep in dependency_graph.get(pkg_name, []):
        deps.extend(get_dependencies(dep))
        deps.append(dep)
    deps = make_unique(deps)
    return deps

def get_standard_packages(just_names=False):
    """
    Returns the list of standard packages.

    just_names ... if True, only the names of the packages are returned

    Packages are copied from various sources (see the *_STANDARD variables
    below).  You can also check (and update) the versions on the web:

    Qsnake: http://qsnake.org/stpack

    """

    QSNAKE_STANDARD = "http://femhub.org/stpack"

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
            "onlinelab-201012222506_c4b2eea",

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

    if just_names:
        packages = \
                [p + ".spkg" for p in qsnake_packages]
    else:
        packages = \
                [QSNAKE_STANDARD + "/" + p + ".spkg" for p in qsnake_packages]
    return packages

def build(cpu_count=0):
    print "Building Qsnake"
    # Only add the packages that you want to have in Qsnake. Don't add
    # dependencies (those are handled in the get_dependencies() function)
    packages_list = [
            "ipython",
            "hermes1d",
            "hermes2d",
            # requires: setupdocs>=1.0, doesn't work without a net...
            "mayavi",
            "phaml",
            "libqsnake",
            "fipy",
            "sfepy",
            "sympy",
            "hdf5",
            "h5py",
            "pytables",
            "nose",
            "onlinelab",
            "mesheditorflex",
            ]
    try:
        for pkg in packages_list:
            install_package(pkg, cpu_count=cpu_count)
        print
        print "Finished building Qsnake."
    except PackageBuildFailed:
        print "Qsnake build failed."

def wait_for_ctrl_c():
    try:
        while 1:
            sleep(1)
    except KeyboardInterrupt:
        pass

def run_lab(auth=False):
    """
    Runs the online lab.
    """
    print "Starting Online Lab: Open your web browser at http://localhost:8000/"
    print "Press CTRL+C to kill it"
    print

    if auth:
        cmd("onlinelab core start --home=$SPKG_LOCAL/share/onlinelab/core-home")
    else:
        cmd("onlinelab core start --no-auth --home=$SPKG_LOCAL/share/onlinelab/core-home")

    cmd("onlinelab service start --home=$SPKG_LOCAL/share/onlinelab/service-home")
    try:
        wait_for_ctrl_c()
    finally:
        cmd("onlinelab core stop --home=$SPKG_LOCAL/share/onlinelab/core-home")
        cmd("onlinelab service stop --home=$SPKG_LOCAL/share/onlinelab/service-home")

def extract_version(package_name):
    """
    Extracts the version from the package_name.

    The version is defined as one of the following:

    -3245s
    -ab434
    -1.1-343s
    -2.3-4
    -134-minimal-24

    but not:

    -ab-13
    -ab-ab
    -m14-m16

    The leading "-" is discarded.

    Example:

    >>> extract_version("jinja-2.5")
    '2.5'

    """
    def numeric(c):
        if c in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            return True
        return False

    first_dash = package_name.find("-")
    last_dash = package_name.rfind("-")
    if first_dash == last_dash:
        return package_name[first_dash+1:]
    while not numeric(package_name[first_dash + 1]):
        package_name = package_name[first_dash+1:]
        first_dash = package_name.find("-")
        last_dash = package_name.rfind("-")
        if first_dash == last_dash:
            return package_name[first_dash+1:]
    return package_name[first_dash + 1:]

def extract_name_version(package_name):
    """
    Extracts the name and the version.

    Example:

    >>> extract_name_version("jinja-2.5")
    ('jinja', '2.5')

    """
    version = extract_version(package_name)
    name = package_name[:-len(version)-1]
    return name, version

def extract_name_version_from_path(p):
    """
    Extracts the name and the version from the full path.

    Example:

    >> extract_name_version_from_path("/home/bla/jinja-2.5.spkg")
    ('jinja', '2.5')

    """
    path, ext = os.path.splitext(p)
    assert ext == ".spkg"
    directory, filename = os.path.split(path)
    return extract_name_version(filename)

def command_update():
    # This doesn't work, because of the following error:
    # git-remote-https: relocation error: /usr/lib/libldap_r-2.4.so.2: symbol gnutls_certificate_get_x509_cas, version GNUTLS_1_4 not defined in file libgnutls.so.26 with link time reference
    # The only solution is to ship our own git version, which we will do in the
    # future, but for now we just keep this option commented out
    #print "Updating the git repository"
    #cmd("git pull https://github.com/qsnake/qsnake.git master")

    download_packages()
    print "Done."

def command_list():
    print "List of installed packages:"
    cmd("ls spkg/installed")


if __name__ == "__main__":
    main()
