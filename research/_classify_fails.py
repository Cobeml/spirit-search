#!/usr/bin/env python3
"""Classify remaining seg/junk fails: which cite missing-witness sources
(fetch candidates) vs which cite on-disk files (unlocatable text)."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, 'research')
import _fix_excerpts as FX

g = json.load(open('research/graph.json'))
led = json.load(open('research/ledger.json'))
srcs = {s['id']: s for s in led['sources']}

def bad(t):
    s = (t or '').strip()
    seg = bool(s) and (s[0].islower() or not re.search(r'[.!?\u201d\u2019"\)\]]$', s))
    junk = bool(re.search(r'[\u200b\u200c\ufeff\ufffd\x91\x92\x93\x94]', s)
                or 'project gutenberg' in s.lower()
                or 'digitized by the internet archive' in s.lower()
                or re.match(r'^\s*[\(\[]?\s*(?:l{1,2}\.|\d{1,3}\.)\s*\d', s))
    return seg or junk

cache = {}
def resolves(sid):
    if sid not in cache:
        cache[sid] = bool(sid in srcs and FX.load_text(srcs[sid]))
    return cache[sid]

missing, unlocatable = {}, {}
for kind, items in [('H', [(n['id'], h) for n in g['nodes'] for h in n.get('highlights', [])]),
                    ('E', [(e['from'] + '|' + e['to'], x) for e in g['edges'] for x in e.get('excerpts', [])])]:
    for owner, it in items:
        if not bad(it.get('text', '')):
            continue
        sid = it.get('source_id')
        key = (kind, owner, sid)
        if not sid or not resolves(sid):
            s = srcs.get(sid, {})
            missing.setdefault((sid, s.get('title', '?')[:60], s.get('url', '')), []).append((kind, owner, it['text'][:60]))
        else:
            unlocatable.setdefault((sid, srcs[sid].get('title', '?')[:60]), []).append((kind, owner, it['text'][:60]))

print(f"=== MISSING WITNESS ({len(missing)} sources, {sum(len(v) for v in missing.values())} bad items) ===")
for (sid, title, url), v in sorted(missing.items(), key=lambda kv: kv[0][0]):
    print(f"sid={sid} items={len(v)} | {title} | {url[:90]}")
print(f"\n=== ON-DISK BUT UNLOCATABLE ({len(unlocatable)} sources, {sum(len(v) for v in unlocatable.values())} bad items) ===")
for (sid, title), v in sorted(unlocatable.items(), key=lambda kv: kv[0][0]):
    print(f"sid={sid} items={len(v)} | {title}")
    for kind, owner, t in v[:2]:
        print(f"    [{kind}] {owner}: {t!r}")
