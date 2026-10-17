#!/usr/bin/env python3
"""P3: re-slice flagged edges at the tightest both-name co-occurrence.

For every edge the audit flagged (excerpt does not name both endpoints) that
the probe located a co-occurrence window for: cut a sentence-bounded passage
centered on the window (preferred: the edge's originally cited source's file),
verify both names appear, replace the edge's excerpts, update the witness
reference when the slice moved to a different source, and register the quote.
"""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import (FILES, SQMAP, positions, expand_span, junk_score,
                        file_for_source, register_file_source, add_quote,
                        GP, LP)
from _audit_relevance import alias_patterns

TODAY = "2026-10-15"
WINDOW = 600
CIT = re.compile(r"\[(\d+)\]")

g = json.load(open(GP))
ledger = json.load(open(LP))
byid = {n["id"]: n for n in g["nodes"]}
pats_of = {n["id"]: alias_patterns(n) for n in g["nodes"]}
POS = {}

def get_pos(nid):
    if nid not in POS:
        POS[nid] = {fp: positions(t, SQMAP[fp], pats_of[nid]) for fp, t in FILES.items()}
    return POS[nid]

def names_in(text, pats):
    tc = " " + re.sub(r"[^a-z0-9]+", " ", text.lower()).strip() + " "
    tsq = re.sub(r"\s+", "", text.lower())
    for p in pats:
        if p["na"] in tc or (p["long"] and p["sq"] in tsq):
            return True
    return False

def best_window(pfa, pat):
    """tightest (dist, fp, i, j) across files; caller passes preference first."""
    best = None
    for fp, t in FILES.items():
        af = get_pos(pfa["id"])[fp]
        at = get_pos(pat["id"])[fp]
        if not af or not at:
            continue
        j = 0
        for i, _ in af:
            while j < len(at) and at[j][0] < i:
                j += 1
            for k in (j - 1, j):
                if 0 <= k < len(at):
                    d = abs(at[k][0] - i)
                    if d <= WINDOW and (best is None or d < best[0]):
                        best = (d, fp, i, at[k][0])
    return best

fixed = skipped = 0
for e in g["edges"]:
    if e.get("audit", {}).get("ok"):
        continue
    frm, to = byid[e["from"]], byid[e["to"]]
    # preference: originally cited source's file(s) first
    preferred = []
    for m in CIT.finditer(e.get("source", "")):
        sid = int(m.group(1))
        s = next((x for x in ledger["sources"] if x["id"] == sid), None)
        if s:
            fp = file_for_source(s)
            if fp:
                preferred.append(fp)
    global_best = best_window(frm, to)
    if not global_best:
        skipped += 1
        continue
    d, fp, i, jpos = global_best
    in_pref = fp in preferred
    # slice around the pair, sentence-bounded
    lo = min(i, jpos) - 80
    hi = max(i, jpos) + 380
    text = expand_span(FILES[fp], max(0, lo), hi, max_fwd=700)
    if not (names_in(text, pats_of[e["from"]]) and names_in(text, pats_of[e["to"]])):
        # retry tighter
        text = expand_span(FILES[fp], min(i, jpos) - 40, max(i, jpos) + 200, max_fwd=400)
    if not (names_in(text, pats_of[e["from"]]) and names_in(text, pats_of[e["to"]])):
        print("  !! could not verify pair for", e["from"], "->", e["to"])
        skipped += 1
        continue
    sid = register_file_source(ledger, fp, TODAY)
    s = next(x for x in ledger["sources"] if x["id"] == sid)
    add_quote(ledger, sid, text, TODAY)
    e["excerpts"] = [{"text": text, "source_id": sid,
                      "source_title": s["title"], "source_url": s.get("url", "")}]
    if not in_pref and preferred:
        e["source"] = f"[{sid}] {s['title']}"  # witness moved; cite what the quote is from
    e.setdefault("review", {})["resliced"] = TODAY
    fixed += 1

shutil.copy(GP, GP.with_suffix(".json.bak5"))
json.dump(g, open(GP, "w"), indent=1, ensure_ascii=False)
json.dump(ledger, open(LP, "w"), indent=1, ensure_ascii=False)
print(f"re-sliced {fixed} edges, skipped {skipped}")
