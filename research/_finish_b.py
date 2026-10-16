#!/usr/bin/env python3
"""Finish the b-list: llwyd (wider window), boulton|watt (Bolton spelling),
hippocrates|asclepius (Oath via Wikisource/Adams)."""
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

def slice_at(fp, pattern, must_name, span_back=120, span_fwd=400, back=400, fwd=450):
    t = FILES[fp]
    for m in list(re.finditer(pattern, t))[:20]:
        s = expand_span(t, max(0, m.start() - span_back), m.start() + span_fwd, max_back=back, max_fwd=fwd)
        if len(s) < 60 or junk_score(s) > 0.55:
            continue
        if not all(aliases_ok(s, nid) for nid in must_name):
            continue
        return s
    return None

def find_edge(frm, to, ty):
    return next((e for e in g["edges"] if e["from"] == frm and e["to"] == to and e["type"] == ty), None)

JOBS = [
    ("llwyd", "manawyddan", "conflict",
     "evidence/_corpus/guest-mabinogion-1877-full.txt",
     r"llwyd.{0,900}manawyddan|manawyddan.{0,900}llwyd", ["llwyd", "manawyddan"],
     120, 500, 600, 700, None),
    ("matthew-boulton", "james-watt", "transmission",
     "evidence/_corpus/boswell-life-of-johnson-vol2.txt",
     r"bolton.{0,500}watt|watt.{0,500}bolton", ["matthew-boulton", "james-watt"],
     120, 500, 400, 700, None),
    ("hippocrates", "asclepius", "transmission",
     "evidence/_corpus/hippocratic-oath.txt",
     r"I SWEAR by Apollo the physician", ["asclepius"],
     20, 400, 200, 500,
     "the Oath is Hippocrates' own text; it names Aesculapius (Asclepius)"),
]
for frm, to, ty, fp, pat, must, sb, sf, b, f, note in JOBS:
    e = find_edge(frm, to, ty)
    if not e:
        print(f"?? missing edge {frm}->{to}")
        continue
    text = slice_at(fp, pat, must, sb, sf, b, f)
    if not text:
        print(f"MISS {frm}->{to}")
        continue
    sid = register_file_source(ledger, fp, TODAY)
    s = next(x for x in ledger["sources"] if x["id"] == sid)
    add_quote(ledger, sid, text, TODAY)
    e["excerpts"] = [{"text": text, "source_id": sid,
                      "source_title": s["title"], "source_url": s.get("url", "")}]
    e["source"] = f"[{sid}] {s['title']}"
    e["audit"] = {"ok": True, "mode": "fetched_witness"}
    if note:
        e["pairing_note"] = note
    print(f"ok {frm}->{to}: {text[:100]!r}")

shutil.copy(GP, GP.with_suffix(".json.bak9"))
json.dump(g, open(GP, "w"), indent=1, ensure_ascii=False)
json.dump(ledger, open(LP, "w"), indent=1, ensure_ascii=False)
