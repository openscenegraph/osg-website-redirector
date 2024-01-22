#!/usr/bin/python

import http.client
import io
import json
import struct
import sys

from pathlib import Path, PurePosixPath
from urllib.parse import urljoin
from zipfile import BadZipFile, ZipFile, ZipInfo, _FH_EXTRA_FIELD_LENGTH, _FH_FILENAME_LENGTH, _FH_SIGNATURE, _SharedFile, sizeFileHeader, stringFileHeader, structFileHeader

class LocalHeaderExtraFieldZipFile(ZipFile):
    # __init__ inhereted

    def readLocalHeaderExtra(self, name):
        # mostly copied from ZipFile.open as that already found (and seeked past) the field
        if not self.fp:
            raise ValueError(
                "Attempt to use ZIP archive that was already closed")

        # Make sure we have an info object
        if isinstance(name, ZipInfo):
            # 'name' is already an info object
            zinfo = name
        else:
            # Get info object for name
            zinfo = self.getinfo(name)

        if self._writing:
            raise ValueError("Can't read from the ZIP file while there "
                    "is an open writing handle on it. "
                    "Close the writing handle before trying to read.")

        # Open for reading:
        self._fileRefCnt += 1
        zef_file = _SharedFile(self.fp, zinfo.header_offset,
                               self._fpclose, self._lock, lambda: self._writing)
        try:
            fheader = zef_file.read(sizeFileHeader)
            if len(fheader) != sizeFileHeader:
                raise BadZipFile("Truncated file header")
            fheader = struct.unpack(structFileHeader, fheader)
            if fheader[_FH_SIGNATURE] != stringFileHeader:
                raise BadZipFile("Bad magic number for file header")

            fname = zef_file.read(fheader[_FH_FILENAME_LENGTH])
            if fheader[_FH_EXTRA_FIELD_LENGTH]:
                return zef_file.read(fheader[_FH_EXTRA_FIELD_LENGTH])
        except:
            zef_file.close()
            raise

archiveLocal = Path(sys.argv[1])

urlMap = {}
deferred = []

with LocalHeaderExtraFieldZipFile(archiveLocal / "hts-cache" / "new.zip") as zip:
    for entryInfo in zip.infolist():
        buffered = io.BytesIO(zip.readLocalHeaderExtra(entryInfo))
        # discard start-line
        buffered.readline()
        message = http.client.parse_headers(buffered)

        if 'X-Save' in message and not message['X-StatusCode'].startswith('3'):
            if not message['X-Save'].endswith('.html') and message['Content-Type'] == 'text/html':
                urlMap[entryInfo.filename] = str(PurePosixPath(message['X-Save']).with_suffix('.html'))
            else:
                urlMap[entryInfo.filename] = message['X-Save']
        elif message['X-StatusCode'] in ['403', '404', '500']:
            urlMap[entryInfo.filename] = None
        else:
            deferred.append((entryInfo.filename, message))
    
prevLen = float('inf')
while len(deferred) < prevLen and len(deferred) > 0:
    prevLen = len(deferred)
    matched = set()

    for (url, message) in deferred:
        if 'Location' in message:
            resolved = urljoin(url, message['Location'])
            if resolved in urlMap:
                urlMap[url] = urlMap[resolved]
                matched.add(url)
            elif resolved.startswith('http://trac.openscenegraph.org') or resolved.startswith('https://trac.openscenegraph.org'):
                urlMap[url] = None
                matched.add(url)

    deferred[:] = [x for x in deferred if not x[0] in matched]

deferredGrouped = {}
for (url, message) in deferred:
    if not url in deferredGrouped:
        deferredGrouped[url] = []
    deferredGrouped[url].append(message)
for url in deferredGrouped:
    print(url)
    for message in deferredGrouped[url]:
        print(message)

for url in urlMap:
    if urlMap[url] != None:
        if not (archiveLocal / urlMap[url]).exists():
            print(f"Non-existent: {url} {urlMap[url]}")

with open("url-map.json", 'w', encoding='UTF-8') as f:
    json.dump(urlMap, f, indent=2)
