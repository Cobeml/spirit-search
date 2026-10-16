#!/usr/bin/env python3
"""Debug the three b-edge misses."""
import re

def ch(f):
    t = open(f, errors="replace").read()
    t = re.sub(r"<style[^>]*>.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t) if t.count("<") > 100 else re.sub(r"[<>]", " ", t)
    return re.sub(r"\s+", " ", t).lower()

o = ch("evidence/_corpus/hippocratic-oath.txt")
print("oath:", repr(o[:160]))
print("swear pos:", o.find("i swear by apollo the physician"))

g = ch("evidence/_corpus/guest-mabinogion-1877-full.txt")
for m in list(re.finditer(r"llwyd", g))[:6]:
    seg = g[m.start():m.start() + 900]
    d = seg.find("manawyddan")
    print("llwyd->manawyddan dist:", d)

b = ch("evidence/_corpus/boswell-life-of-johnson-vol2.txt")
for m in list(re.finditer(r"bolton", b)):
    seg = b[m.start():m.start() + 600]
    d = seg.find("watt")
    print("bolton->watt dist:", d, "|", repr(b[m.start()-60:m.start()+120]))
