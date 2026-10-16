#!/usr/bin/env python3
"""Debug john-jay and fafnir direct-sentence failures."""
import re, sys
sys.path.insert(0, "research")
from _nameinfra import FILES, SQMAP, positions, sentence_at, expand_span
from _audit_relevance import alias_patterns
import json

g = json.load(open("research/graph.json"))
byid = {n["id"]: n for n in g["nodes"]}
for nid in ("john-jay", "fafnir"):
    pats = alias_patterns(byid[nid])
    print("###", nid, "aliases:", [p["a"] for p in pats][:8])
    for fp, t in FILES.items():
        pos = positions(t, SQMAP[fp], pats)
        if pos:
            print("  file:", fp, "occurrences:", len(pos))
            for i, a in pos[:4]:
                snt = sentence_at(t, i)
                wide = expand_span(t, i, i + len(snt) + 60, max_fwd=600) if len(snt) < 60 else snt
                print(f"    @{i} [{a}] snt({len(snt)}): {snt[:90]!r}")
                if wide != snt:
                    print(f"      wide({len(wide)}): {wide[:120]!r}")
            break
