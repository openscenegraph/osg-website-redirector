# OSG Website Redirector

This is a simple webserver written in NodeJS which:
* Checks if the URL it's been accessed by was one which used to be part of the old OpenSceneGraph site, and was captured in the site archive, and if so, gives a link to it.
* Gives a link to the new static OSG site.

It uses an HTTP 300 status code to indicate a multiple choice redirect, so web browsers won't redirect to either choice automatically - the user must click one.
This means that there's no link rot (you can still use your OSG site bookmarks and other pages with old links can still be used to access those things), but the new site is also presented to them.

Search engines should understand this, and there are `rel=alternate` `Link` headers in the HTTP response to help them with this.
That should mean everything gets crawled properly, with queries going to the new site if possible, but using the old site when it's the only one with the relevant information.
It should even keep old search indexing roughly intact.

## Hosting

This server is hosted at https://osg-website-redirector.onrender.com using [Render](https://render.com/)'s free tier.
It needs next to no resources, so this should be fine.

This avoids the hassle of security updates etc. that would be the case with a full-on VM like we'd get with AWS' free tier.
If Render decides to shut down its free tier, it should be simple to migrate to another host as the server's just a single JavaScript file that reads two small HTML files and a JSON file on startup, and serves requests using the copies in memory.
All that needs to happen is copying them somewhere and launching the JS.

## Deployment

Render will automatically deploy any new version pushed to the main branch.

## Local development

It's super simple.

* Have Node installed - more or less any version should be fine.
* Clone the repo.
* `cd node_server`
* `node server.js`

## Updating the URL mapping

When the website archive is updated, some URLs may end up mapped to different filenames (plus some URLs might get added or removed).
The URL mapping JSON file will need to be  updated.
There's a record of which URL(s) got turned into which file in the file-local headers' extra data fields in the archive's `new.zip` file.
Most software completely ignores this field, even if it makes the other extra data fields accessible, but there's a Python script to access it.

* Clone the site archive repo.
* Run `url-map-extractor.py path/to/site/archive`.
  `hts-cache/new.zip` should be a valid path relative to what you pass in as an argument.
* URLs it could figure out end up in `url-map.json`.
* Any it had problems with are logged to stdout.
  Ideally, there shouldn't be any of these - if there are, it might be a problem with the archive.
  They might be ignorable or fixable by hand, so you don't necessarily need to redo the archive.

Once you're satisfied, the JSON file can be committed and pushed, and the server will be redeployed with the new mapping.
