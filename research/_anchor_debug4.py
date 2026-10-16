#!/usr/bin/env python3
"""Debug adam + cincinnatus pattern failures."""
import re, sys
sys.path.insert(0, "research")
from _nameinfra import FILES, expand_span, junk_score

t = FILES["evidence/lilith/ginzberg-legends1-gutenberg.txt"]
ms = list(re.finditer(r"until adam was created", t))
print("adam matches:", len(ms))
for m in ms:
    s = expand_span(t, max(0, m.start() - 120), m.start() + 400, max_back=400, max_fwd=450)
    print("  junk:", round(junk_score(s), 3), "len:", len(s), "|", repr(s[:150]))
    toc = re.search(r"(?i)contents|comparison of|comparison with", s)
    print("  tocish:", bool(toc))

l = FILES["evidence/cincinnatus/livy3-roberts-wikisource.txt"]
ms = list(re.finditer(r"by universal consent .{0,60}cincinnatus was called", l))
print("cinc matches:", len(ms))
for m in ms:
    s = expand_span(l, max(0, m.start() - 120), m.start() + 400, max_back=400, max_fwd=450)
    print("  junk:", round(junk_score(s), 3), "len:", len(s), "|", repr(s[:150]))
