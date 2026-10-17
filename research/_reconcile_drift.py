#!/usr/bin/env python3
"""Reconcile passage drift: the pre-idempotency fixer runs re-sliced some
quotes at the WRONG occurrence of repeated formulas (Iliad catalogue).
Restore: any pre-repair quote whose passage is absent from the current graph
gets re-sliced from its ORIGINAL text with the fixed occurrence-scoring
locater; current highlights that match nothing, name nothing padded, and
carry no manual flag are drifted junk and get dropped."""
import json, re, shutil, sys
from pathlib import Path
sys.path.insert(0, 'research')
import _fix_excerpts as FX
from _audit_relevance import alias_patterns, norm

GP = Path('research/graph.json')
LP = Path('research/ledger.json')
g = json.load(open(GP))
pre = json.load(open('research/graph.json.pre_textfix_1792202840'))
led = json.load(open(LP))
preled = json.load(open('research/ledger.json.pre_textfix_1792202840'))
srcs = {s['id']: s for s in led['sources']}

cache = {}
def tfor(sid):
    if sid not in cache:
        cache[sid] = FX.load_text(srcs.get(sid, {})) if sid in srcs else None
    return cache[sid]

def wkeys(t):
    nq = FX.norm_key(t)
    if len(nq) < 40:
        return {nq} if nq else set()
    return {nq[len(nq)//2 : len(nq)//2 + 30], nq[:30]}

def covered(keys, texts):
    joined = ' '.join(FX.norm_key(x) for x in texts)
    return any(k and k in joined for k in keys)

restored = dropped = kept_new = 0
pats_of = {n['id']: alias_patterns(n) for n in g['nodes']}

def padded_name(t, pats):
    tn = norm(t)
    return any(p['na'] in tn for p in pats)

for n in g['nodes']:
    pn = next((x for x in pre['nodes'] if x['id'] == n['id']), None)
    cur = n.get('highlights', [])
    pre_h = pn.get('highlights', []) if pn else []
    # 1. drop drifted junk: matches no pre passage, names nothing padded, not manual
    keep = []
    for h in cur:
        if h.get('manual') or h.get('via') == 'ledger-quote':
            keep.append(h); continue
        if pn and covered(wkeys(h['text']), [x['text'] for x in pre_h]):
            keep.append(h); continue
        if padded_name(h['text'], pats_of[n['id']]):
            keep.append(h); continue
        dropped += 1
        print(f"  drop drifted junk on {n['id']}: {h['text'][:60]!r}")
    n['highlights'] = keep
    # 2. restore lost passages from the pre-repair texts
    cur_texts = [h['text'] for h in n['highlights']]
    for ph in pre_h:
        if covered(wkeys(ph['text']), cur_texts):
            continue
        t = tfor(ph.get('source_id'))
        if not t:
            continue
        new = FX.fix_quote(ph['text'], t)
        if not new or not padded_name(new, pats_of[n['id']]):
            continue
        if covered(wkeys(new), cur_texts):
            continue
        # place restored name-bearing passage first if the node lacks one
        item = {'text': new, 'source_id': ph.get('source_id'),
                'source_title': ph.get('source_title', ''),
                'source_url': ph.get('source_url', ''), 'direct': True,
                'restored': True}
        if n['highlights'] and padded_name(n['highlights'][0]['text'], pats_of[n['id']]):
            n['highlights'].insert(1, item)
        else:
            n['highlights'].insert(0, item)
        cur_texts.append(new)
        restored += 1
        print(f"  restored passage on {n['id']}: {new[:70]!r}")

# edges: restore lost excerpts per (from,to,type)
premap = {(e['from'], e['to'], e['type']): e for e in pre.get('edges', [])}
for e in g['edges']:
    pe = premap.get((e['from'], e['to'], e['type']))
    if not pe:
        continue
    cur_texts = [x['text'] for x in e.get('excerpts', [])]
    for px in pe.get('excerpts', []):
        if covered(wkeys(px['text']), cur_texts):
            continue
        t = tfor(px.get('source_id'))
        if not t:
            continue
        new = FX.fix_quote(px['text'], t)
        if new and not covered(wkeys(new), cur_texts):
            e.setdefault('excerpts', []).append(
                {'text': new, 'source_id': px.get('source_id'),
                 'source_title': px.get('source_title', ''),
                 'source_url': px.get('source_url', '')})
            cur_texts.append(new)
            restored += 1

# ledger: restore lost quotes per source
presrcs = {s['id']: s for s in preled['sources']}
for sid, curs in ((s['id'], s.get('quotes', [])) for s in led['sources']):
    ps = presrcs.get(sid)
    if not ps:
        continue
    t = tfor(sid)
    if not t:
        continue
    cur_texts = [q['text'] for q in curs]
    for pq in ps.get('quotes', []):
        if covered(wkeys(pq['text']), cur_texts):
            continue
        new = FX.fix_quote(pq['text'], t)
        if new and not covered(wkeys(new), cur_texts):
            curs.append({'text': new, 'date': pq.get('date', ''), 'restored': True})
            cur_texts.append(new)
            restored += 1

print(f"\nrestored {restored} passages, dropped {dropped} drifted junk")
shutil.copy(GP, GP.with_suffix('.json.bakR5'))
shutil.copy(LP, LP.with_suffix('.json.bakR5'))
json.dump(g, open(GP, 'w'), indent=1, ensure_ascii=False)
json.dump(led, open(LP, 'w'), indent=1, ensure_ascii=False)
print("written")
