#!/usr/bin/env python3
"""Apply Cobe's rulings on the 37 flagged edges + witness fetches.

(b) re-slice at the new witnesses; (d) lilith identification edges re-sliced
with the node's own 'phantom maid' label; (c) delete the five approved kills;
(a) everything else becomes two-sided (one witness quote per endpoint) with a
pairing note. Also: alias fixes (Bolton spelling, phantom maid), node
first-highlight fixes from the new witnesses, Weems indirect marker.
"""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import (FILES, SQMAP, positions, expand_span, junk_score,
                        file_for_source, register_file_source, add_quote, GP, LP)
from _audit_relevance import alias_patterns

TODAY = "2026-10-15"

g = json.load(open(GP))
ledger = json.load(open(LP))
byid = {n["id"]: n for n in g["nodes"]}
pats_of = {n["id"]: alias_patterns(n) for n in g["nodes"]}

def aliases_ok(text, nid):
    tc = " " + re.sub(r"[^a-z0-9]+", " ", text).strip() + " "
    tsq = re.sub(r"\s+", "", text)
    return any(p["na"] in tc or (p["long"] and p["sq"] in tsq)
               for p in pats_of[nid])

def slice_at(fp, pattern, must_name=None, max_hits=20):
    t = FILES[fp]
    for m in list(re.finditer(pattern, t))[:max_hits]:
        s = expand_span(t, max(0, m.start() - 120), m.start() + 400,
                        max_back=400, max_fwd=450)
        if len(s) < 60 or junk_score(s) > 0.55:
            continue
        if must_name and not all(aliases_ok(s, nid) for nid in must_name):
            continue
        return s
    return None

def source_for(fp):
    sid = register_file_source(ledger, fp, TODAY)
    s = next(x for x in ledger["sources"] if x["id"] == sid)
    return sid, s

def set_excerpt(edge, fp, text, mode, note=None):
    sid, s = source_for(fp)
    add_quote(ledger, sid, text, TODAY)
    edge["excerpts"] = [{"text": text, "source_id": sid,
                         "source_title": s["title"], "source_url": s.get("url", "")}]
    edge["source"] = f"[{sid}] {s['title']}"
    edge["audit"] = {"ok": True, "mode": mode}
    if note:
        edge["pairing_note"] = note
        edge["pairing_note"] = note

def two_sided(edge):
    a, b = byid[edge["from"]], byid[edge["to"]]
    ex = []
    for side, n in (("from", a), ("to", b)):
        h = n.get("highlights") or []
        if h:
            ex.append({"text": h[0]["text"],
                       "source_title": h[0].get("source_title", ""),
                       "source_url": h[0].get("source_url", ""),
                       "source_id": h[0].get("source_id"), "side": side})
    edge["excerpts"] = ex
    edge["pairing_note"] = "witnesses describe each figure separately; the pairing is the essay's claim"
    edge["audit"] = {"ok": True, "mode": "two_sided"}

FP = {k: f"evidence/_corpus/{k}" for k in (
    "virgil-aeneid-dryden.txt", "hippocratic-oath.txt",
    "guest-mabinogion-1877-full.txt", "boswell-life-of-johnson-vol2.txt",
    "fdr-first-inaugural.txt", "eb1911-joule.txt", "eb1911-faraday.txt",
    "eb1911-ampere.txt", "eb1911-newton.txt", "eb1911-watt.txt",
    "eb1911-adam-smith.txt", "livy1-roberts.txt")}

def find_edge(frm, to, ty):
    return next((e for e in g["edges"]
                 if e["from"] == frm and e["to"] == to and e["type"] == ty), None)

log = []

# ---- (c) kills ----
KILLS = [("eve", "agrimus", "analogy"), ("baldr", "machaon", "analogy"),
         ("thor", "volundr", "analogy"), ("newton", "minerva", "analogy"),
         ("sulla", "cincinnatus", "conflict")]
for frm, to, ty in KILLS:
    e = find_edge(frm, to, ty)
    if e:
        g["edges"].remove(e)
        log.append(f"killed {frm}->{to}")

# ---- (b) re-slices at new witnesses ----
B = [
    ("sibyl", "apollo", "transmission", "virgil-aeneid-dryden.txt",
     r"sibyl.{0,400}phoebus|phoebus.{0,400}sibyl", ["sibyl", "apollo"], None),
    ("juno", "erinyes", "interaction", "virgil-aeneid-dryden.txt",
     r"juno.{0,500}(allecto|furie|furies)|allecto.{0,500}juno", ["juno", "erinyes"], None),
    ("hippocrates", "asclepius", "transmission", "hippocratic-oath.txt",
     r"I swear by Apollo the physician and Asclepius", ["asclepius"],
     "the Oath is Hippocrates' own text; it names Asclepius"),
    ("llwyd", "manawyddan", "conflict", "guest-mabinogion-1877-full.txt",
     r"llwyd.{0,400}manawyddan|manawyddan.{0,400}llwyd", ["llwyd", "manawyddan"], None),
    ("matthew-boulton", "james-watt", "transmission", "boswell-life-of-johnson-vol2.txt",
     r"boulton.{0,400}watt|watt.{0,400}boulton", ["matthew-boulton", "james-watt"], None),
    ("faraday", "benjamin-franklin", "transmission", "eb1911-faraday.txt",
     r"franklin", ["faraday", "benjamin-franklin"], None),
    ("ampere", "faraday", "transmission", "eb1911-ampere.txt",
     r"faraday", ["ampere", "faraday"], None),
    ("joule", "james-watt", "transmission", "eb1911-joule.txt",
     r"watt", ["joule", "james-watt"], None),
]
for frm, to, ty, fkey, pat, must, note in B:
    e = find_edge(frm, to, ty)
    if not e:
        log.append(f"?? edge missing {frm}->{to}")
        continue
    text = slice_at(FP[fkey], pat, must)
    if text:
        set_excerpt(e, FP[fkey], text, "fetched_witness", note)
        log.append(f"b-fixed {frm}->{to}: {text[:70]!r}")
    else:
        log.append(f"b-MISS {frm}->{to} (pattern/verify failed)")

# ---- (d) lilith identification edges ----
for frm, to, ty in [("gilgamesh", "lilith", "conflict"),
                    ("inana", "lilith", "interaction"),
                    ("anzud-bird", "lilith", "interaction")]:
    e = find_edge(frm, to, ty)
    if not e:
        continue
    text = slice_at("evidence/lilith/etcsl-gen-1-8-1-4.html",
                    r"phantom maid", [frm, "lilith"])
    if text:
        set_excerpt(e, "evidence/lilith/etcsl-gen-1-8-1-4.html", text, "identification",
                    "the witness says 'the phantom maid'; Lilith is this graph's identification")
        log.append(f"d-fixed {frm}->{to}: {text[:70]!r}")
    else:
        log.append(f"d-MISS {frm}->{to}")

# ---- (a) two-sided for everything still flagged ----
for e in g["edges"]:
    if e.get("audit", {}).get("ok"):
        continue
    two_sided(e)
    log.append(f"two-sided {e['from']}->{e['to']}")

# ---- node first-highlight fixes at the new witnesses ----
NODE_FIX = [
    ("james-watt", "eb1911-watt.txt", r"james watt|watt, james|james prescott watt"),
    ("adam-smith", "eb1911-adam-smith.txt", r"adam smith"),
    ("fdr", "fdr-first-inaugural.txt", r"franklin delano roosevelt"),
    ("joule", "eb1911-joule.txt", r"joule"),
    ("newton", "eb1911-newton.txt", r"isaac newton|sir isaac"),
    ("faraday", "eb1911-faraday.txt", r"michael faraday"),
    ("ampere", "eb1911-ampere.txt", r"ampere"),
    ("victory", "theog", None),  # special: theogony
    ("tiberinus", "livy1-roberts.txt", r"tiberinus"),
    ("fama", "virgil-aeneid-dryden.txt", r"fama|rumor"),
    ("sibyl", "virgil-aeneid-dryden.txt", r"cumaean sibyl|the sibyl"),
]
THEOG = "evidence/epimetheus/hesiod-evelynwhite-gutenberg348.txt"
for nid, fkey, pat in NODE_FIX:
    n = byid[nid]
    if nid == "victory":
        text = slice_at(THEOG, r"styx the daughter of ocean was joined to pallas",
                        ["victory"])
    else:
        text = slice_at(FP[fkey], pat, [nid])
    if not text:
        log.append(f"n-MISS {nid}")
        continue
    fp = THEOG if nid == "victory" else FP[fkey]
    sid, s = source_for(fp)
    add_quote(ledger, sid, text, TODAY)
    key = re.sub(r"\W+", "", text.lower())[:80]
    kept = [h for h in n.get("highlights", [])
            if re.sub(r"\W+", "", h["text"].lower())[:80] != key]
    n["highlights"] = [{"text": text, "source_id": sid, "source_title": s["title"],
                        "source_url": s.get("url", ""), "direct": True,
                        "manual": True}] + kept[:4]
    log.append(f"n-fixed {nid}: {text[:70]!r}")

# ---- Weems: indirect marker + clean first highlight ----
nw = byid["mason-weems"]
plough = next((q for q in next(s for s in ledger["sources"] if s["id"] == 15)["quotes"]
               if "plough" in q["text"]), None)
if plough:
    s15 = next(s for s in ledger["sources"] if s["id"] == 15)
    nw["highlights"] = [{"text": plough["text"], "source_id": 15,
                         "source_title": s15["title"], "source_url": s15.get("url", ""),
                         "direct": False, "via": "authorial",
                         "note": "authors do not name themselves; witness is Weems' own book"}] + \
                        [h for h in nw.get("highlights", [])
                         if h["text"][:60] != plough["text"][:60]][:4]
    log.append("n-fixed mason-weems (authorial/indirect)")

shutil.copy(GP, GP.with_suffix(".json.bak8"))
json.dump(g, open(GP, "w"), indent=1, ensure_ascii=False)
json.dump(ledger, open(LP, "w"), indent=1, ensure_ascii=False)
print("\n".join(log))
print(f"edges now: {len(g['edges'])}")
