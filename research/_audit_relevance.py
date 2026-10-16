#!/usr/bin/env python3
"""Relevance audit for highlights and edge excerpts.

Checks, per node, whether each highlight mentions the node (via the alias
registry, word-boundary + OCR-squeezed matching), and whether the FIRST
highlight describes the node. Per edge, whether any excerpt names BOTH
endpoints within a substantiating window.

Writes research/audit_relevance.json, flags graph.json in place
(highlight.audit / edge.audit -- research-side only, marker whitelist keeps
them off the site), prints a summary.
"""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _aliases import ALIASES, AMBIGUOUS, INDIRECT

REPO = Path(__file__).resolve().parent.parent
GP = REPO / "research" / "graph.json"

def norm(t):
    t = (t or "").lower().replace("-", " ")
    t = t.replace("š", "sh").replace("ž", "zh").replace("þ", "th").replace("ð", "d")
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " " + re.sub(r"\s+", " ", t).strip() + " "

def squeeze(t):
    return re.sub(r"\s+", "", t)

def alias_patterns(node):
    base = [node["label"], node["id"].replace("-", " ")]
    al = sorted({a.lower() for a in base + ALIASES.get(node["id"], []) if a})
    # plural forms (Weems: 'the Hamiltons and Burrs of the earth')
    al += [a + "s" for a in al if a.endswith(tuple("bcdfgklmnprstv")) and len(a) >= 4]
    pats = []
    for a in al:
        na = " " + norm(a).strip() + " "
        sq = squeeze(a)
        pats.append({"a": a, "na": na, "sq": sq, "long": len(sq) >= 6,
                     "amb": a in AMBIGUOUS})
    return pats

def first_hit(t, tsq, pats):
    best = None
    sqmap = None
    for p in pats:
        if p["na"] in t:
            i = t.find(p["na"])
        elif p["long"] and p["sq"] in tsq:
            j = tsq.find(p["sq"])
            if sqmap is None:
                sqmap = [i for i, ch in enumerate(t) if not ch.isspace()]
            i = sqmap[j] if j < len(sqmap) else j
        else:
            i = -1
        if i >= 0 and (best is None or i < best[0]):
            best = (i, p)
    return best

def mentions(t, pats):
    tsq = squeeze(t)
    return first_hit(t, tsq, pats) is not None

def main():
    g = json.load(open(GP))
    byid = {n["id"]: n for n in g["nodes"]}
    pats_of = {n["id"]: alias_patterns(n) for n in g["nodes"]}

    report = {"nodes": [], "edges": [], "summary": {}}
    n_modes = {"no_highlights": [], "none_mention": [], "first_not_direct": [],
               "partial": [], "clean": []}
    for n in g["nodes"]:
        pats = pats_of[n["id"]]
        hls = n.get("highlights", [])
        if not hls:
            n_modes["no_highlights"].append(n["id"])
            n["audit"] = {"mode": "no_highlights"}
            report["nodes"].append({"id": n["id"], "mode": "no_highlights"})
            continue
        flags, nm = [], 0
        for i, h in enumerate(hls):
            t = norm(h["text"])
            m = mentions(t, pats)
            hit = first_hit(t, squeeze(h["text"].lower()), pats)
            flags.append(m)
            h["audit"] = {"name_mention": m}
            if m:
                nm += 1
        first = flags[0]
        indirect = n["id"] in INDIRECT
        if nm == 0:
            mode = "indirect_expected" if indirect else "none_mention"
        elif not first:
            mode = "first_not_direct"
        elif nm < len(hls):
            mode = "partial"
        else:
            mode = "clean"
        n_modes[mode if mode != "indirect_expected" else "partial"].append(n["id"]) if mode != "indirect_expected" else n_modes["partial"].append(n["id"])
        n["audit"] = {"mode": mode, "mentions": nm, "total": len(hls)}
        report["nodes"].append({"id": n["id"], "label": n["label"], "mode": mode,
                                "mentions": nm, "total": len(hls),
                                "flags": flags})

    e_modes = {"no_excerpts": [], "none_both": [], "far_apart": [], "clean": []}
    for e in g["edges"]:
        pf, pt = pats_of.get(e["from"]), pats_of.get(e["to"])
        exc = e.get("excerpts", [])
        if not exc:
            e_modes["no_excerpts"].append((e["from"], e["to"], e["type"]))
            e["audit"] = {"ok": False, "mode": "no_excerpts"}
            continue
        best = None
        for x in exc:
            t = norm(x["text"])
            tsq = squeeze(x["text"].lower())
            hf, ht = first_hit(t, tsq, pf), first_hit(t, tsq, pt)
            has_f, has_t = hf is not None, ht is not None
            dist = abs((hf[0] if hf else 0) - (ht[0] if ht else 0)) if (has_f and has_t) else None
            x["audit"] = {"has_from": has_f, "has_to": has_t, "dist": dist}
            if has_f and has_t:
                if best is None or (dist or 0) < best[0]:
                    best = (dist or 0, x)
        if best is None:
            e_modes["none_both"].append((e["from"], e["to"], e["type"]))
            e["audit"] = {"ok": False, "mode": "none_both"}
        elif best[0] > 600:
            e_modes["far_apart"].append((e["from"], e["to"], e["type"], best[0]))
            e["audit"] = {"ok": False, "mode": "far_apart", "dist": best[0]}
        else:
            e_modes["clean"].append((e["from"], e["to"]))
            e["audit"] = {"ok": True, "mode": "clean", "dist": best[0]}
        report["edges"].append({"frm": e["from"], "to": e["to"], "type": e["type"],
                                "mode": e["audit"].get("mode", "clean"),
                                "dist": e["audit"].get("dist")})

    report["summary"] = {
        "nodes_total": len(g["nodes"]),
        "node_modes": {k: (len(v), v[:40]) for k, v in n_modes.items()},
        "edges_total": len(g["edges"]),
        "edge_modes": {k: (len(v), [list(x) for x in v][:40]) for k, v in e_modes.items()},
    }
    json.dump(report, open(REPO / "research" / "audit_relevance.json", "w"),
              indent=1, ensure_ascii=False)
    shutil.copy(GP, GP.with_suffix(".json.bak3"))
    json.dump(g, open(GP, "w"), indent=1, ensure_ascii=False)

    print("== NODES ==")
    for k, v in n_modes.items():
        print(f"{k}: {len(v)}")
    print("== EDGES ==")
    for k, v in e_modes.items():
        print(f"{k}: {len(v)}")
    print("\nfirst_not_direct sample:", n_modes["first_not_direct"][:15])
    print("none_mention sample:", n_modes["none_mention"][:15])
    print("edges none_both sample:", [x for x in e_modes["none_both"][:15]])
    print("edges far_apart sample:", [x for x in e_modes["far_apart"][:10]])

if __name__ == "__main__":
    main()
