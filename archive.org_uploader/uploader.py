#!/usr/bin/python

import calendar
import json
import os
import sys
import time

from pathlib import Path

import requests
import savepagenow

urlMapFile = Path(sys.argv[1])
print(f"Using URL map JSON {urlMapFile}")

with urlMapFile.open('r', encoding='UTF-8') as f:
    urlMap = json.load(f)

access_key = os.getenv("SAVEPAGENOW_ACCESS_KEY")
secret_key = os.getenv("SAVEPAGENOW_SECRET_KEY")
if not access_key or not secret_key:
    print("archive.org S3 keys are not set in the environment, rate limit will apply")
    authenticate = False
else:
    authenticate = True

resultMap = {}

for url in urlMap:
    try:
        resultMap[url] = {}
        response = requests.get("http://archive.org/wayback/available", params={"url": url})
        data = response.json()
        if data and len(data['archived_snapshots']) > 0:
            closest = data['archived_snapshots']['closest']
            resultMap[url]['prev_closest'] = closest
            if closest['available']:
                timestamp = calendar.timegm(time.strptime(closest['timestamp'], "%Y%m%d%H%M%S"))
                if (time.time() - timestamp) < 14 * 24 * 60 * 60: # two weeks
                    resultMap[url]['archive_url'] = closest['url']
                    print(f"archive.org for {url} is up to date at {closest['url']}")
                    continue
        
        # we must archive the URL
        newUrl, captured = savepagenow.capture_or_cache(url, authenticate=authenticate)
        resultMap[url]['archive_url'] = newUrl
        resultMap[url]['captured'] = captured
        if captured:
            print(f"{url} freshly archived at {newUrl}")
        else:
            print(f"archive.org used cache for {url} at {newUrl}")

    except Exception as e:
        resultMap[url]['exception_str'] = str(e)
        resultMap[url]['exception_repr'] = repr(e)
        print(e)

with open("upload-results.json", 'w', encoding='UTF-8') as f:
    json.dump(resultMap, f, indent=2)
