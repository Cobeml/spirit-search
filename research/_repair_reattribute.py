#!/usr/bin/env python3
"""Repair pass for remaining bad quotes:
1. Cross-file re-attribution: for each bad quote, locate its text anywhere in
   evidence/ (middle-out window scan); if found in a file other than the
   cited source's resolution, re-slice there and re-point source_id/title/url
   (registering the file as a ledger source when needed).
2. Drop-and-reselect list (title-page/engraving junk): removed; the audit +
   rebuild pass will regenerate firsts; secondaries simply disappear.
3. Unresolved leftovers get review: {status:'needs_witness'} for Cobe.
"""
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

# junk titles/front-matter to drop outright (verified by inspection)
DROP_PREFIX = [
    ("george-washington", "\\-'-\"&"), ("mason-weems", "\\-'-\"&"),
    ("alexander-hamilton", "LONDON : SIMPKIN"),
    ("taliesin", "ady charlotte guest vol"),
    ("fdr", "thumb|right|"),
]
dropped = []
for n in g['nodes']:
    keep = []
    for h in n.get('highlights', []):
        hit = any(n['id'] == nid and h['text'].lstrip().startswith(pre)
                  for nid, pre in DROP_PREFIX)
        if hit:
            dropped.append((n['id'], h['text'][:60]))
        else:
            keep.append(h)
    n['highlights'] = keep
print("dropped junk:", dropped)

# load all files once
ALL = {}
for p in sorted(Path('evidence').rglob('*')):
    if p.suffix in ('.txt', '.html') and p.stat().st_size > 200:
        ALL[str(p)] = TC.norm_file(p.read_text(errors='replace'))
NORM = {}
def normed(fp):
    if fp not in NORM:
        NORM[fp] = FX.norm_with_map(ALL[fp])
    return NORM[fp]

def locate(nq):
    """find quote across ALL files; return (fp, o_start, o_end) or None"""
    W = 40
    for fp in ALL:
        nt, pos = normed(fp)
        for off in (0, len(nq) // 2, max(0, len(nq) // 2 - 60), max(0, len(nq) - W)):
            f = nq[off:off + W]
            if len(f) < 20:
                continue
            i = nt.find(f)
            if i >= 0:
                return fp, pos[i], i
    return None

def register(fp):
    """register file as ledger source, return sid + source dict"""
    stem = Path(fp).stem
    for s in led['sources']:
        if stem in (s.get('title') or '') and 'local, unregistered' in (s.get('title') or ''):
            return s['id'], s
    new_id = max(s['id'] for s in led['sources']) + 1
    s = {"id": new_id, "title": f"Evidence file {stem} (local, unregistered witness)",
         "url": "", "quotes": []}
    led['sources'].append(s)
    return new_id, s

# cluster slug for saving nothing new here; re-attribution only
fixed = still_bad = []
fixed_ct = still_ct = 0
def repair(text, sid):
    """returns (new_text, new_sid, new_title) or (None, sid, None)"""
    nq = FX.norm_key(text)
    if len(nq) < 30:
        return None, sid, None
    hit = locate(nq)
    if not hit:
        return None, sid, None
    fp, o_start, _ni = hit
    new = TC.slice_clean(ALL[fp], o_start, o_start + max(80, len(nq)))
    if not new or not (40 <= len(new) <= 3000):
        return None, sid, None
    # sanity: new text must contain a distinctive window of the original
    w = FX.norm_key(new)
    if nq[len(nq)//2 : len(nq)//2 + 30] not in w and nq[:30] not in w:
        return None, sid, None
    if fp in [str(p) for p in []]:
        pass
    # source: prefer an existing ledger source for that file
    nsid, s = register(fp)
    return new, nsid, s['title']

items = []
for n in g['nodes']:
    for h in n.get('highlights', []):
        items.append((n['id'], 'H', h))
for e in g['edges']:
    for x in e.get('excerpts', []):
        items.append((e['from'] + '|' + e['to'], 'E', x))

def bad(t):
    s = (t or '').strip()
    seg = bool(s) and (s[0].islower() or not re.search(r'[.!?\u201d\u2019"\)\]]$', s))
    junk = bool(re.search(r'[\u200b\u200c\ufeff\ufffd\x91\x92\x93\x94]', s)
                or 'project gutenberg' in s.lower()
                or 'digitized by the internet archive' in s.lower()
                or re.search(r'\.mw-parser-output|thumb\|right', s))
    return seg or junk

for owner, kind, it in items:
    if not bad(it.get('text', '')):
        continue
    new, nsid, ntitle = repair(it['text'], it.get('source_id'))
    if new:
        it['text'] = new
        if nsid != it.get('source_id'):
            it['source_id'] = nsid
            it['source_title'] = ntitle
            s = next(x for x in led['sources'] if x['id'] == nsid)
            it['source_url'] = s.get('url', '')
        fixed_ct += 1
    else:
        still_ct += 1
        still_bad.append((kind, owner, it.get('source_id'), it['text'][:60]))

print(f"repaired {fixed_ct}, unrepairable {still_ct}")
print("\n=== UNREPAIRABLE (for Cobe a/b/c) ===")
for kind, owner, sid, t in still_bad:
    print(f"[{kind}] {owner} (sid={sid}): {t!r}")

shutil.copy(GP, GP.with_suffix('.json.bakR3'))
shutil.copy(LP, LP.with_suffix('.json.bakR3'))
json.dump(g, open(GP, 'w'), indent=1, ensure_ascii=False)
json.dump(led, open(LP, 'w'), indent=1, ensure_ascii=False)
print("written")
