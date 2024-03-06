#!/usr/bin/python

import json
import subprocess
import sys

from pathlib import Path, PurePosixPath

base = Path(sys.argv[1])

validUrls = []

subprocess.run(["git", "fetch"], cwd=base)
lsTree = subprocess.run(["git", "ls-tree", "-r", "--name-only", "origin/gh-pages"], cwd=base, capture_output=True, text=True)

for line in lsTree.stdout.splitlines():
    validUrls.append(line)
    path = PurePosixPath(line)
    if path.suffix == ".html":
        validUrls.append(str(path.parent / path.stem))

with open("new-site-urls.json", 'w', encoding='UTF-8') as f:
    json.dump(validUrls, f)
