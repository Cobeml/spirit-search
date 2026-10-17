#!/usr/bin/env python3
"""Validate every evidence file: does its content match its filename?
Catches wrongly-saved downloads (e.g. a math text saved as weems_...)."""
import re
from pathlib import Path

def title_tokens(s):
    return {t for t in re.split(r"[^a-z0-9]+", s.lower()) if len(t) >= 4}

print(f"{'file':70s} {'gut-title?':8s} {'kw':3s} note")
for p in sorted(Path('evidence').rglob('*')):
    if p.suffix not in ('.txt', '.html') or p.stat().st_size < 200:
        continue
    raw = p.read_text(errors='replace')[:4000]
    name_toks = title_tokens(p.stem)
    m = re.search(r"(?:Project Gutenberg E(?:Book|Text) of|etext of)\s+(.{3,80}?)\r?\n", raw, re.I)
    gtitle = m.group(1) if m else ''
    # coherence: do >=2 filename tokens appear in the first 4000 chars?
    hits = sum(1 for t in name_toks if t in raw.lower())
    note = ''
    if gtitle:
        gt = title_tokens(gtitle)
        overlap = len(name_toks & gt)
        if overlap == 0:
            note = f'MISMATCH? gut-title={gtitle[:50]!r}'
    elif hits <= 0:
        note = 'no gutenberg title, no filename tokens in head'
    flag = 'X' if 'MISMATCH' in note or (hits == 0 and not gtitle) else ' '
    print(f"{flag} {str(p.relative_to('evidence')):68s} {'y' if gtitle else 'n':8s} {hits:3d} {note}")
