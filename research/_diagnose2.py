#!/usr/bin/env python3
"""Deep diagnosis: where do bad highlights come from, and what would fix them?

1. Classify each highlight/excerpt: lowercase-normalized (P2/P3 artifact) vs cased.
2. Dry-run _fix_excerpts.fix_quote on every highlight+excerpt; measure fix rate
   and how many would STILL be mid-sentence after the fix.
3. Locate junk chars (\\x93, \\u200b, boilerplate) in the raw evidence files.
"""
import json, re, sys, collections
from pathlib import Path
sys.path.insert(0, 'research')
import _fix_excerpts as FX

REPO = Path('.')
g = json.load(open('research/graph.json'))
led = json.load(open('research/ledger.json'))
srcs = {s['id']: s for s in led['sources']}

def is_lower_artifact(t):
    """Heuristic: the P2/P3 path stored text from norm_file which lowercases."""
    letters = [c for c in t if c.isalpha()]
    if not letters:
        return False
    return sum(c.islower() for c in letters) / len(letters) > 0.95

hl, ex = [], []
for n in g['nodes']:
    for h in n.get('highlights', []):
        hl.append((n['id'], h))
for e in g['edges']:
    for x in e.get('excerpts', []):
        ex.append((e['from'] + '|' + e['to'], x))

print(f"highlights={len(hl)} excerpts={len(ex)}")
lc_h = sum(1 for _, h in hl if is_lower_artifact(h['text']))
lc_e = sum(1 for _, x in ex if is_lower_artifact(x['text']))
print(f"lowercase-artifact (P2/P3 norm_file slices): highlights={lc_h} excerpts={lc_e}")

# --- dry-run the fixer ---
cache = {}
def tfor(sid):
    if sid not in cache:
        s = srcs.get(sid, {})
        cache[sid] = FX.load_text(s) if sid in srcs else None
    return cache[sid]

def post_fix_stats(items, label):
    would_change = still_midsent = 0
    no_witness = 0
    for owner, it in items:
        sid = it.get('source_id')
        t = tfor(sid)
        if not t:
            no_witness += 1
            continue
        new = FX.fix_quote(it['text'], t)
        if new != it['text'] and 40 <= len(new) <= 3000:
            would_change += 1
            s2 = new.strip()
            if s2[0].islower() or not re.search(r'[.!?"\u201d\)\]]$', s2):
                still_midsent += 1
        else:
            s2 = it['text'].strip()
            if s2 and (s2[0].islower() or not re.search(r'[.!?"\u201d\)\]]$', s2)):
                still_midsent += 1
    print(f"{label}: fixer would change {would_change}/{len(items)}; still mid-sentence after fix: {still_midsent}; no on-disk witness: {no_witness}")

post_fix_stats(hl, 'HIGHLIGHTS')
post_fix_stats(ex, 'EXCERPTS')

# --- why does sentence expansion fail on lowercase text? ---
sample = "Now Zeus, king of the gods, made metis his wife first, and she was wisest among gods and mortal men. But when she was about to bring forth"
low = sample.lower()
m = list(FX.SENT_END.finditer(low))
print(f"\nSENT_END matches on lowercased sample: {len(m)} (case preserved would be 1)")
m2 = list(FX.SENT_END.finditer(sample))
print(f"SENT_END matches on original-case sample: {len(m2)}")

# --- junk char provenance: which raw files carry mojibake/boilerplate? ---
print("\n=== junk provenance in raw evidence files ===")
pats = {
    'cp1252_leftquote(\\x93)': '\x93',
    'zero_width(\\u200b)': '\u200b',
    'replacement(\\ufffd)': '\ufffd',
    'ia_boilerplate': 'digitized by the internet archive',
    'gutenberg_boilerplate': 'Project Gutenberg',
    'superscript_footnote': '[\u00b9\u00b2\u00b3]',
}
for p in sorted(Path('evidence').rglob('*')):
    if not p.is_file() or p.suffix not in ('.txt', '.html'):
        continue
    try:
        raw = p.read_text(errors='replace')
    except Exception:
        continue
    found = [name for name, pat in pats.items() if re.search(pat, raw)]
    if found:
        print(f"  {p}: {', '.join(found)}")
