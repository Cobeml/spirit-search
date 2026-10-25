"""Second scouting pass: ledger tail, edge inventory for the 21, and targeted
anchor contexts missed by pass one. Read-only."""
import json, os, re

R = '/home/cobe-liu/Developing/spirit-search/research/'
EV = '/home/cobe-liu/Developing/spirit-search/evidence/'
ledger = json.load(open(R + 'ledger.json'))
g = json.load(open(R + 'graph.json'))
nodes = {n['id']: n for n in g['nodes']}

print('LEDGER ids 80+:')
for s in ledger['sources']:
    if s['id'] >= 80:
        print(f"  [{s['id']}] {s.get('title','')[:70]} | {s.get('url','')[:55]}")

TARGET = ['fdr', 'alexander-hamilton', 'benedict-arnold', 'numa-pompilius', 'romulus',
          'cato-elder', 'diancecht', 'goibniu', 'dagda', 'brigit', 'miach', 'manannan',
          'morrigan', 'balor', 'math', 'dylan', 'aranrod', 'maelgwn', 'tethys', 'theia', 'crius']
print('\nEXISTING EDGES on targets:')
for nid in TARGET:
    es = [e for e in g['edges'] if nid in (e['from'], e['to'])]
    print(f"  {nid:22s} " + '; '.join(f"{e['from']}->{e['to']}:{e['type']}" for e in es))

NAMEINFRA = R + '_nameinfra.py'
src = open(NAMEINFRA).read()
m = re.search(r"FILES\s*=\s*\{(.*?)\n\}", src, re.S)
print('\n_nameinfra FILES keys:' if m else '\n_nameinfra FILES: pattern not found')
if m:
    keys = re.findall(r"[\"']([\w.-]+)[\"']\s*:", m.group(1))
    print('  ' + ', '.join(keys))

def ctx(fn, pat, cap=3, back=130, fwd=300):
    fp = None
    for root, _, fns in os.walk(EV):
        if fn in fns:
            fp = os.path.join(root, fn)
    if not fp:
        print(f'  !! {fn} not found')
        return
    sq = re.sub(r'\s+', ' ', open(fp, encoding='utf-8', errors='ignore').read())
    shown = 0
    for m2 in re.finditer(pat, sq):
        s = max(0, m2.start() - back); e = min(len(sq), m2.end() + fwd)
        print(f'  [{fn[:20]}] ...{sq[s:e]}...')
        shown += 1
        if shown >= cap:
            return

print('\nNUMA in his own life:')
ctx('plutarch-lives-dryden-clough-gutenberg.txt', r'Numa (?:Pompilius|the king of the Romans|was descended)', 3)
ctx('plutarch-lives-dryden-clough-gutenberg.txt', r'NUMA POMPILIUS', 2)
ctx('plutarch-lives-dryden-clough-gutenberg.txt', r'Numa, (?:like|therefore)', 3)
print('\nCATO censor/own life:')
ctx('plutarch-lives-dryden-clough-gutenberg.txt', r'CATO (?:MAJOR|THE ELDER)', 2)
ctx('plutarch-lives-dryden-clough-gutenberg.txt', r'censor|Cato.{0,30}censor', 3)
print('\nARIANRHOD in Guest:')
ctx('guest-mabinogion-vol3-gutenberg.txt', r'Arianrhod', 3)
print('\nCRIUS/Eurybia:')
ctx('hesiod-evelynwhite-gutenberg348.txt', r'joined in love to Crius', 1, back=60, fwd=340)
print('\nDAGDA chief passage:')
ctx('macculloch-religion-ancient-celts-1911.txt', r'An early chief of the gods is Dagda', 1, back=80, fwd=420)
print('\nLivy1 Numa/Romulus naming:')
ctx('livy1-roberts.txt', r'Numa Pompilius', 2)
ctx('livy1-roberts.txt', r'Romulus, (?:having|when)', 2)
