#!/usr/bin/env python3
"""Probe the three surviving problem firsts: math #1, cupid #1, helios #1."""
import json, re, sys
sys.path.insert(0, 'research')
import _fix_excerpts as FX
import _textclean as TC
from _aliases import ALIASES

g = json.load(open('research/graph.json'))
led = json.load(open('research/ledger.json'))
srcs = {s['id']: s for s in led['sources']}

print("helios aliases:", ALIASES.get('helios'))
print("cupido aliases:", ALIASES.get('cupid'), ALIASES.get('cupido'))
n = next(x for x in g['nodes'] if x['id'] == 'helios')
h0 = n['highlights'][0]
print("\nhelios first FULL text:")
print(repr(h0['text']))
print("source:", h0.get('source_title'))

for nid in ('math', 'cupid'):
    n = next(x for x in g['nodes'] if x['id'] == nid)
    h0 = n['highlights'][0]
    sid = h0.get('source_id')
    s = srcs.get(sid, {})
    t = FX.load_text(s)
    print(f"\n=== {nid} first (sid={sid} resolves={'yes' if t else 'NO'}) ===")
    print("quote head:", repr(h0['text'][:100]))
    print("quote tail:", repr(h0['text'][-60:]), "len:", len(h0['text']))
    if t:
        new = FX.fix_quote(h0['text'], t)
        print("fix_quote ->", repr(new)[:200] if new else "None")
        # diagnose: does the middle window match?
        nq = FX.norm_key(h0['text'])
        nt, pos = FX.norm_with_map(t)
        W = 40
        for off in (0, len(nq)//2, max(0, len(nq)-W)):
            f = nq[off:off+W]
            print(f"  window@{off}: {'HIT' if f and f in nt else 'miss'} {f[:44]!r}")
