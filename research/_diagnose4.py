#!/usr/bin/env python3
"""Final: search.db case/boilerplate state + no-witness breakdown."""
import sqlite3, re, json, sys
sys.path.insert(0, 'research')
from pathlib import Path

db = sqlite3.connect('research/search.db')
n = db.execute("SELECT count(*) FROM chunks").fetchone()[0]
cap = db.execute("SELECT count(*) FROM chunks WHERE text LIKE '%Zeus%' OR text LIKE '%Apollo%'").fetchone()[0]
low = db.execute("SELECT count(*) FROM chunks WHERE text LIKE '%zeus, king%'").fetchone()[0]
print(f"chunks={n}; containing 'Zeus/Apollo' (cased): {cap}; containing 'zeus, king' (lower): {low}")

boiler = db.execute("""SELECT count(*) FROM chunks WHERE text LIKE '%Project Gutenberg%'
  OR text LIKE '%digitized by the internet archive%' OR text LIKE '%START OF THE PROJECT GUTENBERG%'
  OR text LIKE '%END OF THIS PROJECT GUTENBERG%' OR text LIKE '%*** END ***%'""").fetchone()[0]
print(f"boilerplate chunks (PG header/license/IA): {boiler} ({100*boiler/n:.1f}% of corpus)")

# per-source boilerplate count
rows = db.execute("""SELECT s.title, count(*) FROM chunks c JOIN sources s ON s.id=c.source_id
  WHERE c.text LIKE '%Project Gutenberg%' OR c.text LIKE '%digitized by the internet archive%'
  GROUP BY s.title ORDER BY 2 DESC LIMIT 8""").fetchall()
for t, c in rows:
    print(f"  {c:4d}  {t}")

# no-witness breakdown
import _fix_excerpts as FX
g = json.load(open('research/graph.json'))
led = json.load(open('research/ledger.json'))
srcs = {s['id']: s for s in led['sources']}
missing_sid = no_file = 0
for kind, items in [('H', [(n2['id'], h) for n2 in g['nodes'] for h in n2.get('highlights', [])]),
                    ('E', [(e['from'], x) for e in g['edges'] for x in e.get('excerpts', [])])]:
    for owner, it in items:
        sid = it.get('source_id')
        if not sid:
            continue
        if sid not in srcs:
            missing_sid += 1
        elif not FX.load_text(srcs[sid]):
            no_file += 1
print(f"\nno-witness items: source_id not in ledger={missing_sid}, ledger source with no file on disk={no_file}")

# which files are OCR-noisy (glyph salad)?
print("\n=== OCR noise score per evidence file (top offenders) ===")
import collections
for p in sorted(Path('evidence').rglob('*.txt')):
    raw = p.read_text(errors='replace')
    if len(raw) < 1000:
        continue
    weird = len(re.findall(r'[\ufffd\u25a0\u2022\u2190\u2192\u00c2\u00e2]|[\x00-\x08\x0b\x0c\x0e-\x1f]|\u200b|\u200c|\ufeff', raw))
    # ratio of non-ascii, non-standard-punct
    nonstd = sum(1 for c in raw if ord(c) > 127 and c not in '\u2019\u2018\u201c\u201d\u2014\u2013\u2026')
    if weird > 50 or nonstd / len(raw) > 0.01:
        print(f"  {p.name}: weird={weird} nonstd_ratio={nonstd/len(raw):.4f}")
