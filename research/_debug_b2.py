#!/usr/bin/env python3
"""Check eb1911-watt for boulton co-occurrence; llwyd position spread."""
import re

def ch(f):
    t = open(f, errors="replace").read()
    t = re.sub(r"<style[^>]*>.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t) if t.count("<") > 100 else re.sub(r"[<>]", " ", t)
    return re.sub(r"\s+", " ", t).lower()

w = ch("evidence/_corpus/eb1911-watt.txt")
for m in list(re.finditer(r"boulton", w))[:5]:
    seg = w[m.start():m.start() + 700]
    d = seg.find("watt")
    print("boulton->watt:", d, "|", repr(w[max(0, m.start()-80):m.start()+160]))

g = ch("evidence/_corpus/guest-mabinogion-1877-full.txt")
lp = [m.start() for m in re.finditer(r"llwyd", g)]
mp = [m.start() for m in re.finditer(r"manawyddan", g)]
best = min((abs(a - b), a, b) for a in lp for b in mp)
print("closest llwyd/manawyddan:", best)
i = best[1]
print(repr(g[i-150:i+200]))
