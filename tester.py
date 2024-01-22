#!/usr/bin/python

import json

from pathlib import Path

urlMap = {}
with open("url-map.json", 'r', encoding='UTF-8') as f:
    urlMap = json.load(f)

def theFunction(url):
    return Path(url)

mismatches = 0
for url in urlMap:
    if urlMap[url] and theFunction(url) != Path(urlMap[url]) and theFunction(url).with_suffix(".html") != Path(urlMap[url]):
        mismatches += 1
        print(f"Mismatch: {url} got {theFunction(url)}, expected {Path(urlMap[url])}")

if mismatches == 0:
    print("All URLs matched")
else:
    print(f"{mismatches} of {len(urlMap)} paths did not match")
