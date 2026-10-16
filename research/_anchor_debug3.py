#!/usr/bin/env python3
"""Final mysteries: psyche spelling, horace quinquatrus/minerva."""
import re

def ch(f):
    t = open(f, errors="replace").read()
    t = re.sub(r"<[^>]+>", " ", t) if t.count("<") > 100 else re.sub(r"[<>]", " ", t)
    return re.sub(r"\s+", " ", t).lower()

p = ch("evidence/rhiannon/apuleius-golden-ass-adlington-gutenberg.txt")
print("psyche count:", len(re.findall(r"psyche", p)))
print("psiche count:", len(re.findall(r"psiche", p)))
for m in list(re.finditer(r"ps[iy]che", p))[:3]:
    print(repr(p[m.start()-80:m.start()+120]))

h = ch("evidence/genius/horace_epistles_smart_wikisource.txt")
m = re.search(r"quinquatrus", h)
print("horace:", repr(h[m.start()-200:m.start()+200]) if m else "MISS")
print("minerva in horace:", "minerva" in h)
