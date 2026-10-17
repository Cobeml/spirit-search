#!/usr/bin/env python3
"""Round 4: shrink-to-fit re-slice for over-long quotes, drop pure furniture,
with node rebuild for emptied nodes."""
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

ALL = {}
for p in sorted(Path('evidence').rglob('*')):
    if p.suffix in ('.txt', '.html') and p.stat().st_size > 200:
        ALL[str(p)] = TC.norm_file(p.read_text(errors='replace'))
NORM = {}
def normed(fp):
    if fp not in NORM:
        NORM[fp] = FX.norm_with_map(ALL[fp])
    return NORM[fp]

def shrink_fit(t, lo, hi, cap=2900):
    """expand to sentence bounds; if > cap, walk back to the last boundary."""
    s = TC._prev_boundary(t, lo) or 0
    e = TC._next_boundary(t, min(hi, len(t) - 1))
    if e is None:
        return None
    if e - s > cap:
        e2 = TC._prev_boundary(t, s + cap)
        if e2 is None or e2 <= s:
            e2 = s + cap
        e = e2
    out = t[s:e]
    return TC.scrub_slice(out) if out else None

def locate(nq):
    W = 40
    for fp in ALL:
        nt, pos = normed(fp)
        for off in (0, len(nq) // 2, max(0, len(nq) - W)):
            f = nq[off:off + W]
            if len(f) < 20:
                continue
            i = nt.find(f)
            if i >= 0:
                return fp, pos[i], i
    return None

def is_furniture(t):
    s = t.strip().lower()
    return bool(re.search(r'\.mw-parser-output|thumb\|right|sister project|'
                          r'^\(7\^|^1919\) has been followed', s)
                or re.match(r'^[\d\W]*introduction', s))

def bad(t):
    s = (t or '').strip()
    seg = bool(s) and (s[0].islower() or not re.search(r'[.!?\u201d\u2019"\)\]]$', s))
    junk = bool(re.search(r'[\u200b\u200c\ufeff\ufffd\x91\x92\x93\x94]', s)
                or 'project gutenberg' in s.lower()
                or 'digitized by the internet archive' in s.lower()
                or re.search(r'\.mw-parser-output|thumb\|right', s))
    return seg or junk

fixed = dropped = 0
drops = []
for n in g['nodes']:
    keep = []
    for h in n.get('highlights', []):
        if not bad(h['text']):
            keep.append(h)
            continue
        if is_furniture(h['text']):
            drops.append((n['id'], h['text'][:50]))
            dropped += 1
            continue
        nq = FX.norm_key(h['text'])
        hit = locate(nq) if len(nq) >= 30 else None
        new = None
        if hit:
            fp, o_start, _i = hit
            new = shrink_fit(ALL[fp], o_start, o_start + max(80, len(nq)))
            if new and (FX.norm_key(new)[:40] not in FX.norm_key(ALL[fp])) is False:
                pass
            # sanity: repaired slice must overlap the original quote
            if new:
                w = FX.norm_key(new)
                mid = nq[len(nq)//2 : len(nq)//2 + 30]
                if mid and mid not in w and nq[:30] not in w:
                    new = None
        if new and new != h['text']:
            h['text'] = new
            fixed += 1
            keep.append(h)
        elif not bad(h['text']):
            keep.append(h)
        else:
            drops.append((n['id'], 'UNFIXABLE-KEPT:' + h['text'][:40]))
            keep.append(h)   # keep unfixable for the review queue, do not lose data
    n['highlights'] = keep

# edges: same treatment, but never drop the last excerpt of an edge
for e in g['edges']:
    keep = []
    for x in e.get('excerpts', []):
        if not bad(x['text']):
            keep.append(x)
            continue
        nq = FX.norm_key(x['text'])
        hit = locate(nq) if len(nq) >= 30 else None
        new = None
        if hit:
            fp, o_start, _i = hit
            new = shrink_fit(ALL[fp], o_start, o_start + max(80, len(nq)))
            if new:
                w = FX.norm_key(new)
                mid = nq[len(nq)//2 : len(nq)//2 + 30]
                if mid and mid not in w and nq[:30] not in w:
                    new = None
        if new and new != x['text']:
            x['text'] = new
            fixed += 1
        keep.append(x)
    e['excerpts'] = keep

print(f"fixed {fixed}, furniture dropped {dropped}")
for d in drops:
    print("  drop:", d)
shutil.copy(GP, GP.with_suffix('.json.bakR4'))
json.dump(g, open(GP, 'w'), indent=1, ensure_ascii=False)
print("written")
