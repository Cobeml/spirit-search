#!/usr/bin/env python3
"""Repair excerpts/quotes: expand every slice to full sentence boundaries.

For each edge excerpt + ledger quote: find a distinctive fragment of the quote
in its source file (normalized), then expand back to the previous sentence end
and forward to the next, so highlights read as whole sentences.
"""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _textclean as TC

REPO = Path(__file__).resolve().parent.parent
GP, LP = REPO / "research" / "graph.json", REPO / "research" / "ledger.json"

def load_text(s):
    """Locate file for a ledger source by url basename across evidence/."""
    fn = (s.get("url") or "").split("/")[-1].lower()
    cands = (list(REPO.glob("evidence/**/*.txt"))
             + list(REPO.glob("evidence/**/*.html")))
    hits = [p for p in cands
            if fn and (fn in p.name.lower()
                       or p.stem.lower() in fn
                       or p.stem.lower().replace("-", "_") in fn)]
    if not hits and (fn or s.get("title")):
        raw = ((fn or "") + " " + (s.get("title") or "")).lower()
        toks = {t for t in re.split(r"[^a-z0-9]+", raw) if len(t) >= 5} - {"https", "archive", "org", "gutenberg", "trans", "www", "com", "html"}

        def score(p):
            n = p.name.lower()
            return sum(1 for t in toks if t in n)
        scored = sorted(cands, key=lambda p: (-score(p), -p.stat().st_size))
        if scored and score(scored[0]) > 0:
            hits = [scored[0]]
    if not hits:
        return None
    return TC.norm_file(hits[0].read_text(errors="replace"))

TEXT_CACHE = {}

AGGRESSIVE = re.compile(r"[^a-z0-9 ]+")

def norm_key(s):
    return AGGRESSIVE.sub("", re.sub(r"\s+", " ", s.lower().replace("-", ""))).strip()

def norm_with_map(t):
    """normalized text + map from normalized index -> original index"""
    out, pos = [], []
    prev_space = True
    for i, ch in enumerate(t):
        c = ch.lower()
        if c == "-":
            continue  # ignore hyphenation (OCR line-break splits) when matching
        if c.isalnum():
            out.append(c); pos.append(i); prev_space = False
        elif not prev_space:
            out.append(" "); pos.append(i); prev_space = True
    return "".join(out), pos

def _occurrences(nt, f, limit=12):
    out, i = [], nt.find(f)
    while i >= 0 and len(out) < limit:
        out.append(i)
        i = nt.find(f, i + 1)
    return out

def fix_quote(qtext, text):
    """Locate the quote in its (cased, scrubbed) witness and return the
    sentence-bounded, furniture-scrubbed passage. None if unlocatable.

    Repeat-formula texts (Iliad ship counts) hold many occurrences of a
    40-char window; every candidate occurrence is scored by how much of the
    quote its span contains, so re-running always anchors the SAME passage
    (idempotent) instead of jumping between lookalikes.
    """
    nt, pos = norm_with_map(text)
    nq = norm_key(qtext)
    if len(nq) < 30:
        return None
    W = 40
    mid = nq[len(nq) // 2 : len(nq) // 2 + 30] if len(nq) >= 80 else ""
    tail = nq[-35:] if len(nq) >= 45 else ""
    head60 = nq[:60]
    offs = {0, max(0, len(nq) // 2)}
    o = len(nq) // 2
    while o > 0:
        offs.add(o)
        o -= 20
    o = len(nq) // 2
    while o + W < len(nq):
        offs.add(o)
        o += 20
    best_i = -1
    best_score = -1
    for off in sorted(offs):
        f = nq[off:off + W]
        if len(f) < 20:
            continue
        for c in _occurrences(nt, f):
            span = nt[c : c + len(nq) + 600]
            score = 0
            for probe, wgt in ((head60, 2), (mid, 3), (tail, 3)):
                if probe and probe in span:
                    score += wgt
            if score > best_score:
                best_score, best_i = score, c
            if score >= 8:
                break
        if best_score >= 8:
            break
    if best_i < 0:
        return None
    i = best_i
    # try to recover the quote's true head: nq[:60] within ~600 chars before?
    if len(head60) >= 25:
        for back in (200, 400, 700):
            j = nt.find(head60, max(0, i - back), i + W)
            if j >= 0:
                i = j
                break
    o_start = pos[i]
    if tail and len(tail) >= 15:
        j = nt.find(tail, i, i + len(nq) + 600)
        if j >= 0:
            o_end = pos[min(j + len(tail) - 1, len(pos) - 1)] + 1
        else:
            o_end = pos[min(i + len(nq) - 1, len(pos) - 1)] + 1
    else:
        o_end = pos[min(i + len(nq) - 1, len(pos) - 1)] + 1
    new = TC.slice_clean(text, o_start, o_end)
    if new is None:
        return None
    return new if 40 <= len(new) <= 3000 else None

def main():
    global TEXT_CACHE
    g = json.load(open(GP))
    led = json.load(open(LP))
    srcs = {s["id"]: s for s in led["sources"]}
    cache = {}

    def tfor(sid):
        if sid not in cache:
            cache[sid] = load_text(srcs.get(sid, {})) if sid in srcs else None
        return cache[sid]

    fixed = skipped = scrubbed = 0

    def process(text, sid):
        nonlocal fixed, skipped, scrubbed
        if sid not in srcs:
            skipped += 1
            return text
        t = tfor(sid)
        if not t:
            skipped += 1
            return text
        new = fix_quote(text, t)
        if new and new != text and 40 <= len(new) <= 3000:
            fixed += 1
            return new
        # unlocatable or unchanged: still scrub the stored text in place
        cleaned = TC.scrub_text(text)
        if cleaned != text:
            scrubbed += 1
            return cleaned
        skipped += 1
        return text

    # ledger quotes
    for s in led["sources"]:
        for q in s.get("quotes", []):
            q["text"] = process(q["text"], s["id"])
    # edge excerpts
    for e in g["edges"]:
        for x in e.get("excerpts", []):
            x["text"] = process(x["text"], x.get("source_id") or (e.get("source_id")))
    # node highlights (only ledger-backed ones have source_id)
    for n in g["nodes"]:
        for h in n.get("highlights", []):
            if h.get("source_id"):
                h["text"] = process(h["text"], h["source_id"])

    shutil.copy(GP, GP.with_suffix(".json.bak2"))
    json.dump(g, open(GP, "w"), indent=1, ensure_ascii=False)
    json.dump(led, open(LP, "w"), indent=1, ensure_ascii=False)
    print(f"fixed={fixed} scrubbed_only={scrubbed} skipped={skipped}")

if __name__ == "__main__":
    main()
