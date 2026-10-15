#!/usr/bin/env python3
"""Populate graph.json nodes/edges with excerpt highlights.

Primary source of excerpts: ledger.json — the curated verbatim quotes attached
to each numbered source. Node essays cite sources as [n]; edge.source starts
with [n]. Highlights are those quotes, verbatim, cited by source title/url.

Algorithmic supplement (for nodes whose cited sources lack a quote near the
topic): hybrid search inside the node's evidence folder. Corpus-wide proposals
flagged proposed:true come from searching outside the node's evidence folder.

Dry-run by default; --write modifies graph.json (backup saved first).
"""
import argparse, json, re, shutil, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "research"))
from _search_lib import search  # noqa: E402

GRAPH = REPO / "research" / "graph.json"
LEDGER = json.load(open(REPO / "research" / "ledger.json"))
SRC = {s["id"]: s for s in LEDGER["sources"]}
CIT = re.compile(r"\[(\d+)\]")
TAG_RE = re.compile(r"<[^>]+>")

def clean(t):
    t = re.sub(r"\s+", " ", TAG_RE.sub(" ", t)).strip()
    if t and t[0].islower() and " " in t:  # mid-word fragment start
        t = t.split(" ", 1)[1]
    return t

def node_cited_ids(node):
    text = (node.get("essay") or "") + " " + (node.get("power_rationale") or "")
    seen, out = set(), []
    for m in CIT.finditer(text):
        sid = int(m.group(1))
        if sid in SRC and sid not in seen:
            seen.add(sid)
            out.append(sid)
    return out

def quote_hl(q, src_id):
    s = SRC[src_id]
    return {"text": clean(q["text"]),
            "source_id": src_id,
            "source_title": s.get("title", ""),
            "source_url": s.get("url", "")}

STOP = set("the a an of to and or in on with for by from at as is are was were he she it its his her their them they that these those this but not no into out up down so such whom which who".split())

def _tokens(text):
    import re as _re
    return {w for w in _re.findall(r"[A-Za-z]{3,}", (text or "").lower()) if w not in STOP}

def _cite_context(node, sid, essay):
    """essay sentence(s) containing this source's [n] mark."""
    import re as _re
    out = []
    for m in _re.finditer(rf"\[{sid}\]", essay or ""):
        s = max(essay.rfind(".", 0, m.start()), essay.rfind(";", 0, m.start()))
        out.append(essay[s + 1 : essay.find(".", m.end()) if essay.find(".", m.end()) > 0 else min(m.end() + 300, len(essay))])
    return " ".join(out)

QUOTED = re.compile(r"['\u2018\"]([^'\"\u2019]{25,300})['\u2019\"]\s*(?:\((?:[^\)]{0,80})\))?\s*(\[(\d+)\])")

def _essay_anchors(node):
    """Quoted spans in the essay tied to a [n] citation, mapped to source."""
    essay = node.get("essay") or ""
    out = []
    for m in QUOTED.finditer(essay):
        sid = int(m.group(3))
        if sid in SRC:
            out.append((sid, m.group(1)))
    return out

_SRCTEXT = {}

def _source_text(sid):
    if sid not in _SRCTEXT:
        try:
            from _fix_excerpts import load_text
            s = SRC[sid]
            _SRCTEXT[sid] = load_text({"url": s.get("url", ""), "title": s.get("title", "")})
        except Exception:
            _SRCTEXT[sid] = None
    return _SRCTEXT[sid]

def _expand_in_source(sid, frag):
    t = _source_text(sid)
    if not t:
        return None
    try:
        from _fix_excerpts import fix_quote
        out = fix_quote(frag, t)
        return out if out != frag and 40 <= len(out) <= 3000 else None
    except Exception:
        return None

def node_highlights(node, n=5, edges=None):
    essay = node.get("essay") or ""
    out = []
    # 1. quoted spans inside the essay, located and sentence-expanded in the source
    seen_src = set()
    for sid, frag in _essay_anchors(node):
        full = _expand_in_source(sid, frag)
        if full:
            s = SRC[sid]
            out.append({"text": full, "source_id": sid,
                        "source_title": s.get("title", ""), "source_url": s.get("url", "")})
            seen_src.add(sid)
        if len(out) >= n:
            break
    # 2. ledger quotes of cited sources, scored by label/proper-noun overlap
    label_toks = _tokens(node["label"]) | _tokens(node.get("power_rationale"))
    for sid in node_cited_ids(node):
        if sid in seen_src or len(out) >= n:
            continue
        ctx = label_toks | _tokens(_cite_context(node, sid, essay))
        cands = []
        for q in (SRC[sid].get("quotes") or []):
            qt = _tokens(q["text"])
            lab = len(_tokens(node["label"]) & qt)
            ov = len(ctx & qt)
            cands.append((2 * lab + ov, q))
        cands.sort(key=lambda c: -c[0])
        picked = 0
        for score, q in cands:
            lab = len(_tokens(node["label"]) & _tokens(q["text"]))
            if lab == 0 and score < 5:
                continue  # without this node's name or strong context, skip
            h = quote_hl(q, sid)
            if 40 <= len(h["text"]) <= 1200:
                h["relevance"] = score
                out.append(h)
                picked += 1
            if picked >= 2 or len(out) >= n:
                break
        if len(out) >= n:
            break
    if (REPO / "evidence" / node["id"]).is_dir() and len(out) < n:
        for h in search(f"{node['label']} {node.get('tradition','')}", k=6,
                        clusters=[node["id"]]):
            p = best_passage(h)
            if p:
                p["algorithmic"] = True
                out.append(p)
            if len(out) >= n:
                break
    # fallback for essay-less wave nodes: reuse their edges' excerpts
    if not out and edges:
        for e in edges:
            if node["id"] in (e["from"], e["to"]) and e.get("excerpts"):
                out.extend(x for x in e["excerpts"] if 40 <= len(x["text"]) <= 1200)
            if len(out) >= n:
                break
    return out[:n]

def node_proposals(node, n=3):
    q = f"{node['label']} {node.get('tradition','')} {node.get('power_rationale','')[:150]}"
    out = []
    for h in search(q, k=30):
        if h["cluster"] == node["id"]:
            continue
        p = best_passage(h)
        if p:
            p["proposed"] = True
            out.append(p)
        if len(out) >= n:
            break
    return out

def edge_excerpts(edge, label_of=None):
    out = []
    for m in CIT.finditer(edge.get("source", "")):
        sid = int(m.group(1))
        if sid in SRC:
            for q in (SRC[sid].get("quotes") or [])[:1]:
                h = quote_hl(q, sid)
                if 40 <= len(h["text"]) <= 1200:
                    out.append(h)
            break  # first cited source is the edge's witness
    return out

def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z'\"“])", clean(text))
    return [p for p in parts if 40 <= len(p) <= 420 and not re.match(r"^[a-z]", p)]

def _is_junk(t):
    if t.count("<") > 4:
        return True
    if sum(c.isalpha() for c in t) / max(len(t), 1) < 0.55:
        return True
    words = t.split()
    digitish = sum(1 for w in words if any(c.isdigit() for c in w) or w.endswith(","))
    return bool(words) and digitish / len(words) > 0.3

def best_passage(hit, max_sents=3):
    if _is_junk(hit["text"]):
        return None
    s = sentences(hit["text"])
    if not s:
        return None
    return {"text": " ".join(s[:max_sents]),
            "source_title": hit["title"], "source_url": hit["url"],
            "cluster": hit["cluster"]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    g = json.load(open(GRAPH))
    work = g["nodes"][: a.limit] if a.limit else g["nodes"]
    for nd in work:
        nd["highlights"] = node_highlights(nd, edges=g["edges"])
        nd["proposals"] = node_proposals(nd)
        if a.limit:
            print(nd["id"], len(nd["highlights"]), "hl,", len(nd["proposals"]), "prop.")
    if not a.limit:
        for e in g["edges"]:
            e["excerpts"] = edge_excerpts(e)
    nh = sum(len(n.get("highlights", [])) for n in g["nodes"])
    npr = sum(len(n.get("proposals", [])) for n in g["nodes"])
    nex = sum(len(e.get("excerpts", [])) for e in g["edges"])
    print(f"highlights={nh} proposals={npr} edge_excerpts={nex}")
    if a.write:
        shutil.copy(GRAPH, GRAPH.with_suffix(".json.bak"))
        json.dump(g, open(GRAPH, "w"), indent=1, ensure_ascii=False)
        print("graph.json written (backup at research/graph.json.bak)")

if __name__ == "__main__":
    main()
