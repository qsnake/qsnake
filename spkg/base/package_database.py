"""
Package database utilities for creating and modifying the database.
"""


from os.path import split, splitext
from qsnake_run import (extract_name_version, get_dependency_graph,
        get_standard_packages)
dependency_graph = get_dependency_graph()
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
