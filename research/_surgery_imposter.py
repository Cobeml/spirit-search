#!/usr/bin/env python3
"""Surgery after chain: remove imposter-sourced quotes from ledger+graph,
repair the affected nodes (math), and report helios/cupid first-highlight
state for follow-up."""
import json, re, shutil, sys
from pathlib import Path
sys.path.insert(0, 'research')
import _fix_excerpts as FX
import _textclean as TC

GP = Path('research/graph.json')
LP = Path('research/ledger.json')
g = json.load(open(GP))
led = json.load(open(LP))
srcs = {s['id']: s for s in led['sources']}

IMPOSTER_SID = 235   # registered against the deleted Hardy Boys file
changed = False

# 1. purge quotes on imposter sources; drop imposter sources entirely
purged_quotes = sum(len(s.get('quotes', [])) for s in srcs.values() if s['id'] == IMPOSTER_SID)
kept_sources = [s for s in led['sources'] if s['id'] != IMPOSTER_SID]
print(f"purging source {IMPOSTER_SID} ({purged_quotes} quote(s))")
led['sources'] = kept_sources

# 2. drop any graph highlight/excerpt citing the imposter source
dropped = []
for n in g['nodes']:
    keep = []
    for h in n.get('highlights', []):
        if h.get('source_id') == IMPOSTER_SID:
            dropped.append((n['id'], h['text'][:70]))
            continue
        keep.append(h)
    if len(keep) != len(n.get('highlights', [])):
        n['highlights'] = keep
        changed = True
for e in g['edges']:
    keep = [x for x in e.get('excerpts', []) if x.get('source_id') != IMPOSTER_SID]
    if len(keep) != len(e.get('excerpts', [])):
        e['excerpts'] = keep
        changed = True
print("dropped graph items:", dropped)

# 3. re-fix remaining highlights on affected nodes against their real files
cache = {}
def tfor(sid):
    if sid not in cache:
        s = srcs.get(sid, {}) if sid in srcs else {}
        cache[sid] = FX.load_text(s) if sid in srcs else None
    return cache[sid]

repaired = 0
for nid in sorted({d[0] for d in dropped}):
    n = next(x for x in g['nodes'] if x['id'] == nid)
    for h in n.get('highlights', []):
        sid = h.get('source_id')
        t = tfor(sid)
        if not t:
            continue
        new = FX.fix_quote(h['text'], t)
        if new and new != h['text'] and 40 <= len(new) <= 3000:
            h['text'] = new
            repaired += 1
print(f"repaired {repaired} highlights on affected nodes")

# 4. report helios + cupid current firsts (post-toc_fixup state)
for nid in ('helios', 'cupid', 'math'):
    n = next((x for x in g['nodes'] if x['id'] == nid), None)
    if n and n.get('highlights'):
        h0 = n['highlights'][0]
        print(f"\n{nid} first [{h0.get('source_title','')[:40]}]: {h0['text'][:170]!r}")
        print(f"  audit: {h0.get('audit')}")

shutil.copy(GP, GP.with_suffix('.json.bakSurgery'))
json.dump(g, open(GP, 'w'), indent=1, ensure_ascii=False)
json.dump(led, open(LP, 'w'), indent=1, ensure_ascii=False)
print("\nwrote graph.json + ledger.json")
