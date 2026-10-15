#!/usr/bin/env python3
"""Generic growth wave for spirit-graph: add review-tagged nodes+edges whose
excerpts are sliced verbatim from corpus files. Spec is data; run per wave.

Each NODE: id, label, tradition, era, notes
Each EDGE: frm, to, type, title, source_id, file (evidence path), anchor
           (regex; first high-quality match is sliced as excerpt)
Quality filter: skip matches inside TOC/footnotes; pick the occurrence with
the highest surrounding alphabetic density.
"""
import argparse, json, re, shutil, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GP, LP = REPO / "research" / "graph.json", REPO / "research" / "ledger.json"
TODAY = "2026-10-14"

def load():
    return json.load(open(GP)), json.load(open(LP))

def norm(t):
    return re.sub(r"\s+", " ", t)

def best_slice(text, pattern, span=300):
    # only strip tags when the file is actually HTML-ish; plain OCR text has
    # stray '<' chars that would eat huge spans
    if text.count("<") > 100:
        text = re.sub(r"<[^>]+>", " ", text)
    else:
        text = re.sub(r"[<>]", " ", text)
    t = norm(text)
    best, best_score = None, -1
    for m in re.finditer(pattern, t):
        s = max(0, m.start() - 40)
        chunk = t[s : m.start() + span]
        if "Gutenberg" in chunk[:100] and "License" in chunk:
            continue
        alnum = sum(c.isalpha() for c in chunk)
        frac = alnum / max(len(chunk), 1)
        digits = sum(1 for w in chunk.split() if any(c.isdigit() for c in w))
        score = frac - 0.05 * digits
        if score > best_score:
            best, best_score = chunk.strip(), score
    return best

def add_quote(led, src_id, q):
    src = next(s for s in led["sources"] if s["id"] == src_id)
    if all(x["text"][:60] != q[:60] for x in src.get("quotes", [])):
        src.setdefault("quotes", []).append({"text": q, "added": TODAY})

def run(nodes, edges, source_files):
    g, led = load()
    by_id = {n["id"] for n in g["nodes"]}
    texts = {}
    for k, rel in source_files.items():
        texts[k] = (REPO / rel).read_text(errors="replace")
    added_n = added_e = 0
    for spec in nodes:
        if spec["id"] in by_id:
            continue
        g["nodes"].append({
            "id": spec["id"], "label": spec["label"],
            "tradition": spec["tradition"], "batch": None, "date_added": TODAY,
            "era": spec["era"],
            "notes": [{"date": TODAY, "text": spec.get("note", "")
                       + " Auto-added in corpus-growth wave; unpriced pending power gate."}],
            "review": {"status": "auto-added", "date": TODAY},
        })
        by_id.add(spec["id"])
        added_n += 1
    has_edge = lambda f, t, ty: any(e["from"] == f and e["to"] == t and e["type"] == ty for e in g["edges"])
    for spec in edges:
        if spec["frm"] not in by_id or spec["to"] not in by_id or has_edge(spec["frm"], spec["to"], spec["type"]):
            continue
        q = best_slice(texts[spec["file"]], spec["anchor"])
        if not q or len(q) < 80:
            print("!! weak slice", spec["anchor"][:40])
            continue
        add_quote(led, spec["source_id"], q)
        src = next(s for s in led["sources"] if s["id"] == spec["source_id"])
        g["edges"].append({
            "from": spec["frm"], "to": spec["to"], "type": spec["type"],
            "source": spec["source_ref"], "title": spec["title"], "essay": None,
            "date_added": TODAY, "era": spec.get("era"), "influence": None,
            "excerpts": [{"text": q, "source_id": spec["source_id"],
                          "source_title": src["title"], "source_url": src["url"]}],
            "review": {"status": "auto-added", "date": TODAY},
        })
        added_e += 1
    shutil.copy(GP, GP.with_suffix(".json.bak"))
    json.dump(g, open(GP, "w"), indent=1, ensure_ascii=False)
    json.dump(led, open(LP, "w"), indent=1, ensure_ascii=False)
    print(f"+{added_n} nodes +{added_e} edges | totals: {len(g['nodes'])} nodes {len(g['edges'])} edges")
