#!/usr/bin/env python3
"""Debug the 11 unrepairables: why did locate()/repair() fail?"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, 'research')
import _fix_excerpts as FX
import _textclean as TC

g = json.load(open('research/graph.json'))
led = json.load(open('research/ledger.json'))
srcs = {s['id']: s for s in led['sources']}
TARGETS = {'gilgamesh', 'volundr', 'nithuth', 'bothvild', 'james-watt',
           'adam-smith', 'faraday', 'joule', 'cronos', 'rhea', 'eos'}

ALL = {}
for p in sorted(Path('evidence').rglob('*')):
    if p.suffix in ('.txt', '.html') and p.stat().st_size > 200:
        ALL[str(p)] = TC.norm_file(p.read_text(errors='replace'))
NORM = {}
def normed(fp):
    if fp not in NORM:
        NORM[fp] = FX.norm_with_map(ALL[fp])
    return NORM[fp]

for n in g['nodes']:
    if n['id'] not in TARGETS:
        continue
    for h in n.get('highlights', []):
        s = h['text'].strip()
        seg = bool(s) and (s[0].islower() or not re.search(r'[.!?\u201d\u2019"\)\]]$', s))
        if not seg and not re.search(r'\.mw-parser|thumb\|', s):
            continue
        nq = FX.norm_key(h['text'])
        print(f"\n== {n['id']} sid={h.get('source_id')} nqlen={len(nq)}")
        print("   quote[:90]:", repr(h['text'][:90]))
        print("   quote[-50:]:", repr(h['text'][-50:]))
        hits = []
        W = 40
        for fp in ALL:
            nt, pos = normed(fp)
            for off in (0, len(nq)//2, max(0, len(nq)//2-60), max(0, len(nq)-W)):
                f = nq[off:off+W]
                if len(f) < 20:
                    continue
                i = nt.find(f)
                if i >= 0:
                    hits.append((fp, off, i))
                    break
            if len(hits) >= 3:
                break
        print("   locate hits:", hits[:3] if hits else "NONE")
        if not hits:
            # try squeezed matching (OCR linebreaks)
            sq = re.sub(r'\s+', '', nq)
            for fp in list(ALL)[:70]:
                nts = re.sub(r'\s+', '', normed(fp)[0])
                j = nts.find(sq[:40])
                if j >= 0:
                    print("   SQUEEZED hit in", fp, "at", j)
                    break
