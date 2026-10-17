#!/usr/bin/env python3
"""Diagnose highlight/excerpt quality: sentence segmentation + junk chars."""
import json, re, collections, unicodedata

G = json.load(open('research/graph.json'))

highlights, excerpts = [], []
for n in G['nodes']:
    for i, h in enumerate(n.get('highlights', [])):
        highlights.append((n['id'], i, h.get('text', '')))
for e in G.get('edges', []):
    for i, x in enumerate(e.get('excerpts', [])):
        excerpts.append((e.get('from'), e.get('to'), e.get('type'), i, x.get('text', '')))

print(f"nodes={len(G['nodes'])} edges={len(G.get('edges', []))} highlights={len(highlights)} excerpts={len(excerpts)}")

def classify_text(t):
    issues = []
    s = t.strip()
    # --- sentence segmentation ---
    if not s:
        issues.append('EMPTY')
        return issues
    first = s[0]
    if first.islower():
        issues.append('starts_lowercase(midsentence)')
    elif first in ',;:)]}"\'.':
        issues.append('starts_midpunct')
    # trailing: does it end with sentence-terminal punct?
    if not re.search(r'[.!?"\u201d\u2019\)\]]$', s):
        issues.append('no_terminal_punct(midsentence_end)')
    # leading ellipsis/dash suggests a truncated lead
    if re.match(r'^[\u2026\u2013\u2014-]{1,2}\s', s):
        issues.append('leading_ellipsis')
    if re.search(r'[\u2026]\s*$', s):
        issues.append('trailing_ellipsis')
    # starts with a quote that never closes (unbalanced quote suggests slice)
    if s.count('"') % 2 == 1:
        issues.append('unbalanced_dquote')
    if s.count('\u201c') != s.count('\u201d'):
        issues.append('unbalanced_curlyquote')
    # --- junk chars / document artifacts ---
    # html entities that survived
    ents = re.findall(r'&[a-zA-Z#0-9]{2,10};', s)
    if ents:
        issues.append('html_entity')
    # unicode replacement / control
    if '\ufffd' in s or any(ord(c) < 32 and c not in '\n\t' for c in s):
        issues.append('replacement_or_control')
    # footnote markers: superscript digits stuck to words
    if re.search(r'[a-z]\u00b9|\u00b2|\u00b3', s):
        issues.append('superscript_footnote')
    # bracketed footnote/illustration editorial inserts
    if re.search(r'\[(?:footnote|Footnote|FN|sic|illegible|.*?\u2026)\]', s):
        issues.append('bracketed_editorial')
    # stray chapter/section refs mid-quote
    if re.search(r'\b(?:BOOK|BOOK I{1,3}|CHAPTER|BOOK [IVX]+)\b\s*$', s):
        issues.append('trailing_chapter_header')
    if re.search(r'^\s*(?:BOOK|CHAPTER|Book|Chapter)\s+[IVXLC0-9]+', s) and len(s) < 60:
        issues.append('leading_chapter_header')
    # Table of contents / index style: dotted leaders or many short lines
    if re.search(r'\.{4,}\s*\d+', s) or re.search(r'\s\d{1,3}$', s) and len(s.splitlines()) > 3:
        issues.append('toc_or_index_line')
    # vol/page refs like "BOOK I. 12" or "ll. 25" leading
    if re.match(r'^\s*\(?l{1,2}\.\s*\d+', s):
        issues.append('leading_linemarker')
    # weird spacing from OCR: multiple spaces inside a line, hyphen-space linebreaks kept
    if re.search(r'[a-z]- \n', s) or re.search(r'\w +- \w', s):
        issues.append('hyphen_linebreak_kept')
    if re.search(r'[^\s\n]{25,}\s{2,}[^\s\n]{10,}', s):
        pass
    # double spaces (OCR page-width justifies)
    if re.search(r'\S\s{3,}\S', s):
        issues.append('ocr_multispace')
    # newlines inside what should be a flowing sentence
    if '\n' in s and len(re.findall(r'[.!?]["\u201d]?\s*$', s, re.M)) < len(s.splitlines()) - 1 and len(s) < 1200:
        issues.append('embedded_newlines')
    # rare/odd chars: statistical outliers
    odd = [c for c in set(s) if ord(c) > 127 and unicodedata.category(c)[0] not in 'LPS' and c not in '\u2019\u201c\u201d\u2014\u2013\u2026']
    if any(c not in '\u00e9\u00e8\u00ea\u00e0\u00e2\u00ee\u00ef\u00f4\u00fb\u00f9\u00e7\u00c9\u0153\u00e6\u00f6\u00fc\u00df\u00f1\u00e1\u00ed\u00f3\u00fa\u00fa' for c in odd):
        issues.append('odd_punct_or_symbol:' + ''.join(sorted(set(odd)))[:12])
    # very long (likely multiple sentences squeezed: fine but note)
    return issues

hstats = collections.Counter(); hissue_examples = collections.defaultdict(list)
for nid, i, t in highlights:
    for iss in classify_text(t):
        hstats[iss] += 1
        if len(hissue_examples[iss]) < 3:
            hissue_examples[iss].append((nid, t[:140]))

estats = collections.Counter(); eissue_examples = collections.defaultdict(list)
for frm, to, typ, i, t in excerpts:
    for iss in classify_text(t):
        estats[iss] += 1
        if len(eissue_examples[iss]) < 3:
            eissue_examples[iss].append((f"{frm}|{to}", t[:140]))

print("\n=== HIGHLIGHT issues (count out of", len(highlights), ") ===")
for k, v in hstats.most_common():
    print(f"{v:5d}  {k}")
print("\n=== EDGE EXCERPT issues (count out of", len(excerpts), ") ===")
for k, v in estats.most_common():
    print(f"{v:5d}  {k}")

print("\n=== EXAMPLES (highlights) ===")
for k in list(hstats)[:14]:
    for nid, t in hissue_examples[k][:2]:
        print(f"[{k}] {nid}: {t!r}")
print("\n=== EXAMPLES (excerpts) ===")
for k in list(estats)[:14]:
    for eid, t in eissue_examples[k][:2]:
        print(f"[{k}] {eid}: {t!r}")
