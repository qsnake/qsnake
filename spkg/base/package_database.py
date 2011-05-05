"""
This script reads the packages.json file, checking that the syntax + fields are
ok, then writes it back, in a formatted style.

You should run this by hand after any modifications to packages.json, to make
sure that there are no mistakes.
"""


from os.path import split, splitext
from json import load
f = open("packages.json")
data = load(f)
g = []
for p in data:
    pkg = {
            "name": p["name"],
            "dependencies": p["dependencies"],
            "version": p["version"],
            "download": p["download"],
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
f.write("\n")
