#!/usr/bin/env python3
"""DRY RUN of the patched _fix_excerpts against graph.json + ledger.json.
No writes. Reports the same buckets as the pre-patch baseline:
  baseline: fixed_clean 360, fixed_still_bad 20, notfound_mid 112, nowitness 110, unchanged_clean 257
"""
import json, re, sys
sys.path.insert(0, 'research')
import _fix_excerpts as FX
import _textclean as TC

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
    if not s:
        return True
    if re.match(r'^[\u2026\u2013\u2014-]\s*', s):
        return False  # ellipsis-lead is a deliberate excerpt convention? count separately
    return s[0].islower() or not re.search(r'[.!?"\u201d\u2019\)\]]$', s)

def junky(s):
    return bool(re.search(r'[\u200b\u200c\ufeff\ufffd\x93\x94\x92]', s)
                or 'digitized by the internet archive' in s.lower()
                or 'project gutenberg' in s.lower()
                or re.match(r'^\s*[\(\[]?l{1,2}\.\s*\d', s)
                or re.search(r'[.!?]"?\s+\d{1,4}\s+[A-Z]', s))

buckets = {}
samples = {'fixed_still_bad': [], 'notfound_mid': [], 'nowitness': []}
total = 0
for kind, items in [('H', [(n['id'], h) for n in g['nodes'] for h in n.get('highlights', [])]),
                    ('E', [(e['from'] + '|' + e['to'], x) for e in g['edges'] for x in e.get('excerpts', [])])]:
    for owner, it in items:
        total += 1
        sid = it.get('source_id')
        t = tfor(sid)
        if not t:
            buckets['nowitness'] = buckets.get('nowitness', 0) + 1
            if len(samples['nowitness']) < 3: samples['nowitness'].append((kind, owner, it['text'][:100]))
            continue
        new = FX.fix_quote(it['text'], t)
        if new and 40 <= len(new) <= 3000:
            if new != it['text']:
                if midsent(new) or junky(new):
                    buckets['fixed_still_bad'] = buckets.get('fixed_still_bad', 0) + 1
                    if len(samples['fixed_still_bad']) < 5: samples['fixed_still_bad'].append((kind, owner, new[:130]))
                else:
                    buckets['fixed_clean'] = buckets.get('fixed_clean', 0) + 1
            else:
                if midsent(new) or junky(new):
                    buckets['unchanged_but_bad'] = buckets.get('unchanged_but_bad', 0) + 1
                    if len(samples['notfound_mid']) < 5: samples['notfound_mid'].append((kind, owner, 'UNCHANGED: ' + new[:120]))
                else:
                    buckets['unchanged_clean'] = buckets.get('unchanged_clean', 0) + 1
        else:
            buckets['notfound'] = buckets.get('notfound', 0) + 1
            if midsent(it['text']) or junky(it['text']):
                buckets['notfound_mid'] = buckets.get('notfound_mid', 0) + 1
                if len(samples['notfound_mid']) < 8: samples['notfound_mid'].append((kind, owner, it['text'][:120]))

print("total items:", total)
print("buckets:", json.dumps(buckets, indent=1))
for k, v in samples.items():
    print(f"\n--- {k} ---")
    for kind, owner, t in v:
        print(f"[{kind}] {owner}: {t!r}")
