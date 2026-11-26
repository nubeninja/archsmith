#!/usr/bin/env python3
"""Check a .drawio file. Exit 1 on errors. Usage: validate.py file.drawio [--strict]"""
import re
import sys
import xml.etree.ElementTree as ET

BAD_URL = re.compile(r"image=(https?:|data:)", re.I)


def check(path, strict=False):
    errors, warnings = [], []
    raw = open(path, encoding="utf-8").read()
    for m in re.finditer(r"<!--(.*?)-->", raw, re.S):
        if "--" in m.group(1):
            errors.append("double hyphen inside an XML comment")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        return [f"XML does not parse: {e}"], []
    if root.tag != "mxfile":
        errors.append("root element must be <mxfile>")
    pages = root.findall("diagram")
    if not pages:
        errors.append("no <diagram> pages")
    for d in pages:
        name = d.get("name", "?")
        if d.find("mxGraphModel") is None:
            errors.append(f"[{name}] compressed or empty diagram content; use uncompressed XML")
            continue
        cells = d.findall(".//mxCell")
        ids = [c.get("id") for c in cells]
        for i in {x for x in ids if ids.count(x) > 1}:
            errors.append(f"[{name}] duplicate cell id: {i}")
        idset = set(ids)
        if "0" not in idset:
            errors.append(f"[{name}] missing root cell id=0")
        for c in cells:
            cid, style = c.get("id"), c.get("style") or ""
            if c.get("parent") and c.get("parent") not in idset:
                errors.append(f"[{name}] {cid}: parent {c.get('parent')} does not exist")
            if c.get("edge") == "1":
                for end in ("source", "target"):
                    if c.get(end) and c.get(end) not in idset:
                        errors.append(f"[{name}] edge {cid}: {end} {c.get(end)} does not exist")
                    if not c.get(end):
                        warnings.append(f"[{name}] edge {cid}: no {end} (dangling)")
            if BAD_URL.search(style):
                errors.append(f"[{name}] {cid}: image URL or data URI in style (official shapes only)")
            for m in re.finditer(r"mxgraph\.([a-z0-9_]+)\.", style):
                if m.group(1) not in ("aws4", "weblogos"):
                    warnings.append(f"[{name}] {cid}: shape library {m.group(1)} is not aws4 or weblogos")
            if c.get("vertex") == "1" and "fontFamily" not in style and "mxgraph" in style:
                warnings.append(f"[{name}] {cid}: no fontFamily in style")
        mg = d.find("mxGraphModel")
        if mg.get("background"):
            warnings.append(f"[{name}] hardcoded background breaks dark mode")
    return errors, (warnings if not strict else warnings)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: validate.py file.drawio [--strict]")
    errs, warns = check(sys.argv[1], "--strict" in sys.argv)
    for w in warns:
        print("WARN ", w)
    for e in errs:
        print("ERROR", e)
    if not errs:
        print("OK" + (f" ({len(warns)} warnings)" if warns else ""))
    sys.exit(1 if errs or ("--strict" in sys.argv and warns) else 0)
