#!/usr/bin/env python3
"""Fixup: replace TOC/heading-junk direct highlights with real prose.

Detects first highlights that are contents-page enumerations (roman-numeral
runs, 'CONTENTS', chapter listings) and re-selects a proper name-bearing prose
sentence for just those nodes.
"""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import FILES, SQMAP, positions, sentence_at, expand_span, junk_score, register_file_source, add_quote, GP, LP
from _audit_relevance import alias_patterns

TODAY = "2026-10-15"

TOC = re.compile(r"(?i)(\b[i]{1,3}\b\s*\.|\b[ivx]+\.\s).{0,60}?(\b[i]{1,3}\b\s*\.|\b[ivx]+\.\s)|contents\b|index\b|gutenberg")
NUMBERED = re.compile(r"(?i)\b(i{1,3}|iv|vi{0,3}|ix|xi{0,2})\.\s")

def is_tocish(text):
    if TOC.search(text):
        return True
    hits = len(NUMBERED.findall(text))
    return hits >= 2

g = json.load(open(GP))
ledger = json.load(open(LP))
byid = {n["id"]: n for n in g["nodes"]}
pats_of = {n["id"]: alias_patterns(n) for n in g["nodes"]}
POS = {}

def get_pos(nid):
    if nid not in POS:
        POS[nid] = {fp: positions(t, SQMAP[fp], pats_of[nid]) for fp, t in FILES.items()}
    return POS[nid]

def node_alias_in(text, pats):
    tc = " " + re.sub(r"[^a-z0-9]+", " ", text.lower()).strip() + " "
    tsq = re.sub(r"\s+", "", text.lower())
    for p in pats:
        if p["na"] in tc or (p["long"] and p["sq"] in tsq):
            return True
    return False

fixed = 0
for n in g["nodes"]:
    hls = n.get("highlights", [])
    if not hls or not hls[0].get("direct"):
        continue
    if not is_tocish(hls[0]["text"]):
        continue
    # re-select: first non-TOC name-bearing sentence
    best = None
    for fp, t in FILES.items():
        for k, (i, _a) in enumerate((get_pos(n["id"]).get(fp) or [])[:40]):
            snt = sentence_at(t, i)
            if len(snt) < 60:
                snt = expand_span(t, i, i + len(snt) + 60, max_fwd=600)
            if len(snt) < 60 or is_tocish(snt):
                continue
            if not node_alias_in(snt, pats_of[n["id"]]):
                continue
            score = 2.0 - junk_score(snt) + min(len(snt), 500) / 400.0 - 0.05 * k
            if best is None or score > best[0]:
                best = (score, fp, snt)
        if best and best[0] > 2.2:
            break
    if not best:
        print("  !! still only TOC for", n["id"])
        continue
    _s, fp, text = best
    sid = register_file_source(ledger, fp, TODAY)
    s = next(x for x in ledger["sources"] if x["id"] == sid)
    add_quote(ledger, sid, text, TODAY)
    first_key = re.sub(r"\W+", "", text.lower())[:80]
    kept = [h for h in hls[1:] if re.sub(r"\W+", "", h["text"].lower())[:80] != first_key]
    n["highlights"] = [{"text": text, "source_id": sid, "source_title": s["title"],
                        "source_url": s.get("url", ""), "direct": True}] + kept[:4]
    fixed += 1
    print(f"  fixed {n['id']}: {text[:100]!r}")

shutil.copy(GP, GP.with_suffix(".json.bak6"))
json.dump(g, open(GP, "w"), indent=1, ensure_ascii=False)
json.dump(ledger, open(LP, "w"), indent=1, ensure_ascii=False)
print(f"TOC fixup: {fixed} nodes")
