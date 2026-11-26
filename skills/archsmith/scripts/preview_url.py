#!/usr/bin/env python3
"""Print a draw.io web link that opens a .drawio file with no desktop app.
The diagram sits in the URL fragment, so the browser reads it and no server receives it
until you share the link. Usage: preview_url.py file.drawio [--open]"""
import base64
import sys
import urllib.parse
import webbrowser
import zlib


def build(path):
    xml = open(path, encoding="utf-8").read()
    data = urllib.parse.quote(xml, safe="~()*!.'").encode()
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    packed = c.compress(data) + c.flush()
    return "https://app.diagrams.net/#R" + urllib.parse.quote(base64.b64encode(packed).decode(), safe="")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: preview_url.py file.drawio [--open]")
    url = build(sys.argv[1])
    print(url)
    if "--open" in sys.argv:
        webbrowser.open(url)
