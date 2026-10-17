#!/usr/bin/env python3
"""Why are 113 mid-sentence quotes unlocatable? Try the whole corpus."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, 'research')
import _fix_excerpts as FX
import _textclean as TC

g = json.load(open('research/graph.json'))
led = json.load(open('research/ledger.json'))
srcs = {s['id']: s for s in led['sources']}

# load ALL evidence files once
ALL = {}
for p in sorted(Path('evidence').rglob('*')):
    if p.suffix in ('.txt', '.html') and p.stat().st_size > 200:
        ALL[str(p.relative_to('.'))] = TC.norm_file(p.read_text(errors='replace'))
NORMS = {}
def normed(fp):
    if fp not in NORMS:
        NORMS[fp] = FX.norm_with_map(ALL[fp])
    return NORMS[fp]

def longest_run(nq):
    runs = re.findall(r"[a-z0-9]{15,}", nq[5:]) or [""]
    return max(runs, key=len) if runs else ""

outcomes = {}
examples = {}
for kind, items in [('H', [(n['id'], h) for n in g['nodes'] for h in n.get('highlights', [])]),
                    ('E', [(e['from'] + '|' + e['to'], x) for e in g['edges'] for x in e.get('excerpts', [])])]:
    for owner, it in items:
        sid = it.get('source_id')
        resolved = FX.load_text(srcs.get(sid, {})) if sid in srcs else None
        if not resolved:
            continue  # nowitness, handled separately
        if FX.fix_quote(it['text'], resolved):
            continue  # locatable, fine
        nq = FX.norm_key(it['text'])
        if len(nq) < 30:
            continue
        run = longest_run(nq)
        hit_fp = hit_reason = None
        for fp in ALL:
            nt, _ = normed(fp)
            if len(run) >= 15 and nt.find(run) >= 0:
                hit_fp = fp
                hit_reason = f"run found in {fp} (len {len(run)})"
                break
        key = hit_reason.split(' (')[0] if hit_reason else "NOWHERE on disk"
        outcomes[key] = outcomes.get(key, 0) + 1
        if key not in examples:
            examples[key] = (kind, owner, sid, it['text'][:90], run[:40])

print("=== unlocatable outcomes (115ish expected) ===")
for k, v in sorted(outcomes.items(), key=lambda kv: -kv[1]):
    kind, owner, sid, t, run = examples[k]
    print(f"{v:4d}  {k}")
    print(f"      e.g. [{kind}] {owner} sid={sid}: {t!r}")
    print(f"      longest run: {run!r}")
