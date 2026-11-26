#!/usr/bin/env python3
"""Check a .drawio file. Standard library only, Python 3.8 or newer. No install needed.

Usage:  python3 validate.py FILE.drawio [--strict] [--min-font-slide N] [--min-font-overview N]
(On Windows use `python` or `py` instead of `python3`.)

ERRORS (exit code 1): XML does not parse, compressed or empty pages, duplicate cell ids,
missing parents, edges pointing at cells that do not exist, image URLs or data URIs in styles.
WARNINGS (exit code 0, or 1 with --strict): text too small to read on a projector, labels that
are too long, overview canvas too big to view, overlapping icons or labels, other shape
libraries, hardcoded background.
The overlap check is an estimate (label sizes are guessed from text length). It does not check
whether an arrow crosses a label. Always open the file in draw.io before sharing it.
"""
import math
import re
import sys
import xml.etree.ElementTree as ET

BAD_URL = re.compile(r"image=(https?:|data:)", re.I)
DEFAULT_FONT = 12  # draw.io default when a style has no fontSize
MAX_SHOWN = 12


def num(v, d=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def plain(text):
    t = re.sub(r"<br\s*/?>|&lt;br\s*/?&gt;|&#xa;|\n", "\n", text or "", flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    return t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").strip()


def style_of(c):
    return c.get("style") or ""


def font_of(style):
    m = re.search(r"fontSize=(\d+(?:\.\d+)?)", style)
    return float(m.group(1)) if m else float(DEFAULT_FONT)


def is_icon(style):
    return bool(re.search(r"shape=mxgraph\.aws4\.(?!group)|resIcon=mxgraph\.aws4\.|shape=mxgraph\.weblogos\.", style))


def is_group(style):
    return bool(re.search(r"group|container=1|swimlane|dashed=1;.*fillColor=none", style)) and not is_icon(style)


def absolute_boxes(cells):
    by_id = {c.get("id"): c for c in cells}
    cache = {}

    def origin(cid):
        if cid in cache:
            return cache[cid]
        c = by_id.get(cid)
        if c is None or c.get("vertex") != "1":
            cache[cid] = (0.0, 0.0)
            return cache[cid]
        g = c.find("mxGeometry")
        x = num(g.get("x")) if g is not None else 0.0
        y = num(g.get("y")) if g is not None else 0.0
        px, py = origin(c.get("parent"))
        cache[cid] = (px + x, py + y)
        return cache[cid]

    out = {}
    for c in cells:
        if c.get("vertex") == "1":
            g = c.find("mxGeometry")
            if g is not None and g.get("width"):
                x, y = origin(c.get("id"))
                out[c.get("id")] = (x, y, num(g.get("width")), num(g.get("height")))
    return out


def label_box(style, text, box):
    """Estimated box of an icon's outside label, or None if the label sits inside the shape."""
    x, y, w, h = box
    lines = plain(text).split("\n")
    fs = font_of(style)
    ew = min(max((len(l) for l in lines), default=0) * fs * 0.55, 420)
    eh = len(lines) * fs * 1.25
    if ew == 0:
        return None
    if "labelPosition=right" in style:
        return (x + w + 6, y + h / 2 - eh / 2, ew, eh)
    if "labelPosition=left" in style:
        return (x - 6 - ew, y + h / 2 - eh / 2, ew, eh)
    if "verticalLabelPosition=bottom" in style:
        return (x + w / 2 - ew / 2, y + h + 4, ew, eh)
    if "verticalLabelPosition=top" in style:
        return (x + w / 2 - ew / 2, y - 4 - eh, ew, eh)
    return None


def hit(a, b, tol=4.0):
    return a[0] + tol < b[0] + b[2] and b[0] + tol < a[0] + a[2] and a[1] + tol < b[1] + b[3] and b[1] + tol < a[1] + a[3]


def check(path, strict=False, min_slide=20, min_overview=14):
    errors, warnings = [], []
    raw = open(path, encoding="utf-8").read()
    for m in re.finditer(r"<!--(.*?)-->", raw, re.S):
        if "--" in m.group(1):
            errors.append("double hyphen inside an XML comment")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        return ["XML does not parse: %s" % e], []
    if root.tag != "mxfile":
        errors.append("root element must be <mxfile>")
    pages = root.findall("diagram")
    if not pages:
        errors.append("no <diagram> pages")
    for d in pages:
        name = d.get("name", "?")
        mg = d.find("mxGraphModel")
        if mg is None:
            errors.append("[%s] compressed or empty diagram content; use uncompressed XML" % name)
            continue
        pw, ph = num(mg.get("pageWidth")), num(mg.get("pageHeight"))
        slide = (pw, ph) == (1920.0, 1080.0)
        floor = min_slide if slide else min_overview
        cells = mg.findall(".//mxCell")
        ids = [c.get("id") for c in cells]
        for i in sorted({x for x in ids if ids.count(x) > 1}):
            errors.append("[%s] duplicate cell id: %s" % (name, i))
        idset = set(ids)
        if "0" not in idset:
            errors.append("[%s] missing root cell id=0" % name)
        small, wordy = [], []
        for c in cells:
            cid, style = c.get("id"), style_of(c)
            if c.get("parent") and c.get("parent") not in idset:
                errors.append("[%s] %s: parent %s does not exist" % (name, cid, c.get("parent")))
            if c.get("edge") == "1":
                for end in ("source", "target"):
                    if c.get(end) and c.get(end) not in idset:
                        errors.append("[%s] edge %s: %s %s does not exist" % (name, cid, end, c.get(end)))
                    if not c.get(end):
                        warnings.append("[%s] edge %s: no %s (dangling)" % (name, cid, end))
            if BAD_URL.search(style):
                errors.append("[%s] %s: image URL or data URI in style (official shapes only)" % (name, cid))
            for m in re.finditer(r"mxgraph\.([a-z0-9_]+)\.", style):
                if m.group(1) not in ("aws4", "weblogos"):
                    warnings.append("[%s] %s: shape library %s is not aws4 or weblogos" % (name, cid, m.group(1)))
            text = plain(c.get("value"))
            if text and c.get("vertex") == "1":
                fs = font_of(style)
                if fs < floor:
                    small.append("%s (%gpx, \"%s\")" % (cid, fs, text.split("\n")[0][:24]))
                words = len(text.split())
                limit = 70 if style.startswith("text") else 9
                if words > limit:
                    wordy.append("%s (%d words)" % (cid, words))
        if small:
            warnings.append("[%s] text under %gpx on a %s page: %s%s" % (
                name, floor, "slide" if slide else "overview", ", ".join(small[:MAX_SHOWN]),
                " +%d more" % (len(small) - MAX_SHOWN) if len(small) > MAX_SHOWN else ""))
        if wordy:
            warnings.append("[%s] labels too long (keep icon labels to 2 short lines): %s%s" % (
                name, ", ".join(wordy[:MAX_SHOWN]), " +%d more" % (len(wordy) - MAX_SHOWN) if len(wordy) > MAX_SHOWN else ""))
        if not slide and (pw > 3000 or ph > 3000):
            warnings.append("[%s] canvas %gx%g is too big to view; aim for 3000 px or less per side" % (name, pw, ph))
        if mg.get("background"):
            warnings.append("[%s] hardcoded background breaks dark mode" % name)
        # overlap estimate between icons, their outside labels and free text
        boxes = absolute_boxes(cells)
        items = []  # (owner id, kind, box)
        for c in cells:
            cid, style = c.get("id"), style_of(c)
            if cid not in boxes or c.get("edge") == "1":
                continue
            if "ellipse" in style and "fontColor=#FFFFFF" in style:
                continue  # numbered badges overlap icons on purpose
            if is_icon(style):
                items.append((cid, "icon", boxes[cid]))
                lb = label_box(style, c.get("value"), boxes[cid])
                if lb:
                    items.append((cid, "label", lb))
            elif style.startswith("text") and plain(c.get("value")):
                items.append((cid, "text", boxes[cid]))
        found = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if a[0] == b[0]:
                    continue
                if hit(a[2], b[2]):
                    found.append("%s %s / %s %s" % (a[0], a[1], b[0], b[1]))
        if found:
            warnings.append("[%s] %d likely overlaps: %s%s" % (
                name, len(found), "; ".join(found[:MAX_SHOWN]), " +%d more" % (len(found) - MAX_SHOWN) if len(found) > MAX_SHOWN else ""))
    return errors, warnings


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    opts = {}
    for i, a in enumerate(argv[1:], 1):
        if a in ("--min-font-slide", "--min-font-overview") and i + 1 < len(argv):
            opts[a] = float(argv[i + 1])
            args = [x for x in args if x != argv[i + 1]]
    if not args:
        sys.exit(__doc__)
    strict = "--strict" in argv
    errs, warns = check(args[0], strict, opts.get("--min-font-slide", 20), opts.get("--min-font-overview", 14))
    for w in warns:
        print("WARN ", w)
    for e in errs:
        print("ERROR", e)
    if not errs:
        print("OK" + (" (%d warnings)" % len(warns) if warns else ""))
    return 1 if errs or (strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
