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
import urllib2
import json

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

    parser = OptionParser(usage="""\
[options] [commands]

Commands:

  update                Updates the downloaded packages
  install PACKAGE       Installs the package 'PACKAGE'
  list                  Lists all installed packages
  test                  Runs the Qsnake testsuite""")
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
            default=0, help="number of cpu to use (0 = all), default 0")
    parser.add_option("--shell",
            action="store_true", dest="shell",
            default=False, help="starts a Qsnake shell")
    parser.add_option("-s", "--script",
            action="store", type="str", dest="script", metavar="SCRIPT",
            default=None, help="runs '/bin/bash SCRIPT' in a Qsnake shell")
    # Not much used:
    #parser.add_option("--python",
    #        action="store", type="str", dest="python", metavar="SCRIPT",
    #        default=None, help="runs 'python SCRIPT' in a Qsnake shell")

    # These are not used either:
    #parser.add_option("--unpack",
    #        action="store", type="str", dest="unpack", metavar="PACKAGE",
    #        default=None, help="unpacks the PACKAGE into the 'devel/' dir")
    #parser.add_option("--pack",
    #        action="store", type="str", dest="pack", metavar="PACKAGE",
    #        default=None, help="creates 'devel/PACKAGE.spkg' from 'devel/PACKAGE'")
    #parser.add_option("--devel-install",
    #        action="store", type="str", dest="devel_install", metavar="PACKAGE",
    #        default=None, help="installs 'devel/PACKAGE' into Qsnake directly")
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
    parser.add_option("--verify-database",
            action="store_true", dest="verify_database",
            default=False,
            help="Verifies the package database integrity")
    parser.add_option("--erase-binary",
            action="store_true", dest="erase_binary",
            default=False,
            help="Erases all binaries (keeps downloads)")
    options, args = parser.parse_args()
    if len(args) == 1:
        arg, = args
        if arg == "update":
            command_update()
            return
        elif arg == "list":
            command_list()
            return
        elif arg == "test":
            run_tests()
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
                print
                print "Package build failed."
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
    #if options.python:
    #    cmd("cd $CUR; /usr/bin/env python " + options.python)
    #    return
    #if options.unpack:
    #    pkg = pkg_make_absolute(options.unpack)
    #    print "Unpacking '%(pkg)s' into 'devel/'" % {"pkg": pkg}
    #    cmd("mkdir -p $QSNAKE_ROOT/devel")
    #    cmd("cd $QSNAKE_ROOT/devel; tar xjf %s" % pkg)
    #    return
    #if options.pack:
    #    dir = options.pack
    #    if not os.path.exists(dir):
    #        dir = expandvars("$QSNAKE_ROOT/devel/%s" % dir)
    #    if not os.path.exists(dir):
    #        raise Exception("Unknown package to pack")
    #    dir = os.path.split(dir)[1]
    #    print "Creating devel/%(dir)s.spkg from devel/%(dir)s" % {"dir": dir}
    #    cmd("cd $QSNAKE_ROOT/devel; tar cjf %(dir)s.spkg %(dir)s" % \
    #            {"dir": dir})
    #    return
    #if options.devel_install:
    #    dir = options.devel_install
    #    if not os.path.exists(dir):
    #        dir = expandvars("$QSNAKE_ROOT/devel/%s" % dir)
    #    if not os.path.exists(dir):
    #        raise Exception("Unknown package to pack")
    #    dir = os.path.normpath(dir)
    #    dir = os.path.split(dir)[1]
    #    print "Installing devel/%(dir)s into Qsnake" % {"dir": dir}
    #    cmd("mkdir -p $QSNAKE_ROOT/spkg/build/")
    #    cmd("rm -rf $QSNAKE_ROOT/spkg/build/%(dir)s" % {"dir": dir})
    #    cmd("cp -r $QSNAKE_ROOT/devel/%(dir)s $QSNAKE_ROOT/spkg/build/" % \
    #            {"dir": dir})
    #    setup_cpu(options.cpu_count)
    #    cmd("cd $QSNAKE_ROOT/spkg/build/%(dir)s; /bin/bash spkg-install" % \
    #            {"dir": dir})
    #    cmd("rm -rf $QSNAKE_ROOT/spkg/build/%(dir)s" % {"dir": dir})
    #    return
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
    if options.verify_database:
        verify_database()
        return
    if options.erase_binary:
        erase_binary()
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

def cmd(s, capture=False, ok_exit_code_list=None):
    """
    ok_exit_code_list ... a list of ok exit codes (otherwise cmd() raises an
    exception)
    """
    if ok_exit_code_list is None:
        ok_exit_code_list = [0]
    s = expandvars(s)
    if capture:
        p = subprocess.Popen(s, shell=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        output = p.communicate()[0]
        r = p.returncode
    else:
        output = None
        r = os.system(s)
    if r not in ok_exit_code_list:
        raise CmdException("Command '%s' failed with err=%d." % (s, r))
    return output

def create_package(package):
    git_repo = "http://github.com/qsnake/" + package + ".git"
    a = git_repo.rfind("/") + 1
    b = git_repo.rfind(".git")
    dir_name = git_repo[a:b]
    print "Creating a package in the current directory."
    print "Package name:", package
    print "Git repository:", git_repo
    tmp = tempfile.mkdtemp()
    print "Using temporary directory:", tmp
    cur = cmd("echo $CUR", capture=True).strip()
    cmd("cd %s; git clone --depth 1 %s" % (tmp, git_repo))
    commit = cmd("cd %s/%s; git rev-parse HEAD" % (tmp, dir_name),
            capture=True).strip()
    sha = commit[:7]
    if os.path.exists("%s/%s/spkg-prepare" % (tmp, dir_name)):
        print "spkg-prepare found, running it..."
        cmd("cd %s/%s; sh spkg-prepare" % (tmp, dir_name))
    if os.path.exists("%s/%s/spkg-install" % (tmp, dir_name)):
        print "spkg-install file exists, not doing anything"
    elif os.path.exists("%s/%s/setup.py" % (tmp, dir_name)):
        print "spkg-install file doesn't exist, creating one for setup.py"
        f = open("%s/%s/spkg-install" % (tmp, dir_name), "w")
        f.write("""
#! /bin/sh

if [ "$SPKG_LOCAL" = "" ]; then
   echo "SPKG_LOCAL undefined ... exiting";
   echo "Maybe run 'qsnake --shell'?"
   exit 1
fi

set -e

python setup.py install
""")
        f.close()
    else:
        raise Exception("spkg-install nor setup.py is present")
    new_dir_name = "%s-%s" % (package, sha)
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
    cmd("cd $QSNAKE_ROOT; cp -r * %s/%s/" % (tmp, qsnake_dir))
    print "Removing source SPKG packages"
    cmd("rm -f %s/%s/spkg/standard/*" % (tmp, qsnake_dir))
    print "Creating a binary tarball"
    cmd("cd %s; tar czf %s.tar.gz %s" % (tmp, qsnake_dir, qsnake_dir))
    cmd("cd $QSNAKE_ROOT; cp %s/%s.tar.gz ." % (tmp, qsnake_dir))
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
    spkg, git = get_standard_packages()
    for p in spkg:
        cmd("cd $QSNAKE_ROOT/spkg/standard; ../base/qsnake-wget %s" % p)

    for p in git:
        # Obtain the latest hash from github:
        url = "http://github.com/api/v2/json/repos/show/qsnake/%s/branches"
        data = urllib2.urlopen(url % p).read()
        data = json.loads(data)
        commit = data["branches"]["master"]
        sha = commit[:7]
        path = "$QSNAKE_ROOT/spkg/standard/%s-%s.spkg" % (p, sha)
        # If we already have this hash, do nothing, otherwise update the
        # package:
        if os.path.exists(expandvars(path)):
            print "Package '%s' (%s) is current, not updating." % (p, sha)
        else:
            cmd("rm -f $QSNAKE_ROOT/spkg/standard/%s-*.spkg" % p)
            cmd("cd $QSNAKE_ROOT/spkg/standard; ../../qsnake --create-package %s" % p)
            print "\n"

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
    try:
        cmd("cd $QSNAKE_ROOT/spkg/build/%s-%s; . $QSNAKE_ROOT/local/bin/qsnake-env; ./spkg-install" % (name, version))
    except CmdException:
        raise PackageBuildFailed()

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
        # Download from the web:
        remote = True
        import tempfile
        tmpdir = tempfile.mkdtemp()
        cmd("wget --directory-prefix=" + tmpdir + " " + pkg)
        pkg_name = os.path.split(pkg)
        pkg = os.path.join(tmpdir,pkg_name[1])
    elif pkg == ".":
        # Install from the current directory, try to guess
        # how to install it properly:
        if os.path.exists(expandvars("$CUR/spkg-install")):
            setup_cpu(cpu_count)
            try:
                cmd("cd $CUR; /bin/bash spkg-install")
            except CmdException:
                print "Qsnake 'install .' exited with an error."
        elif os.path.exists(expandvars("$CUR/setup.py")):
            try:
                cmd("cd $CUR; python setup.py install")
            except CmdException:
                print "Qsnake 'python setup.py install' exited with an error."
        else:
            print "Don't know how to install from the current directory."
        return
    else:
        # Install the 'pkg' package
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

    print
    print "Package '%s' installed." % pkg_make_relative(pkg)

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
    dependency_graph = get_dependency_graph()
    deps = []
    for dep in dependency_graph.get(pkg_name, []):
        deps.extend(get_dependencies(dep))
        deps.append(dep)
    deps = make_unique(deps)
    return deps

def build(cpu_count=0):
    print "Building Qsnake"
    # Only add the packages that you want to have in Qsnake. Don't add
    # dependencies (those are handled in the get_dependencies() function)
    packages_list = [
            # Basics:
            "git",
            "libqsnake",

            # SciPy stack
            "ipython",
            "scipy",
            "sympy",
            "matplotlib",
            "h5py",

            # PDE packages:
            "fipy",
            "sfepy",
            "phaml",

            # Electronic structure packages:
            "gpaw",
            "elk",
            ]
    try:
        for pkg in packages_list:
            install_package(pkg, cpu_count=cpu_count)
        print
        print "Finished building Qsnake."
    except PackageBuildFailed:
        print
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
    print "Updating the git repository"
    cmd("cd $QSNAKE_ROOT; git pull http://github.com/qsnake/qsnake.git master")

    download_packages()
    print "Done."

def command_list():
    print "List of installed packages:"
    cmd("cd $QSNAKE_ROOT; ls spkg/installed")

def get_standard_packages():
    from json import load
    f = open(expandvars("$QSNAKE_ROOT/spkg/base/packages.json"))
    data = load(f)
    QSNAKE_STANDARD = "http://qsnake.googlecode.com/files"
    spkg = []
    git = []
    for p in data:
        download = p["download"]
        if download == "qsnake-spkg":
            spkg.append(QSNAKE_STANDARD + "/" + p["name"] + "-" + \
                    p["version"] + ".spkg")
        elif download == "qsnake-git":
            git.append(p["name"])
        else:
            raise Exception("Unsupported 'download' field")
    return spkg, git

def get_dependency_graph():
    from json import load
    f = open(expandvars("$QSNAKE_ROOT/spkg/base/packages.json"))
    data = load(f)
    QSNAKE_STANDARD = "http://qsnake.googlecode.com/files"
    graph = {}
    for p in data:
        graph[p["name"]] = p["dependencies"]
    return graph

def verify_database():
    print "Verifying the package database..."
    try:
        packages = get_standard_packages()
        dependency_graph = get_dependency_graph()
        for p in dependency_graph:
            deps = dependency_graph[p]
            for p2 in deps:
                if not p2 in dependency_graph:
                    msg = "Dependency '%s' of the package '%s' doesn't exist"
                    raise Exception(msg % (p2, p))
        print "OK"
    except:
        print "Failed."
        print
        print "More information about the error:"
        raise

def erase_binary():
    print "Deleting all installed files..."
    cmd("rm -rf $QSNAKE_ROOT/local")
    cmd("rm -rf $QSNAKE_ROOT/spkg/build")
    cmd("rm -rf $QSNAKE_ROOT/spkg/installed")
    print "    Done."

def run_tests():
    import qsnake
    qsnake.test()

if __name__ == "__main__":
    main()
