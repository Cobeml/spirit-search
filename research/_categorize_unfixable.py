#!/usr/bin/env python3
"""Categorize unfixable edges by type for the audit report."""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
g = json.load(open(REPO / "research" / "graph.json"))
f = json.load(open(REPO / "research" / "audit_fixability.json"))

unfix = [k for k, v in f["edges"].items() if not v["fixable"]]
bytype = {}
for k in unfix:
    frm, to, ty = k.split("|")
    bytype.setdefault(ty, []).append(k)
for ty, ks in sorted(bytype.items(), key=lambda x: -len(x[1])):
    print(f"{ty}: {len(ks)}")
    for k in ks:
        print("   ", k)
print()
# nodes that lack any name-bearing text on disk, with their cited sources
ledger = json.load(open(REPO / "research" / "ledger.json"))
src = {s["id"]: s for s in ledger["sources"]}
import re
CIT = re.compile(r"\[(\d+)\]")
for nid, v in f["nodes"].items():
    if not v["fixable"]:
        n = next(x for x in g["nodes"] if x["id"] == nid)
        ids = sorted({int(m.group(1)) for m in CIT.finditer((n.get("essay") or "")) if int(m.group(1)) in src})
        print(f"node {nid}: cited sources {[ (i, src[i]['title'][:40]) for i in ids ][:4]}")
