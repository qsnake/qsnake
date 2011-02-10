Qsnake
======

Qsnake is an open source distribution of scientific codes with a unified Python
interface.

Installation
------------

Download the git repository::

    git clone https://github.com/qsnake/qsnake.git
    cd qsnake

Download external packages and install minimal qsnake::

    ./qsnake -d
    ./qsnake install ipython

Run qsnake::

    ./qsnake

You can install other packages, for example numpy, by doing ``qsnake install
numpy``.

License
-------

Everything in the Qsnake git repository is BSD licensed (see the LICENSE file).
Individual packages, that are downloaded externally, can have other licenses.
Depending on what packages you install, you should consult their licenses to
make sure that you comply with them.
