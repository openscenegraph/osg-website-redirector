#!/usr/bin/python

import hashlib
import json
import urllib.parse

from pathlib import Path

urlMap = {}
with open("url-map.json", 'r', encoding='UTF-8') as f:
    urlMap = json.load(f)

def theFunction(url):
    parsed = urllib.parse.urlparse(url)
    netloc = parsed.netloc
    if not netloc in ["www.openscenegraph.com", "lists.openscenegraph.org"]:
        netloc = "www.openscenegraph.com"
    path = Path(netloc)
    relativePath = parsed.path
    while relativePath.startswith('/'):
        relativePath = relativePath.removeprefix('/')
    if relativePath.startswith("index.php/login"):
        relativePath = "index.php/login.html"
    path = path / relativePath
    strpath = str(path)
    for character in "<>:\"|?*":
        strpath = strpath.replace(character, '_')
    path = Path(strpath)
    if relativePath.endswith('/') or len(relativePath) == 0:
        path /= "index.html"
    if len(parsed.query) != 0 or url.endswith('?'):
        miniHash = hashlib.md5(parsed.query.encode("UTF-8")).hexdigest()[0:4]
        path = path.with_stem(path.stem + miniHash)
        parsedQuery = urllib.parse.parse_qs(parsed.query)
        if "jat3type" in parsedQuery and "css" in parsedQuery["jat3type"]:
            path = path.with_suffix(".css")
    if path.suffix == ".gz":
        path = path.with_suffix(".gzip")
    elif path.suffix == ".jpeg" or path.suffix == ".jpe":
        path = path.with_suffix(".jpg")
    if path.name in ["attachment-0001.obj"]:
        path = path.with_name("attachment-2.html")
    if len(str(path.parent)) >= 178:
        count = str(path.parent).count("Screenshots")
        name = f"{path.stem}{f'-{count - 9}' if count > 10 else ''}{path.suffix}"
        path = Path(str(path)[0:178]) / name
    return path

mismatches = 0
for url in urlMap:
    if urlMap[url] and theFunction(url) != Path(urlMap[url]) and theFunction(url).with_suffix(".html") != Path(urlMap[url]):
        mismatches += 1
        print(f"Mismatch: {url} got {theFunction(url)}, expected {Path(urlMap[url])}")

if mismatches == 0:
    print("All URLs matched")
else:
    print(f"{mismatches} of {len(urlMap)} paths did not match")
