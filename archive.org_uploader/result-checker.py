#!/usr/bin/python

import json
import re
import sys

from pathlib import Path

with Path(sys.argv[1]).open('r', encoding='UTF-8') as f:
    urlMap = json.load(f)

urlList = []
for url in urlMap:
    urlList.append(url)

spnDir = Path(sys.argv[2])
success = []
for successJson in spnDir.glob("**/success-json.log"):
    with successJson.open('r', encoding='UTF-8') as f:
        for line in f.read().splitlines():
            success.append(json.loads(line))

noSuccess = set(urlList)
for url in success:
    if url['status'] == "success":
        if url['original_url'] in noSuccess:
            noSuccess.remove(url['original_url'])
    else:
        print(f"Unknown status: {url['status']}")

pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} (?P<url>.*)\nThe same snapshot had been made (?:\d+ hours, )?\d+ minutes ago. You can make new capture of this URL after \d+ hours.")
for invalidLog in spnDir.glob("**/invalid.log"):
    with invalidLog.open('r', encoding='UTF-8') as f:
        logText = f.read()
    for match in pattern.finditer(logText):
        url = match.group("url")
        if url in noSuccess:
            noSuccess.remove(url)

print("No successful capture for:")
for url in noSuccess:
    print(f"* '{url}' originally {"captured" if urlMap[url] else "not captured"}")
print(f"{len(noSuccess)} URLs of {len(urlList)}")

with Path("filtered-url-list.txt").open('w', encoding='UTF-8') as f:
    for url in noSuccess:
        if urlMap[url]:
            print(url, file=f)
    for url in noSuccess:
        if not urlMap[url]:
            print(url, file=f)
