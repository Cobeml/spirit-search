#!/usr/bin/env python3
"""Canonical case-preserving text loading, scrubbing and sentence-bounded slicing.

Every consumer of evidence text (highlight rebuild, edge re-slice, excerpt
repair, search chunker) must load through this module so that:

- quotes keep the witness's original capitalization (matching lowercases at
  match time, never at load time);
- sentence boundaries are detected even when a page/verse/line number token
  sits between the period and the next capital;
- document furniture (Gutenberg header/license, IA boilerplate, zero-width
  chars, cp1252 mojibake, inline page/verse numbers, "(ll. N)" locators,
  chapter headings) is scrubbed out of slices, never out of the stored
  witness files themselves.

Import surface:
  load_case(path)            -> case-preserving, scrubbed, single-spaced text
  norm_file(raw)             -> same, from a raw string (replaces _nameinfra.norm_file)
  sentence_at(t, pos)        -> whole sentence containing byte offset pos
  expand_span(t, lo, hi)     -> sentence-bounded passage covering [lo, hi)
  slice_clean(t, lo, hi)     -> expand_span + furniture scrub; None if no bounds
  scrub_text(s)              -> in-place scrub of an already-sliced quote string
  SENT_MARKERS_OK(text, m)   -> boundary validator (abbreviation guard)
"""
import html as _html
import re
from pathlib import Path

# ---------------------------------------------------------------- scrubbing

# cp1252 smart punctuation mis-decoded as latin-1 control chars
MOJIBAKE = {
    "\u0085": "\u2026", "\u0086": "\u2020", "\u0087": "\u2021",
    "\u0091": "\u2018", "\u0092": "\u2019", "\u0093": "\u201c",
    "\u0094": "\u201d", "\u0095": "\u2022", "\u0096": "\u2013",
    "\u0097": "\u2014",
}
INVISIBLE_RE = re.compile("[\u200b\u200c\u200d\u2060\ufeff\u00ad\u180e\ufffd]")
# wiki-media markup that survives plain tag-stripping on scraped HTML pages
WIKI_FILE = re.compile(r"\[\[(?:File|Image|media):[^\]]*\]\]", re.I)

PG_START = re.compile(r"\*{3}\s*START OF (?:THE|THIS)?\s*PROJECT GUTENBERG"
                      r"(?: EBOOK| ETEXT| TEXT)?[^\n]*\*{3}", re.I)
PG_END = re.compile(r"\*{3}\s*END OF (?:THE|THIS)?\s*PROJECT GUTENBERG"
                   r"(?: EBOOK| ETEXT| TEXT)?[^\n]*\*{3}", re.I)
IA_LINE = re.compile(r"^\s*digitized by the internet archive.*$",
                     re.I | re.M)
IA_FUNDING = re.compile(r"^\s*(?:in \d{4} )?with funding from.*$\n?", re.I | re.M)
# Google-scanned djvu preamble (books.google.com front matter)
GOOG_PREAMBLE = re.compile(
    r"\A.{0,200}?This is a digital copy of a book.*?discovery\.?\s*"
    r"(?:https?://books\.google\.com/?\s*)?", re.I | re.S)

def scrub_raw(t):
    """Remove non-text artifacts. Never changes real words."""
    for k, v in MOJIBAKE.items():
        t = t.replace(k, v)
    t = INVISIBLE_RE.sub("", t)
    t = WIKI_FILE.sub(" ", t)
    # Google-scan preamble: only strip when the marker sits at the very front
    if t[:300].lower().find("digital copy of a book") >= 0:
        t = GOOG_PREAMBLE.sub("", t, count=1)
    # Project Gutenberg header/license trimming (markers delimit the book)
    m = PG_START.search(t)
    if m:
        t = t[m.end():]
        m2 = PG_END.search(t)
        if m2:
            t = t[:m2.start()]
    # archive.org djvu front-matter: boilerplate line + scan-cover glyph junk
    m = IA_LINE.search(t)
    if m:
        cut_from = max(0, m.start() - 1200) if m.start() < 5000 else m.start()
        m2 = IA_FUNDING.search(t[m.end():])
        cut_to = m.end() + (m2.end() if m2 else 200)
        t = t[:cut_from] + t[cut_to:]
    return t

def tr_keepcase(t):
    """Transliterate diacritics (š->sh etc.) WITHOUT lowercasing."""
    for a, b in (("š", "sh"), ("Š", "Sh"), ("ž", "zh"), ("Ž", "Zh"),
                 ("þ", "th"), ("Þ", "Th"), ("ð", "d"), ("Ð", "D")):
        t = t.replace(a, b)
    return t

def _tags(t):
    # <style>/<script> CONTENT leaks into text as raw CSS on scraped pages
    t = re.sub(r"<(style|script)\b[^>]*>.*?</\1\s*>", " ", t,
               flags=re.I | re.S)
    if t.count("<") > 100:
        return re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"[<>]", " ", t)

def norm_file(raw):
    """Raw file string -> scrubbed, tag-stripped, single-spaced, CASED text."""
    t = _html.unescape(raw)
    t = scrub_raw(t)
    t = _tags(t)
    t = re.sub(r"\s+", " ", t)
    return tr_keepcase(t)

def load_case(path):
    return norm_file(Path(path).read_text(errors="replace"))

# ------------------------------------------------------- sentence boundaries

# boundary = sentence punctuation (+closing quotes) + whitespace, followed by
# a capital or a furniture number token then a capital. The capital lookahead
# is also the guard against stripping real quantities ("pounds. 200 men").
# A em/en dash after the closing quote is accepted (2026-10-21: Weems prints
# 'me." — And'; without this every slice near the cabinet roster walked back
# two sentences into Washington's speech).
CAND = re.compile(
    r"([.!?])([\"'\u2019\u201d\)\]]*)\s*[\u2014\u2013]?\s+"
    r"(?=(?:\d{1,4}(?::\d{1,4})?(?:[-\u2013,]\s?\d{1,4})*\s+)?"
    r"[A-Z\u201c\"(\[])"
)
# tokens after whose period a capital does NOT start a new sentence
ABBR = {"st", "no", "nr", "mr", "mrs", "ms", "dr", "prof", "rev", "hon",
        "cf", "vol", "pp", "p", "ll", "l", "v", "vv", "viz", "b", "c",
        "bc", "ad", "ah", "pt", "sec", "ch", "chap", "ed", "al", "wt",
        "ff", "ib", "rc", "ec", "it", "el", "loc", "cit", "op",
        "gen", "ex", "num", "deut", "isa", "jer", "ezek", "ps", "prov",
        "matt", "mark", "luke", "john", "acts", "rom", "cor", "gal",
        "eph", "phil", "col", "thes", "tim", "titus", "heb", "james",
        "pet", "jude", "rev"}
HEADWORD = {"book", "chapter", "part", "argument", "vol"}

def boundary_ok(t, m):
    """Reject abbreviation periods ("St. Paul", "A. H. Clough", "274 f. EC")."""
    # single capital + period right after the candidate boundary = initials
    if re.match(r"[A-Z]\.\s", t[m.end():]):
        return False
    pre = t[max(0, m.start() - 40):m.start()]
    w = re.search(r"([A-Za-z\u00c0-\u017f]+)[\u2019']?$", pre)
    if w:
        tok = w.group(1).lower()
        if tok in ABBR:
            return False
        # single-letter token: only a boundary in "BOOK I." style headings
        if len(tok) == 1:
            w2 = re.search(r"([A-Za-z\u00c0-\u017f]+)\s*$", pre[:w.start()])
            if not (w2 and w2.group(1).lower() in HEADWORD):
                return False
    return True

def _skip_furniture(t, i):
    """Skip a page/verse/line number token at a sentence start ("5:28 And")."""
    m = re.match(r"\d{1,4}(?::\d{1,4})?(?:\s?[-\u2013]\s?\d{1,4})?\s+", t[i:])
    if m:
        i += m.end()
    return i

def _prev_boundary(t, upto, max_back=None):
    """Last valid sentence-start position <= upto.

    re endpos TRUNCATES lookaheads: scanning with endpos=upto makes the
    boundary that ends exactly AT upto invisible (its capital lookahead
    sits at index upto), which silently creeped slices one sentence
    earlier on every repair pass. Scan a char further and filter instead.
    """
    best = None
    lo = 0 if max_back is None else max(0, upto - max_back)
    for m in CAND.finditer(t, lo, min(len(t), upto + 2)):
        if m.end() > upto:
            continue
        if boundary_ok(t, m):
            s = _skip_furniture(t, m.end())
            if s <= upto:
                best = s
    return best

def _next_boundary(t, frm, max_fwd=40000):
    # scan from frm-4: if the quote already ends exactly at a sentence
    # boundary (period + up to 3 closing quote/bracket chars), that boundary
    # must be the one returned, else every repair pass appends one more
    # sentence (tail creep, non-idempotent)
    for m in CAND.finditer(t, max(0, frm - 4), min(len(t), frm + max_fwd)):
        if boundary_ok(t, m):
            return m.start() + 1 + len(m.group(2))   # include punct + closing quotes
    # end-of-text: terminal punctuation in the tail counts as a boundary
    tail = t[max(0, frm - 4):max(0, frm - 4) + max_fwd]
    m2 = re.search(r"([.!?][\"'\u2019\u201d\)]*)\s*$", tail)
    if m2:
        return max(0, frm - 4) + m2.start() + len(m2.group(1))
    return None

# ------------------------------------------------------- furniture stripping

LOCATOR_HEAD = re.compile(
    r"^\s*[\(\[]?\s*l{1,2}\.\s*\d+[a-z]?(?:\s?[-\u2013,]\s?\d+[a-z]?)?\s*[\)\]]\s*")
# bracketed section refs: "[5.72]", "[1.7.2]", "(3.10.3)"
SECTION_HEAD = re.compile(
    r"^\s*[\(\[]\s*\d{1,3}(?:\.\d{1,3}){0,2}[a-z]?\s*[\)\]]\s*")
HEADING_HEAD = re.compile(
    r"^\s*(?:BOOK|Book|CHAPTER|Chapter|PART|Part|ARGUMENT|Argument|THE BOOK|The Book)"
    r"\s+[IVXLCivxlc0-9]+\.?\s+(?=[A-Z\u201c\"'])")
LEADING_NUM = re.compile(r"^\s*\d{1,4}(?::\d{1,4})?(?:\s?[-\u2013]\s?\d{1,4})?\s+(?=[A-Z])")
# page/verse/line numbers wedged between sentences: "married. 176 Besides"
PAGENUM_AFTER_PUNCT = re.compile(
    r"([.!?][\"'\u2019\u201d\)]?)\s+\d{1,4}(?::\d{1,4})?(?:\s?[-\u2013]\s?\d{1,4})?\s+(?=[A-Z])")
# Loeb-style page numbers mid-sentence: "centaur, 178 by whom"
PAGENUM_MID = re.compile(r",\s*(\d{2,4})\s+(?=[a-z])")
QUANTITY_BEFORE = re.compile(
    r"\b(?:with|of|some|about|nearly|over|under|above|below|more|less|than|"
    r"almost|exactly|number|times|years|men|ships|horse|men-at)\s*,?\s*$")

def _strip_mid_pagenums(s):
    def repl(m):
        pre = s[max(0, m.start() - 40):m.start()]
        if QUANTITY_BEFORE.search(pre):
            return m.group(0)          # real quantity, keep the number
        return ","
    return PAGENUM_MID.sub(repl, s)

def scrub_slice(s):
    """Strip document furniture from a sliced quote (slices only)."""
    s = LOCATOR_HEAD.sub("", s)
    s = SECTION_HEAD.sub("", s)
    s = HEADING_HEAD.sub("", s)
    # all-caps running header + page number (OCR glue in djvu texts)
    s = re.sub(r"^[A-Z][A-Z' ]{8,60}\s+\d{1,3}\s+(?=[A-Z])", "", s)
    s = LEADING_NUM.sub("", s)
    s = PAGENUM_AFTER_PUNCT.sub(r"\1 ", s)
    s = _strip_mid_pagenums(s)
    return s.strip()

def scrub_text(s):
    """Scrub an already-cut quote string in place (mojibake/invisible/furniture)."""
    for k, v in MOJIBAKE.items():
        s = s.replace(k, v)
    s = INVISIBLE_RE.sub("", s)
    return scrub_slice(s)

# ------------------------------------------------------------- slice helpers

def expand_span(t, lo, hi, max_back=None, max_fwd=40000):
    """Sentence-bounded passage covering [lo, hi); None if no forward bound."""
    s = _prev_boundary(t, lo, max_back)
    s = 0 if s is None else s
    e = _next_boundary(t, max(hi, s), max_fwd)
    if e is not None and e <= s:
        # lo sits exactly at a sentence start: the frm-4 back-scan in
        # _next_boundary returns the PREVIOUS sentence's end. Rescan from
        # s+1 (frm-4 => s-3 would re-find the same previous boundary).
        e = _next_boundary(t, s + 5, max_fwd)
    if e is None:
        return None
    return t[s:e].strip()

def slice_clean(t, lo, hi):
    """expand_span + furniture scrub. None if unbounded."""
    out = expand_span(t, lo, hi)
    if out is None:
        return None
    return scrub_slice(out)

def sentence_at(t, pos, max_back=None, max_fwd=40000):
    """Whole scrubbed sentence containing offset pos."""
    out = expand_span(t, pos, pos + 1, max_back, max_fwd)
    return scrub_slice(out) if out else None
