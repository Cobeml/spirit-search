#!/usr/bin/env python3
"""Isolate: probe logic for a single edge (benedict-arnold|aaron-burr)."""
import json, re, html, sys
from pathlib import Path

sys.path.insert(0, "research")
from _audit_relevance import alias_patterns

REPO = Path(".")
G = json.load(open("research/graph.json"))
byid = {n["id"]: n for n in G["nodes"]}
pats_of = {n["id"]: alias_patterns(n) for n in G["nodes"]}

def tr(t):
    t = t.lower()
    return t.replace("š", "sh").replace("ž", "zh").replace("þ", "th").replace("ð", "d")

FILES, SQMAP = {}, {}
for p in sorted(REPO.glob("evidence/**/*.txt")) + sorted(REPO.glob("evidence/**/*.html")):
    t = html.unescape(p.read_text(errors="replace"))
    t = re.sub(r"<[^>]+>", " ", t) if t.count("<") > 100 else re.sub(r"[<>]", " ", t)
    t = re.sub(r"\s+", " ", tr(t))
    fp = str(p)
    FILES[fp] = t
    SQMAP[fp] = [i for i, ch in enumerate(t) if not ch.isspace()]

def positions(t, sqm, pats):
    out = []
    tsq = re.sub(r"\s+", "", t)
    for p in pats:
        na = " " + re.sub(r"[^a-z0-9]+", " ", tr(p["a"])).strip() + " "
        sq = re.sub(r"\s+", "", na)
        start = 0
        while True:
            i = t.find(na, start)
            if i < 0:
                break
            out.append((i, p["a"]))
            start = i + 1
        if len(sq) >= 6:
            start = 0
            while True:
                j = tsq.find(sq, start)
                if j < 0:
                    break
                out.append((sqm[j] if j < len(sqm) else j, p["a"] + "(sq)"))
                start = j + 1
    out.sort()
    return out

fp = "evidence/washington/weems_life_of_washington_archive_org_1800_djvu.txt"
af = positions(FILES[fp], SQMAP[fp], pats_of["benedict-arnold"])
at = positions(FILES[fp], SQMAP[fp], pats_of["aaron-burr"])
print("arnold-side aliases:", [p["a"] for p in pats_of["benedict-arnold"]])
print("burr-side aliases:", [p["a"] for p in pats_of["aaron-burr"]])
print("af:", len(af), af[-6:])
print("at:", len(at), at[:6])
best = None
j = 0
for i, _ in af:
    while j < len(at) and at[j][0] < i:
        j += 1
    for k in (j - 1, j):
        if 0 <= k < len(at):
            d = abs(at[k][0] - i)
            if d <= 600 and (best is None or d < best[0]):
                best = (d, i, at[k][0])
print("best:", best)
