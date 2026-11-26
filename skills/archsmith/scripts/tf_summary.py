#!/usr/bin/env python3
"""Summarise Terraform so the model reads a few lines instead of every file.
Usage: tf_summary.py [dir ...]            scans *.tf (skips .terraform)
       tf_summary.py --plan plan.json     reads `terraform show -json tfplan` output
Prints resource counts, resource names, CIDRs, module sources and AZ/region hints.
It is a regex scan, not a parser: use it to find what to read, then read the real files."""
import collections
import json
import os
import re
import sys

RES = re.compile(r'^\s*resource\s+"(aws_[a-z0-9_]+)"\s+"([^"]+)"', re.M)
MOD = re.compile(r'^\s*module\s+"([^"]+)"\s*\{[^}]*?source\s*=\s*"([^"]+)"', re.M | re.S)
CIDR = re.compile(r'"(\d{1,3}(?:\.\d{1,3}){3}/\d{1,2})"')
AZ = re.compile(r'availability_zones?|azs\b|az_count', re.I)


def scan_dirs(dirs):
    res, mods, cidrs, az_files = collections.defaultdict(list), [], collections.Counter(), set()
    for top in dirs:
        for root, subdirs, files in os.walk(top):
            subdirs[:] = [d for d in subdirs if d not in (".terraform", ".git", "node_modules")]
            for f in files:
                if not f.endswith(".tf"):
                    continue
                p = os.path.join(root, f)
                t = open(p, encoding="utf-8", errors="ignore").read()
                for rtype, rname in RES.findall(t):
                    res[rtype].append(f"{rname} ({os.path.relpath(p, top)})")
                mods += [(n, s) for n, s in MOD.findall(t)]
                cidrs.update(CIDR.findall(t))
                if AZ.search(t):
                    az_files.add(os.path.relpath(p, top))
    return res, mods, cidrs, az_files


def scan_plan(path):
    plan = json.load(open(path))
    res = collections.defaultdict(list)

    def walk(m):
        for r in m.get("resources", []):
            res[r["type"]].append(r["address"])
        for c in m.get("child_modules", []):
            walk(c)
    walk(plan.get("planned_values", {}).get("root_module", {}))
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--plan"]:
        res = scan_plan(a[1]); mods, cidrs, az_files = [], collections.Counter(), set()
    else:
        res, mods, cidrs, az_files = scan_dirs(a or ["."])
    print(f"# Terraform summary: {sum(len(v) for v in res.values())} resources, {len(res)} types")
    for t in sorted(res):
        names = ", ".join(res[t][:6]) + (f", +{len(res[t]) - 6} more" if len(res[t]) > 6 else "")
        print(f"- {t} x{len(res[t])}: {names}")
    if mods:
        print("\n# Modules")
        for n, s in mods:
            print(f"- {n}: {s}")
    if cidrs:
        print("\n# CIDRs found: " + ", ".join(sorted(cidrs)))
    if az_files:
        print("\n# Files that mention AZs: " + ", ".join(sorted(az_files)))
