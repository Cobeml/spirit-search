#!/usr/bin/env python3
"""Fixability probe v2: single coordinate space + diacritic transliteration.

For every flagged node: is any alias-bearing sentence available on disk?
For every flagged edge: is there a BOTH-endpoint co-occurrence window (<=600
chars) in any evidence file, and how tight is the best one?

Writes research/audit_fixability.json + prints summary.
"""
import json, re, sys, unicodedata, html as _html
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _aliases import ALIASES
from _audit_relevance import alias_patterns

REPO = Path(__file__).resolve().parent.parent
G = json.load(open(REPO / "research" / "graph.json"))

def tr(t):
    """lowercase + transliterate diacritics (š->sh etc.)"""
    t = t.lower()
    t = t.replace("š", "sh").replace("ž", "zh").replace("þ", "th").replace("ð", "d")
    return t

def norm_file(t):
    t = _html.unescape(t)
    if t.count("<") > 100:
        t = re.sub(r"<[^>]+>", " ", t)
    else:
        t = re.sub(r"[<>]", " ", t)
    return re.sub(r"\s+", " ", tr(t))

FILES = {}
SQMAP = {}
for p in sorted(REPO.glob("evidence/**/*.txt")) + sorted(REPO.glob("evidence/**/*.html")):
    raw = p.read_text(errors="replace")
    t = norm_file(raw)
    FILES[str(p.relative_to(REPO))] = t
    # squeeze index -> padded index map
    m = []
    for i, ch in enumerate(t):
        if not ch.isspace():
            m.append(i)
    SQMAP[str(p.relative_to(REPO))] = m

def positions(t, sqm, pats):
    """all alias positions in the PADDED coordinate space"""
    out = []
    tsq = re.sub(r"\s+", "", t)
    for p in pats:
        na = " " + re.sub(r"[^a-z0-9]+", " ", tr(p["a"])).strip() + " "
        sq = re.sub(r"\s+", "", na)
        start = 0
        while True:
            i = t.find(na, start)
            if i < 0:
                break
            out.append((i, p["a"]))
            start = i + 1
        if len(sq) >= 6:
            start = 0
            while True:
                j = tsq.find(sq, start)
                if j < 0:
                    break
                out.append((sqm[j] if j < len(sqm) else j, p["a"] + "(sq)"))
                start = j + 1
    out.sort()
    return out

byid = {n["id"]: n for n in G["nodes"]}
pats_of = {n["id"]: alias_patterns(n) for n in G["nodes"]}
POS = {}
def get_pos(nid):
    if nid not in POS:
        POS[nid] = {fp: positions(t, SQMAP[fp], pats_of[nid]) for fp, t in FILES.items()}
    return POS[nid]

WINDOW = 600
out = {"nodes": {}, "edges": {}}
n_fix = n_unfix = 0
for n in G["nodes"]:
    mode = n.get("audit", {}).get("mode")
    if mode in (None, "clean"):
        continue
    pos = get_pos(n["id"])
    hits = {fp: len(v) for fp, v in pos.items() if v}
    ok = bool(hits)
    if ok:
        n_fix += 1
    else:
        n_unfix += 1
    out["nodes"][n["id"]] = {"fixable": ok, "files": hits}

e_fix = e_unfix = 0
for e in G["edges"]:
    if e.get("audit", {}).get("ok"):
        continue
    best = None
    for fp, t in FILES.items():
        af = get_pos(e["from"])[fp]
        if not af:
            continue
        at = get_pos(e["to"])[fp]
        if not at:
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
    key = f"{e['from']}|{e['to']}|{e['type']}"
    if best:
        e_fix += 1
        out["edges"][key] = {"fixable": True, "dist": best[0], "file": best[1]}
    else:
        e_unfix += 1
        out["edges"][key] = {"fixable": False}

json.dump(out, open(REPO / "research" / "audit_fixability.json", "w"),
          indent=1, ensure_ascii=False)
print(f"nodes fixable from disk: {n_fix}, not nameable on disk: {n_unfix}")
print(f"edges with co-occurrence window: {e_fix}, without: {e_unfix}")
print("unfixable nodes:", [k for k, v in out["nodes"].items() if not v["fixable"]])
print("unfixable edges:", [k for k, v in out["edges"].items() if not v["fixable"]])
