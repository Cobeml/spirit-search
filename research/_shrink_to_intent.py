#!/usr/bin/env python3
"""Shrink head-crept quotes back to their intended passage.

Every quote sliced before the _prev_boundary endpos fix starts one sentence
early (e.g. machaon's first leads with Eumelus's catalogue entry instead of
Tricca's). For each current highlight that CONTAINS a pre-repair quote's
passage but is longer, re-slice from the pre-repair text with the fixed
locater and replace."""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0, 'research')
import _fix_excerpts as FX

GP = Path('research/graph.json')
LP = Path('research/ledger.json')
g = json.load(open(GP))
pre = json.load(open('research/graph.json.pre_textfix_1792202840'))
led = json.load(open(LP))
srcs = {s['id']: s for s in led['sources']}

cache = {}
def tfor(sid):
    if sid not in cache:
        cache[sid] = FX.load_text(srcs.get(sid, {})) if sid in srcs else None
    return cache[sid]

def wins(t):
    nq = FX.norm_key(t)
    if len(nq) < 40:
        return [nq] if nq else []
    return [nq[:30], nq[len(nq)//2 : len(nq)//2 + 30], nq[-30:]]

def contains(big, small_windows):
    b = FX.norm_key(big)
    return all(w and w in b for w in small_windows)

shrunk = 0
for n in g['nodes']:
    pn = next((x for x in pre['nodes'] if x['id'] == n['id']), None)
    if not pn:
        continue
    pre_h = pn.get('highlights', [])
    seen = set()
    out = []
    for h in n.get('highlights', []):
        matched_pre = None
        for ph in pre_h:
            if contains(h['text'], wins(ph['text'])):
                matched_pre = ph
                break
        if matched_pre and len(h['text']) > len(matched_pre['text']) + 10:
            t = tfor(matched_pre.get('source_id'))
            if t:
                new = FX.fix_quote(matched_pre['text'], t)
                if new and new != h['text'] and contains(new, wins(matched_pre['text'])) \
                        and len(new) < len(h['text']):
                    if n['id'] in ('machaon', 'podalirius'):
                        print(f"  shrink {n['id']}: {h['text'][:60]!r} -> {new[:60]!r}")
                    h = dict(h)
                    h['text'] = new
                    shrunk += 1
        key = FX.norm_key(h['text'])[:80]
        if key in seen:
            continue          # drop exact duplicates after shrinking
        seen.add(key)
        out.append(h)
    n['highlights'] = out

for e in g['edges']:
    pe = next((x for x in pre.get('edges', [])
              if (x['from'], x['to'], x['type']) == (e['from'], e['to'], e['type'])), None)
    if not pe:
        continue
    for x in e.get('excerpts', []):
        for px in pe.get('excerpts', []):
            if contains(x['text'], wins(px['text'])) and len(x['text']) > len(px['text']) + 10:
                t = tfor(px.get('source_id'))
                if not t:
                    continue
                new = FX.fix_quote(px['text'], t)
                if new and new != x['text'] and contains(new, wins(px['text'])) \
                        and len(new) < len(x['text']):
                    x['text'] = new
                    shrunk += 1
                break

print(f"shrunk {shrunk} quotes to their intended passages")
shutil.copy(GP, GP.with_suffix('.json.bakR7'))
json.dump(g, open(GP, 'w'), indent=1, ensure_ascii=False)
print("written")
