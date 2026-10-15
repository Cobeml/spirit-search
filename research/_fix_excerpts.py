#!/usr/bin/env python3
"""Repair excerpts/quotes: expand every slice to full sentence boundaries.

For each edge excerpt + ledger quote: find a distinctive fragment of the quote
in its source file (normalized), then expand back to the previous sentence end
and forward to the next, so highlights read as whole sentences.
"""
import json, re, shutil, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GP, LP = REPO / "research" / "graph.json", REPO / "research" / "ledger.json"

def load_text(s):
    """Locate file for a ledger source by url basename across evidence/."""
    fn = (s.get("url") or "").split("/")[-1]
    cands = list(REPO.glob("evidence/**/*.txt"))
    hits = [p for p in cands if fn and (fn in p.name or p.stem in fn or p.stem.replace("-", "_") in fn)]
    if not hits and fn:
        raw = (fn + " " + (s.get("title") or "")).lower()
        toks = {t for t in re.split(r"[^a-z0-9]+", raw) if len(t) >= 5} - {"https", "archive", "org", "gutenberg", "trans"}

        def score(p):
            n = p.name.lower()
            return sum(1 for t in toks if t in n)
        scored = sorted(cands, key=lambda p: (-score(p), -p.stat().st_size))
        if scored and score(scored[0]) > 0:
            hits = [scored[0]]
    if not hits:
        return None
    t = hits[0].read_text(errors="replace")
    if t.count("<") > 100:
        t = re.sub(r"<[^>]+>", " ", t)
    else:
        t = re.sub(r"[<>]", " ", t)
    return re.sub(r"\s+", " ", t)

TEXT_CACHE = {}

SENT_END = re.compile(r"(?<=[.!?])[\"'\)\]]?\s+(?=[A-Z'\"“\(\[]|$)")

def expand_to_sentences(t, start, end, max_back=500, max_fwd=600):
    # back: last sentence end strictly before our first full word
    back = None
    for m in SENT_END.finditer(t, max(0, start - max_back), start):
        back = m.end()
    if back is None:
        back = start
    s = back
    fwd = None
    for m in SENT_END.finditer(t, end, end + max_fwd):
        fwd = m.start()
        break
    if fwd is None:
        fwd = min(len(t), end + max_fwd)
    e = fwd if fwd > end else end
    return t[s:e].strip()

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

def fix_quote(qtext, text_norm):
    nt, pos = norm_with_map(text_norm)
    nq = norm_key(qtext)
    if len(nq) > 30:
        frag = nq[:40]
    else:
        frag = nq
    i = nt.find(frag)
    if i < 0 and len(nq) > 80:
        i = nt.find(nq[len(nq)//2 : len(nq)//2 + 40])
    if i < 0:
        return qtext
    o_start = pos[i]
    # end: find normalized tail
    tail = nq[-35:]
    j = nt.find(tail, i)
    o_end = pos[j + len(tail) - 1] if j >= 0 else min(len(text_norm) - 1, pos[min(i + len(nq), len(pos) - 1)])
    new = expand_to_sentences(text_norm, o_start, o_end + 1)
    return new if 40 <= len(new) <= 3000 else qtext

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

    fixed = skipped = 0

    def process(text, sid):
        nonlocal fixed, skipped
        if sid not in srcs:
            skipped += 1
            return text
        t = tfor(sid)
        if not t:
            skipped += 1
            return text
        old = text
        new = fix_quote(text, t)
        if new != text and 40 <= len(new) <= 3000:
            fixed += 1
            return new
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
    print(f"fixed={fixed} skipped={skipped}")

if __name__ == "__main__":
    main()
