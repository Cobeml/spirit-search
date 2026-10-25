"""Read-only probe of _manual_firsts.py anchor behavior under the current
_textclean boundaries (2026-10-21). Replicates the pin logic for selected
OVERRIDES nodes, plus candidate replacement anchors for the Weems roster
nodes and fdr. Writes nothing."""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import FILES, junk_score, expand_span
from _audit_relevance import alias_patterns
import json

GP = Path(__file__).resolve().parent / 'graph.json'
g = json.load(open(GP))
byid = {n['id']: n for n in g['nodes']}
pats_of = {n['id']: alias_patterns(n) for n in g['nodes']}

TOCISH = re.compile(r"(?i)(\b[i]{1,3}\b\s*\.|\b[ivx]+\.\s).{0,60}?(\b[i]{1,3}\b\s*\.|\b[ivx]+\.\s)|\bcontents\b|comparison of .{0,40} with|digitized by the internet archive")


def sentence_pair(t, i):
    s = expand_span(t, max(0, i - 120), i + 400, max_back=400, max_fwd=450)
    if len(s) < 80:
        s = expand_span(t, max(0, i - 300), i + 500, max_back=1200, max_fwd=700)
    if len(s) < 80:
        s = expand_span(t, max(0, i - 200), i + 60, max_fwd=700)
    return s


def alias_ok(text, pats):
    tc = " " + re.sub(r"[^a-z0-9]+", " ", text.lower()).strip() + " "
    tsq = re.sub(r"\s+", "", text.lower())
    return any(p["na"] in tc or (p["long"] and p["sq"] in tsq) for p in pats)


FILEALIAS = {
    "weems": "evidence/washington/weems-life-of-washington-1800s-archive-full.txt",
    "fdr": "evidence/_corpus/fdr-first-inaugural.txt",
}

PROBE = [
    ("thomas-jefferson", "weems", [r"secretary of foreign aifairs", r"berkley, jefferson",
                                   r"washington prudently rallied around him the wisest"]),
    ("alexander-hamilton", "weems", [r"col\. hamilton, secretary of the treasury",
                                     r"washington prudently rallied around him the wisest"]),
    ("henry-knox", "weems", [r"gen\. knox, secretary of war",
                             r"washington prudently rallied around him the wisest"]),
    ("james-wilson", "weems", [r"james wilson", r"washington prudently rallied around him the wisest"]),
    ("charles-lee", "weems", [r"general lee.{0,40}said washington", r"for god.{0,20}sake, general lee"]),
    ("aaron-burr", "weems", [r"hamiltons and burrs"]),
    ("john-jay", "weems", [r"washington prudently rallied around him the wisest"]),
    ("edward-braddock", "weems", [r"braddock", r"general braddock"]),
    ("george-washington", "weems", [r"great washington was born"]),
    ("fdr", "fdr", [r"first inaugural address of franklin d\. roosevelt\s+saturday, march 4, 1933\s+i am certain",
                    r"first inaugural address of franklin d\. roosevelt"]),
]

for nid, fkey, patterns in PROBE:
    fp = FILEALIAS[fkey]
    t = FILES.get(fp)
    if t is None:
        print(f"!! {nid}: file missing {fp}")
        continue
    tl = t.lower()
    print('=' * 72)
    print(nid)
    for pat in patterns:
        hit = False
        for m in re.finditer(pat, tl):
            s = sentence_pair(t, m.start())
            ok_len = len(s) >= 60
            ok_toc = not TOCISH.search(s)
            ok_junk = junk_score(s) <= 0.55
            ok_alias = alias_ok(s, pats_of[nid])
            print(f"  [{ 'PIN' if all((ok_len, ok_toc, ok_junk, ok_alias)) else 'SKIP' }] "
                  f"len={ok_len} toc={ok_toc} junk={ok_junk} alias={ok_alias}")
            print(f"      {s[:170]!r}")
            hit = True
            break
        if not hit:
            print(f'  [NO-HIT] {pat!r}')
