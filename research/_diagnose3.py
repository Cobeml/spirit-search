#!/usr/bin/env python3
"""Residual analysis: why would 89+43 still be mid-sentence after fix_quote?
Also: does the site search corpus (search.db chunks) suffer the same?"""
import json, re, sys, sqlite3
from pathlib import Path
sys.path.insert(0, 'research')
import _fix_excerpts as FX

g = json.load(open('research/graph.json'))
led = json.load(open('research/ledger.json'))
srcs = {s['id']: s for s in led['sources']}
cache = {}
def tfor(sid):
    if sid not in cache:
        cache[sid] = FX.load_text(srcs.get(sid, {})) if sid in srcs else None
    return cache[sid]

def midsent(s):
    s = s.strip()
    return bool(s) and (s[0].islower() or not re.search(r'[.!?"\u201d\)\]]$', s))

buckets = {'fixed_clean': 0, 'fixed_still_bad': 0, 'notfound': 0, 'notfound_mid': 0, 'nowitness': 0, 'unchanged_clean': 0}
samples = {'fixed_still_bad': [], 'notfound_mid': []}
for kind, items in [('H', [(n['id'], h) for n in g['nodes'] for h in n.get('highlights', [])]),
                    ('E', [(e['from'] + '|' + e['to'], x) for e in g['edges'] for x in e.get('excerpts', [])])]:
    for owner, it in items:
        sid = it.get('source_id')
        t = tfor(sid)
        if not t:
            buckets['nowitness'] += 1
            continue
        new = FX.fix_quote(it['text'], t)
        if new != it['text'] and 40 <= len(new) <= 3000:
            if midsent(new):
                buckets['fixed_still_bad'] += 1
                if len(samples['fixed_still_bad']) < 4: samples['fixed_still_bad'].append((kind, owner, new[:150]))
            else:
                buckets['fixed_clean'] += 1
        else:
            if midsent(it['text']):
                buckets['notfound_mid'] += 1
                if len(samples['notfound_mid']) < 4: samples['notfound_mid'].append((kind, owner, it['text'][:150]))
            else:
                buckets['unchanged_clean'] += 1

print("buckets:", json.dumps(buckets, indent=1))
for k, v in samples.items():
    print(f"\n--- {k} samples ---")
    for kind, owner, t in v:
        print(f"[{kind}] {owner}: {t!r}")

# search corpus check
print("\n=== search.db chunk quality ===")
db = sqlite3.connect('research/search.db')
row = db.execute("SELECT count(*) FROM chunks").fetchone()
print("chunk count:", row)
cols = [c[1] for c in db.execute("PRAGMA table_info(chunks)")]
print("cols:", cols)
sample = db.execute("SELECT text FROM chunks LIMIT 400").fetchall()
lower_chunks = sum(1 for (t,) in sample if sum(c.islower() for c in t if c.isalpha()) / max(1, sum(1 for c in t if c.isalpha())) > 0.95)
midsent_chunks = sum(1 for (t,) in sample if t.strip() and (t.strip()[0].islower() or not re.search(r'[.!?]"?\)\]?$', t.strip()[-3:])))
print(f"sampled 400 chunks: lowercase-normalized={lower_chunks}, mid-sentence-cut (start or end)={midsent_chunks}")
for (t,) in db.execute("SELECT text FROM chunks LIMIT 3").fetchall():
    print("  chunk sample:", t[:120])
# how does _search_build chunk?
