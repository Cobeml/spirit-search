#!/usr/bin/env python3
"""P2: rebuild node highlights so the FIRST highlight names the node.

For every flagged node: locate the best name-bearing sentence in its cited
sources (then the wider corpus), sentence-sliced, and make it the first
highlight. Existing highlights are kept after it (deduped, capped).
Nodes with no name-bearing text anywhere fall back to name-bearing ledger
quotes; author-nodes (mason-weems) stay indirect and remain flagged.
"""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import (FILES, SQMAP, positions, sentence_at, junk_score,
                        file_for_source, register_file_source, add_quote,
                        GP, LP, REPO)
from _audit_relevance import alias_patterns

TODAY = "2026-10-15"
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

def cited_files(node, ledger):
    out = []
    text = (node.get("essay") or "") + " " + (node.get("power_rationale") or "")
    for m in CIT.finditer(text):
        sid = int(m.group(1))
        s = next((x for x in ledger["sources"] if x["id"] == sid), None)
        if s:
            fp = file_for_source(s)
            if fp:
                out.append(fp)
    return out

def best_direct(node, preferred):
    """Best name-bearing sentence across files, preferred files first."""
    pos = get_pos(node["id"])
    best = None  # (score, fp, text, occ_index)
    order = preferred + [fp for fp in FILES if fp not in preferred]
    for fp in order:
        occ = pos.get(fp) or []
        for k, (i, _a) in enumerate(occ[:30]):
            snt = sentence_at(FILES[fp], i)
            if len(snt) < 60:
                # short roster/heading line: widen to the following sentence
                from _nameinfra import expand_span
                snt = expand_span(FILES[fp], i, i + len(snt) + 60, max_fwd=600)
            if len(snt) < 60 or node_alias_in(snt, pats_of[node["id"]]) is False:
                continue
            score = (2.0 - junk_score(snt)
                     + min(len(snt), 500) / 400.0
                     - 0.05 * k
                     + (0.6 if fp in preferred else 0))
            if best is None or score > best[0]:
                best = (score, fp, snt, k)
        if best and best[0] > 2.4 and fp in preferred:
            break  # strong hit in a cited source: stop
    return best

def node_alias_in(text, pats):
    tc = " " + re.sub(r"[^a-z0-9]+", " ", text.lower()).strip() + " "
    tsq = re.sub(r"\s+", "", text.lower())
    for p in pats:
        if p["na"] in tc or (p["long"] and p["sq"] in tsq):
            return True
    return False

changed = 0
for n in g["nodes"]:
    mode = (n.get("audit") or {}).get("mode")
    if mode in (None, "clean"):
        continue
    preferred = cited_files(n, ledger)
    best = best_direct(n, preferred)
    new_first = None
    if best:
        _score, fp, text, _k = best
        sid = register_file_source(ledger, fp, TODAY)
        s = next(x for x in ledger["sources"] if x["id"] == sid)
        add_quote(ledger, sid, text, TODAY)
        new_first = {"text": text, "source_id": sid,
                     "source_title": s["title"], "source_url": s.get("url", ""),
                     "direct": True}
    else:
        # fallback: name-bearing ledger quote of a cited source
        for sid in sorted({int(m.group(1)) for m in CIT.finditer((n.get("essay") or ""))}):
            s = next((x for x in ledger["sources"] if x["id"] == sid), None)
            if not s:
                continue
            for q in s.get("quotes", []):
                if node_alias_in(" " + re.sub(r"[^a-z0-9]+", " ", q["text"].lower()) + " ",
                                 pats_of[n["id"]]):
                    new_first = {"text": q["text"], "source_id": sid,
                                 "source_title": s["title"], "source_url": s.get("url", ""),
                                 "direct": True, "via": "ledger-quote"}
                    break
            if new_first:
                break
    if not new_first:
        print("  !! no direct sentence for", n["id"], "(stays flagged)")
        continue
    olds = n.get("highlights", [])
    first_key = re.sub(r"\W+", "", new_first["text"].lower())[:80]
    kept = [h for h in olds
            if re.sub(r"\W+", "", h["text"].lower())[:80] != first_key]
    n["highlights"] = [new_first] + kept[:4]
    changed += 1

shutil.copy(GP, GP.with_suffix(".json.bak4"))
json.dump(g, open(GP, "w"), indent=1, ensure_ascii=False)
json.dump(ledger, open(LP, "w"), indent=1, ensure_ascii=False)
print(f"rebuilt first highlight on {changed} nodes")
