Qsnake
======

Qsnake is an open source distribution of scientific codes with a unified Python
interface.

Installation
------------

Download the git repository::

    git clone https://github.com/qsnake/qsnake.git
    cd qsnake

Install prerequisites:

* gfortran (>= 4.4, due to the ``iso_c_binding`` module)
* gcc, g++ (>= 4.2 should be enough)
* python (>= 2.5 should work)
* git (just make sure it has the ``http`` support)

On recent Ubuntu, you can just do::

    sudo apt-get install gcc, g++, gfortran, python, git

Download external packages and install qsnake::

    ./qsnake -d
    ./qsnake -b

Run qsnake::

    ./qsnake

You can install any package, for example numpy, by doing ``qsnake install
numpy``.

License
-------

Everything in the Qsnake git repository is BSD licensed (see the LICENSE file).
Individual packages, that are downloaded externally, can have other licenses.
Depending on what packages you install, you should consult their licenses to
make sure that you comply with them.

Related Software
----------------

Qsnake should be compatible with `Sage <http://sagemath.org/>`_, the
buildsystem is rewritten from scratch, and it is BSD licensed, but the format
of the packages is exactly the same as in Sage.
