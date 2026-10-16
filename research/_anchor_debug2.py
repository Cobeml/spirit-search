#!/usr/bin/env python3
"""Anchor debug for the 8 missed manual overrides."""
import re

def ch(f):
    t = open(f, errors="replace").read()
    t = re.sub(r"<[^>]+>", " ", t) if t.count("<") > 100 else re.sub(r"[<>]", " ", t)
    return re.sub(r"\s+", " ", t).lower()

w = ch("evidence/washington/weems-life-of-washington-1800s-archive-full.txt")
m = re.search(r"the great washington was born", w)
print("wash:", repr(w[m.start()-120:m.start()+220]) if m else "MISS")

l = ch("evidence/cincinnatus/livy3-roberts-wikisource.txt")
for m in list(re.finditer(r"cincinnatus", l))[:5]:
    print("livy:", repr(l[m.start()-70:m.start()+130]))

p = ch("evidence/rhiannon/apuleius-golden-ass-adlington-gutenberg.txt")
for m in [m for m in re.finditer(r"\bpsyche\b", p)][:3]:
    print("psyche:", repr(p[m.start()-90:m.start()+110]))

s = ch("evidence/sandmann/freud-cp4-1925-full-djvu.txt")
for sp in ("nathaniel", "nathanael"):
    mm = list(re.finditer(sp, s))
    print(sp, len(mm), repr(s[mm[0].start()-90:mm[0].start()+110]) if mm else "")

g = ch("evidence/lilith/ginzberg-legends1-gutenberg.txt")[20000:]
m = re.search(r"until adam was created", g)
print("adam:", repr(g[m.start()-260:m.start()+260]) if m else "MISS")

il = ch("evidence/machaon/homer-iliad-butler-mb.txt")
print("agamemnon, king of men:", bool(re.search(r"agamemnon, king of men", il)))
m = re.search(r"king agamemnon|agamemnon rose|agamemnon, son of atreus", il)
print("agam:", repr(il[m.start()-80:m.start()+150]) if m else "MISS")
m = re.search(r"priam, son of laomedon|old priam", il)
print("priam:", repr(il[m.start()-80:m.start()+150]) if m else "MISS")

import glob
for f in glob.glob("evidence/**/*.txt", recursive=True) + glob.glob("evidence/**/*.html", recursive=True):
    t = open(f, errors="replace").read().lower()
    if "quinquatrus" in t:
        print("fasti file:", f)
