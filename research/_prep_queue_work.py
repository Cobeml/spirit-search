"""Queue-work prep (2026-10-21): ledger state + witness mention map for the 21 thin nodes.

Prints, for each ledger source: id, title, url, n attached quotes. Then counts
padded mentions per evidence file for every thin-queue name so batch scripts can
mine before fetching. Never edits anything.
"""
import json, os, re

R = '/home/cobe-liu/Developing/spirit-search/research/'
EV = '/home/cobe-liu/Developing/spirit-search/evidence/'
ledger = json.load(open(R + 'ledger.json'))

print('LEDGER SOURCES (id | quotes | title | url):')
for s in ledger['sources']:
    print(f"  [{s['id']:>3}] q={len(s.get('quotes', []))} {s.get('title', '')[:66]} | {s.get('url', '')[:60]}")

NAMES = {
    'fdr': ['Roosevelt'], 'alexander-hamilton': ['Hamilton'],
    'numa-pompilius': ['Numa'], 'romulus': ['Romulus'], 'cato-elder': ['Cato'],
    'diancecht': ['Diancecht', 'Dian Cecht'], 'goibniu': ['Goibniu', 'Gobniu'],
    'dagda': ['Dagda'], 'brigit': ['Brigit', 'Brigit '],
    'miach': ['Miach'], 'manannan': ['Manannan', 'Manannán'],
    'morrigan': ['Morrigan', 'Morrigu', 'Morrigan'], 'balor': ['Balor'],
    'math': ['Math '], 'dylan': ['Dylan'], 'aranrod': ['Aranrod', 'Arianrod'],
    'maelgwn': ['Maelgwn'], 'tethys': ['Tethys'], 'theia': ['Theia'],
    'crius': ['Crius', 'Crios'], 'benedict-arnold': ['Arnold'],
}

files = []
for root, _, fns in os.walk(EV):
    for fn in fns:
        if fn.endswith('.imposter'):
            continue
        files.append(os.path.join(root, fn))

texts = {}
for fp in files:
    try:
        texts[fp] = open(fp, encoding='utf-8', errors='ignore').read()
    except Exception:
        pass

print('\nMENTION MAP (node -> file:count, top 4):')
for nid, variants in NAMES.items():
    hits = {}
    for fp, raw in texts.items():
        sq = re.sub(r'\s+', ' ', raw)
        n = 0
        for v in variants:
            n += len(re.findall(r'(?<![A-Za-z])' + re.escape(v) + r'(?![A-Za-z])', sq, re.I))
        if n:
            hits[os.path.relpath(fp, EV)] = n
    top = ', '.join(f'{os.path.basename(f)}:{c}' for f, c in sorted(hits.items(), key=lambda x: -x[1])[:4])
    print(f"  {nid:22s} total={sum(hits.values()):5d}  {top}")
