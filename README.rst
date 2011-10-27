Qsnake
======

Qsnake is an open source distribution of scientific codes with a unified Python
interface.

Installation
------------

Release
~~~~~~~

Download the source package from:

https://github.com/qsnake/qsnake/archives/master

Install prerequisites:

* gfortran (>= 4.4, due to the ``iso_c_binding`` module)
* gcc, g++ (>= 4.2 should be enough)
* python (>= 2.5 should work)
* make (any version should work)

On recent Ubuntu, you can just do::

    sudo apt-get install gcc g++ gfortran python make

and::

    tar xf qsnake-0.9.11.tar
    cd qsnake-0.9.11
    ./qsnake -b

Development Version
~~~~~~~~~~~~~~~~~~~

Besides the prerequisites above, also install:

* git (just make sure it has the ``http`` support)

On recent Ubuntu, you can just do::

    sudo apt-get install git

Download the git repository::

    git clone https://github.com/qsnake/qsnake.git
    cd qsnake

Download external packages::

    ./qsnake -d

Now you have an equivalent source package as in the "Release" section (except
with all the recent updates). Install qsnake as usual using::

    ./qsnake -b

Tip
~~~

Add the ``qsnake`` executable into your ``$PATH``, for example by::

    cd ~/usr/bin
    ln -s ~/repos/qsnake/qsnake .
    export PATH=$PATH:$HOME/usr/bin

And just use ``qsnake`` from now on.


Usage
-----

Run qsnake::

    qsnake

Launch web GUI::

    qsnake --lab

or run lab() from within qsnake in a terminal.
You can install any package, for example numpy, by doing ``qsnake install
numpy``. You can develop in the Qsnake environment with::

    qsnake --shell


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
