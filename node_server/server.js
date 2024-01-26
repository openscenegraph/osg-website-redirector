const fs = require('fs');
const http = require('node:http');
const urlMap = require('../url-map.json');

const linkFound = fs.readFileSync('./link_found.html').toString();
const notFound = fs.readFileSync('./not_found.html').toString();

const hostname = '0.0.0.0';
const port = process.env.PORT || 8000;

const htmlEscape = (str) => {
    const lut = {
        '&': "&amp;",
        '"': "&quot;",
        '\'': "&apos;",
        '<': "&lt;",
        '>': "&gt;"
    };
    return str.replace(/[&"'<>]/, char => lut[char]);
}

const server = http.createServer((req, res) => {
    let originalUrl = "https://www.openscenegraph.com";
    if (req.headers.host && req.headers.host == "lists.openscenegraph.org") {
        originalUrl = "http://lists.openscenegraph.org";
    }
    originalUrl += req.url;
    res.setHeader('Content-Type', 'text/html');
    if (urlMap[originalUrl]) {
        res.setHeader('Link', `<https://openscenegraph.github.io/OpenSceneGraphDotComBackup/OpenSceneGraph/${urlMap[originalUrl]}>; rel=alternate, <https://openscenegraph.github.io/openscenegraph.io/>; rel=alternate`);
        res.statusCode = 300;
        let fullUrlEscaped = `https://openscenegraph.github.io/OpenSceneGraphDotComBackup/OpenSceneGraph/${htmlEscape(urlMap[originalUrl])}`;
        res.end(linkFound.replaceAll("URL_REPLACEMENT_TOKEN", fullUrlEscaped));
    } else {
        res.statusCode = 404;
        res.end(notFound);
    }
});

server.listen(port, hostname, () => {
    console.log(`Server running at http://${hostname}:${port}/`);
});
