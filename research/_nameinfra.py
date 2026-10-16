#!/usr/bin/env python3
"""Shared name-matching infrastructure for the rebuild passes (P2/P3).

Loads evidence files once, provides alias positions (padded coordinate space,
transliteration + plural aware), sentence slicing at name occurrences, and
ledger-source resolution for evidence files.
"""
import html as _html
import json, re
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _audit_relevance import alias_patterns  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
GP = REPO / "research" / "graph.json"
LP = REPO / "research" / "ledger.json"

SENT_END = re.compile(r"(?<=[.!?])[\"'\)\]]?\s+(?=[A-Z'\"\u201c\(\[]|$)")

def tr(t):
    t = t.lower()
    return (t.replace("š", "sh").replace("ž", "zh")
             .replace("þ", "th").replace("ð", "d"))

def norm_file(raw):
    t = _html.unescape(raw)
    t = re.sub(r"<[^>]+>", " ", t) if t.count("<") > 100 else re.sub(r"[<>]", " ", t)
    return re.sub(r"\s+", " ", tr(t))

FILES, SQMAP = {}, {}
for p in sorted(REPO.glob("evidence/**/*.txt")) + sorted(REPO.glob("evidence/**/*.html")):
    t = norm_file(p.read_text(errors="replace"))
    fp = str(p.relative_to(REPO))
    FILES[fp] = t
    SQMAP[fp] = [i for i, ch in enumerate(t) if not ch.isspace()]

def positions(t, sqm, pats):
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

def sentence_at(t, pos, max_back=400, max_fwd=500):
    back = None
    for m in SENT_END.finditer(t, max(0, pos - max_back), pos):
        back = m.end()
    s = back if back is not None else max(0, pos - 100)
    fwd = None
    for m in SENT_END.finditer(t, pos, pos + max_fwd):
        fwd = m.start()
        break
    e = fwd if fwd is not None else min(len(t), pos + 400)
    return t[s:e].strip()

def expand_span(t, lo, hi, max_back=2500, max_fwd=800):
    back = None
    for m in SENT_END.finditer(t, max(0, lo - max_back), lo):
        back = m.end()
    s = back if back is not None else lo
    fwd = None
    for m in SENT_END.finditer(t, hi, hi + max_fwd):
        fwd = m.start()
        break
    e = fwd if fwd is not None else min(len(t), hi + max_fwd)
    return t[s:e].strip()

def junk_score(text):
    if not text:
        return 1.0
    alpha = sum(c.isalpha() for c in text) / max(len(text), 1)
    words = text.split()
    digits = sum(1 for w in words if any(c.isdigit() for c in w))
    return (1 - alpha) + 0.3 * (digits / max(len(words), 1))

def file_for_source(src):
    """Resolve a ledger source dict to its evidence file path (or None)."""
    fn = (src.get("url") or "").split("/")[-1]
    cands = list(REPO.glob("evidence/**/*.txt")) + list(REPO.glob("evidence/**/*.html"))
    hits = [p for p in cands if fn and (fn in p.name or p.stem in fn or p.stem.replace("-", "_") in fn)]
    if not hits and fn:
        raw = (fn + " " + (src.get("title") or "")).lower()
        toks = {t for t in re.split(r"[^a-z0-9]+", raw) if len(t) >= 5} - \
               {"https", "archive", "org", "gutenberg", "trans", "wikisource", "www"}

        def score(p):
            n = p.name.lower()
            return sum(1 for t2 in toks if t2 in n)
        ranked = sorted(cands, key=lambda p: (-score(p), -p.stat().st_size))
        if ranked and score(ranked[0]) > 0:
            hits = [ranked[0]]
    if not hits:
        return None
    return str(hits[0].relative_to(REPO))

def build_sid_map(ledger):
    fp_to_sid = {}
    for s in ledger["sources"]:
        fp = file_for_source(s)
        if fp and fp not in fp_to_sid:
            fp_to_sid[fp] = s["id"]
    return fp_to_sid

def register_file_source(ledger, fp, today):
    """Auto-register a ledger source for an evidence file that has none."""
    sid_map = build_sid_map(ledger)
    if fp in sid_map:
        return sid_map[fp]
    stem = Path(fp).stem
    title = "Evidence file " + stem + " (local, unregistered witness)"
    new_id = max(s["id"] for s in ledger["sources"]) + 1
    ledger["sources"].append({"id": new_id, "url": "", "title": title,
                              "accessed": today, "quotes": []})
    return new_id

def add_quote(ledger, sid, text, today):
    s = next(x for x in ledger["sources"] if x["id"] == sid)
    if all(q["text"][:60] != text[:60] for q in s.get("quotes", [])):
        s.setdefault("quotes", []).append({"text": text, "added": today})
