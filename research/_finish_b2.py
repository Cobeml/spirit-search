#!/usr/bin/env python3
"""Finish b-list v2 with corrected patterns + llwyd same-scene pair."""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import FILES, expand_span, junk_score, register_file_source, add_quote, GP, LP
from _audit_relevance import alias_patterns

TODAY = "2026-10-15"
g = json.load(open(GP))
ledger = json.load(open(LP))
byid = {n["id"]: n for n in g["nodes"]}
pats_of = {n["id"]: alias_patterns(n) for n in g["nodes"]}

def aliases_ok(text, nid):
    tc = " " + re.sub(r"[^a-z0-9]+", " ", text).strip() + " "
    tsq = re.sub(r"\s+", "", text)
    return any(p["na"] in tc or (p["long"] and p["sq"] in tsq) for p in pats_of[nid])

def slice_at(fp, pattern, must_name):
    t = FILES[fp]
    for m in list(re.finditer(pattern, t))[:20]:
        s = expand_span(t, max(0, m.start() - 120), m.start() + 400, max_back=400, max_fwd=450)
        if len(s) < 60 or junk_score(s) > 0.55:
            continue
        if not all(aliases_ok(s, nid) for nid in must_name):
            continue
        return s
    return None

def set_ex(fp, e, text, mode, note=None):
    sid = register_file_source(ledger, fp, TODAY)
    s = next(x for x in ledger["sources"] if x["id"] == sid)
    add_quote(ledger, sid, text, TODAY)
    e["excerpts"] = [{"text": text, "source_id": sid, "source_title": s["title"],
                      "source_url": s.get("url", "")}]
    e["source"] = f"[{sid}] {s['title']}"
    e["audit"] = {"ok": True, "mode": mode}
    if note:
        e["pairing_note"] = note

def find_edge(frm, to, ty):
    return next((e for e in g["edges"] if e["from"] == frm and e["to"] == to and e["type"] == ty), None)

OATH = "evidence/_corpus/hippocratic-oath.txt"
EBW = "evidence/_corpus/eb1911-watt.txt"
V3 = "evidence/rhiannon/guest-mabinogion-vol3-gutenberg.txt"

# 1. Oath (lowercase pattern; FILES text is normalized)
e = find_edge("hippocrates", "asclepius", "transmission")
text = slice_at(OATH, r"i swear by apollo the physician", ["asclepius"])
if text and e:
    set_ex(OATH, e, text, "fetched_witness",
           "the Oath is Hippocrates' own text; it names Aesculapius (Asclepius)")
    print("ok hippocrates->asclepius:", repr(text[:100]))
else:
    print("MISS hippocrates->asclepius")

# 2. Boulton & Watt from EB1911 Watt
e = find_edge("matthew-boulton", "james-watt", "transmission")
text = slice_at(EBW, r"boulton & watt|boulton.{0,300}watt", ["matthew-boulton", "james-watt"])
if text and e:
    set_ex(EBW, e, text, "fetched_witness")
    print("ok boulton->watt:", repr(text[:100]))
else:
    print("MISS boulton->watt")

# 3. Llwyd + Manawyddan: same scene in Guest vol3, names 2.6k apart -> two-part quote
e = find_edge("llwyd", "manawyddan", "conflict")
t3 = FILES[V3]
m = re.search(r"i am llwyd the son of kilcoed", t3)
if e and m:
    from_side = expand_span(t3, max(0, m.start() - 120), m.start() + 300, max_back=300, max_fwd=400)
    # nearest Manawyddan mention before the speech
    j = t3.rfind("manawyddan", 0, m.start())
    to_side = expand_span(t3, max(0, j - 200), j + 60, max_back=300, max_fwd=400)
    sid = register_file_source(ledger, V3, TODAY)
    s = next(x for x in ledger["sources"] if x["id"] == sid)
    for txt in (from_side, to_side):
        add_quote(ledger, sid, txt, TODAY)
    e["excerpts"] = [
        {"text": from_side, "source_id": sid, "source_title": s["title"],
         "source_url": s.get("url", ""), "side": "from"},
        {"text": to_side, "source_id": sid, "source_title": s["title"],
         "source_url": s.get("url", ""), "side": "to"}]
    e["source"] = f"[{sid}] {s['title']}"
    e["audit"] = {"ok": True, "mode": "same_scene"}
    e["pairing_note"] = "one scene in Guest's translation; the two speeches sit 2,600 characters apart"
    print("ok llwyd->manawyddan (same scene)")
else:
    print("MISS llwyd->manawyddan")

shutil.copy(GP, GP.with_suffix(".json.bak10"))
json.dump(g, open(GP, "w"), indent=1, ensure_ascii=False)
json.dump(ledger, open(LP, "w"), indent=1, ensure_ascii=False)
