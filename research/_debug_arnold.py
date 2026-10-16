#!/usr/bin/env python3
"""Debug: why benedict-arnold|aaron-burr co-occurrence fails."""
import re, html, sys
sys.path.insert(0, "research")
from _aliases import ALIASES
from _audit_relevance import norm, squeeze

def tr(t):
    t = t.lower()
    return t.replace("š", "sh").replace("ž", "zh").replace("þ", "th").replace("ð", "d")

t = html.unescape(open("evidence/washington/weems_life_of_washington_archive_org_1800_djvu.txt", errors="replace").read())
t = re.sub(r"<[^>]+>", " ", t) if t.count("<") > 100 else re.sub(r"[<>]", " ", t)
t = re.sub(r"\s+", " ", tr(t))
i = t.find("arnolds and lees")
print(repr(t[i-60:i+120]))
# check padded matches
for a in ("arnold", "arnolds", "burr", "burrs"):
    print(a, "found at", t.find(" " + a + " "))
