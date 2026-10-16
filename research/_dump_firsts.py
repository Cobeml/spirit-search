#!/usr/bin/env python3
"""Print first (direct) highlight of every node for manual quality review."""
import json, sys
from pathlib import Path

g = json.load(open("research/graph.json"))
for n in g["nodes"]:
    hls = n.get("highlights", [])
    if not hls:
        print(f"{n['id']:28s} <none>")
        continue
    h = hls[0]
    tag = "D" if h.get("direct") else " "
    print(f"{n['id']:28s} [{tag}] {h['text'][:105]!r}")
