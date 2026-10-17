#!/usr/bin/env python3
"""Round 2: (1) drop cross-tradition weems-sourced highlights (OCR caption
junk that gamed the squeezed matcher), (2) run _fix_excerpts with the
title-resolution fix, (3) _manual_firsts, (4) final audit."""
import json, re, shutil, sys
from pathlib import Path
sys.path.insert(0, 'research')

GP = Path('research/graph.json')
LP = Path('research/ledger.json')
g = json.load(open(GP))

WEEMS_OK = {"george-washington", "mason-weems", "thomas-jefferson", "henry-knox",
            "james-wilson", "charles-lee", "alexander-hamilton", "john-jay",
            "burr", "franklin", "weems-fabricators"}
dropped = []
for n in g['nodes']:
    if n['id'] in WEEMS_OK:
        continue
    keep = []
    for h in n.get('highlights', []):
        if 'weems' in (h.get('source_title', '') or '').lower():
            dropped.append((n['id'], h['text'][:80]))
            continue
        keep.append(h)
    n['highlights'] = keep
for e in g['edges']:
    frm_ok = e['from'] in WEEMS_OK or e['to'] in WEEMS_OK
    if frm_ok:
        continue
    e['excerpts'] = [x for x in e.get('excerpts', [])
                     if 'weems' not in (x.get('source_title', '') or '').lower()]
print("dropped cross-tradition weems items:", dropped)
shutil.copy(GP, GP.with_suffix('.json.bakR2'))
json.dump(g, open(GP, 'w'), indent=1, ensure_ascii=False)
