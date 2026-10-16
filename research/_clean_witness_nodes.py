#!/usr/bin/env python3
"""Clean witness files (EB1911 css/nav prefix, FDR wikitext) and re-slice
the affected node first-highlights at proper narrative anchors."""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import FILES, expand_span, junk_score, register_file_source, add_quote, GP, LP, REPO
import importlib
import _nameinfra

REPO = Path(__file__).resolve().parent.parent
TODAY = "2026-10-15"

# ---- 1. clean the raw evidence files on disk ----
EB = {
    "eb1911-joule.txt": r"JOULE, JAMES PRESCOTT",
    "eb1911-faraday.txt": r"FARADAY, MICHAEL",
    "eb1911-ampere.txt": r"AMP\u00c8RE, ANDR\u00c9 MARIE|AMPÈRE, ANDRÉ MARIE|AMP",
    "eb1911-newton.txt": r"NEWTON, SIR ISAAC",
    "eb1911-watt.txt": r"WATT, JAMES",
    "eb1911-adam-smith.txt": r"SMITH, ADAM",
}
for fn, marker in EB.items():
    p = REPO / "evidence" / "_corpus" / fn
    raw = p.read_text(errors="replace")
    m = re.search(marker, raw)
    if m:
        cleaned = raw[m.start():]
        # drop trailing wikisource footer if present
        cleaned = re.split(r"\s*----+\s*", cleaned)[0]
        p.write_text(cleaned)
        print(f"cleaned {fn}: {len(raw)} -> {len(cleaned)}")
    else:
        print(f"!! marker not found in {fn}; head: {raw[:120]!r}")

p = REPO / "evidence" / "_corpus" / "fdr-first-inaugural.txt"
raw = p.read_text(errors="replace")
t = re.sub(r"\{\{[^{}]*\}\}", " ", raw)
t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", t)
t = re.sub(r"\s+", " ", t).strip()
p.write_text(t)
print("cleaned fdr-first-inaugural.txt:", len(raw), "->", len(t))

# ---- 2. reload FILES with cleaned content ----
importlib.reload(_nameinfra)
from _nameinfra import FILES as F2, expand_span as es2, register_file_source as rfs2, add_quote as aq2

g = json.load(open(GP))
ledger = json.load(open(LP))
byid = {n["id"]: n for n in g["nodes"]}

def fix_first(nid, fp, pattern, span_back=120, span_fwd=400, back=400, fwd=450):
    n = byid[nid]
    t = F2[fp]
    m = re.search(pattern, t)
    if not m:
        print(f"  !! {nid}: pattern miss")
        return
    s = es2(t, max(0, m.start() - span_back), m.start() + span_fwd, max_back=back, max_fwd=fwd)
    if junk_score(s) > 0.55 or len(s) < 60:
        print(f"  !! {nid}: junk/short slice")
        return
    sid = rfs2(ledger, fp, TODAY)
    src = next(x for x in ledger["sources"] if x["id"] == sid)
    aq2(ledger, sid, s, TODAY)
    key = re.sub(r"\W+", "", s.lower())[:80]
    kept = [h for h in n.get("highlights", [])
            if re.sub(r"\W+", "", h["text"].lower())[:80] != key]
    n["highlights"] = [{"text": s, "source_id": sid, "source_title": src["title"],
                        "source_url": src.get("url", ""), "direct": True,
                        "manual": True}] + kept[:4]
    print(f"  ok {nid}: {s[:90]!r}")

C = "evidence/_corpus/"
THEOG = "evidence/epimetheus/hesiod-evelynwhite-gutenberg348.txt"
AEN = C + "virgil-aeneid-dryden.txt"

fix_first("james-watt", C + "eb1911-watt.txt", r"WATT, JAMES \(1736")
fix_first("adam-smith", C + "eb1911-adam-smith.txt", r"SMITH, ADAM \(")
fix_first("joule", C + "eb1911-joule.txt", r"JOULE, JAMES PRESCOTT \(|joule was born")
fix_first("newton", C + "eb1911-newton.txt", r"NEWTON, SIR ISAAC \(1642")
fix_first("faraday", C + "eb1911-faraday.txt", r"FARADAY, MICHAEL \(|faraday was born")
fix_first("ampere", C + "eb1911-ampere.txt", r"AMPÈRE, ANDRÉ MARIE|ampere was born")
fix_first("fdr", C + "fdr-first-inaugural.txt", r"I, Franklin Delano Roosevelt|franklin delano roosevelt, do")
fix_first("victory", THEOG, r"styx the daughter of ocean was joined to pallas", span_back=20, back=80)
fix_first("fama", AEN, r"[Rr]umour", span_back=80, span_fwd=500, back=300, fwd=600)

shutil.copy(GP, GP.with_suffix(".json.bak12"))
json.dump(g, open(GP, "w"), indent=1, ensure_ascii=False)
json.dump(ledger, open(LP, "w"), indent=1, ensure_ascii=False)
print("done")
