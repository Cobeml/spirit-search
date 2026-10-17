#!/usr/bin/env python3
"""Regenerate name-bearing firsts for nodes left without one (gilgamesh, fdr)
using the same scoring as _rebuild_highlights.best_direct."""
import json, re, shutil, sys
from pathlib import Path
sys.path.insert(0, 'research')
from _nameinfra import FILES, SQMAP, positions, junk_score, register_file_source, add_quote, GP, LP
from _audit_relevance import alias_patterns

TODAY = "2026-10-16"
g = json.load(open(GP))
ledger = json.load(open(LP))
pats_of = {n['id']: alias_patterns(n) for n in g['nodes']}

def names_in(text, pats):
    tl = text.lower()
    tc = " " + re.sub(r"[^a-z0-9]+", " ", tl).strip() + " "
    tsq = re.sub(r"\s+", "", tl)
    return any(p['na'] in tc or (p['long'] and p['sq'] in tsq) for p in pats)

POS = {}
def get_pos(nid):
    if nid not in POS:
        POS[nid] = {fp: positions(t, SQMAP[fp], pats_of[nid]) for fp, t in FILES.items()}
    return POS[nid]

from _textclean import sentence_at
for nid in ('gilgamesh', 'fdr', 'mason-weems'):
    n = next(x for x in g['nodes'] if x['id'] == nid)
    pats = pats_of[nid]
    if n.get('highlights') and names_in(n['highlights'][0]['text'], pats):
        print(f"{nid}: first already names, skip")
        continue
    best = None
    for fp, t in FILES.items():
        for k, (i, _a) in enumerate((get_pos(nid).get(fp) or [])[:30]):
            snt = sentence_at(t, i) or ""
            if len(snt) < 60:
                continue
            if not names_in(snt, pats):
                continue
            score = 2.0 - junk_score(snt) + min(len(snt), 500) / 400.0 - 0.05 * k
            if best is None or score > best[0]:
                best = (score, fp, snt)
        if best and best[0] > 2.4:
            break
    if not best:
        print(f"{nid}: NO name-bearing sentence found on disk")
        continue
    _s, fp, text = best
    sid = register_file_source(ledger, fp, TODAY)
    s = next(x for x in ledger['sources'] if x['id'] == sid)
    add_quote(ledger, sid, text, TODAY)
    first_key = re.sub(r"\W+", "", text.lower())[:80]
    kept = [h for h in n.get('highlights', [])
            if re.sub(r"\W+", "", h['text'].lower())[:80] != first_key]
    n['highlights'] = [{"text": text, "source_id": sid, "source_title": s['title'],
                        "source_url": s.get('url', ''), "direct": True}] + kept[:4]
    print(f"{nid}: new first [{s['title'][:40]}]: {text[:110]!r}")

shutil.copy(GP, GP.with_suffix('.json.bakR8'))
json.dump(g, open(GP, 'w'), indent=1, ensure_ascii=False)
json.dump(ledger, open(LP, 'w'), indent=1, ensure_ascii=False)
print("written")
