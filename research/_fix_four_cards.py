"""Queue work 2026-10-21: repair the four text-quality flags from the audit.

Drops pure scan/boilerplate furniture cards (gilgamesh Jastrow cover slice,
mason-weems Internet Archive strip, cupid 'curiositie:' gloss slice) and
re-slices adam's mid-sentence Ginzberg card to clean sentence bounds.
Run AFTER _manual_firsts.py so cupid's re-pinned card is in place."""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import FILES, sentence_at, register_file_source, add_quote, LP

GP = Path(__file__).resolve().parent / 'graph.json'
g = json.load(open(GP))
ledger = json.load(open(LP))
byid = {n['id']: n for n in g['nodes']}

DROP = {
    'gilgamesh': lambda h: h['text'].lstrip().startswith('JASTROW'),
    'mason-weems': lambda h: 'Digitized by the Internet Archive' in h['text'],
    'cupid': lambda h: h['text'].lstrip().lower().startswith('curiositie'),
}
for nid, pred in DROP.items():
    n = byid[nid]
    before = len(n.get('highlights', []))
    n['highlights'] = [h for h in n.get('highlights', []) if not pred(h)]
    print(f'{nid}: {before} -> {len(n["highlights"])} cards')

# adam: re-slice the mid-sentence Ginzberg card to whole scrubbed sentences
adam = byid['adam']
fp = 'evidence/lilith/ginzberg-legends1-gutenberg.txt'
t = FILES.get(fp)
assert t, 'ginzberg file not in FILES'
fixed = 0
for h in adam.get('highlights', []):
    head = re.sub(r'\s+', ' ', h['text'])[:40]
    i = t.find(head.split()[0])
    # locate the card by its squeezed prefix
    sq = re.sub(r'\s+', ' ', t)
    j = sq.find(head)
    if j < 0:
        print('  adam: card head not found:', head)
        continue
    # map squeezed offset back is unreliable; re-slice by locating whole card text
    qn = re.sub(r'\s+', ' ', h['text']).strip()
    k = sq.find(qn)
    if k < 0:
        k = j
    snt = sentence_at(t, k)
    if snt and len(snt) > 60 and 'Adam' in snt:
        if re.sub(r'\s+', ' ', snt).strip() != qn:
            h['text'] = snt
            h.setdefault('audit', {})
            h['audit'].pop('seg', None)
            h['audit'].pop('junk', None)
            fixed += 1
            print(f'  adam: re-sliced -> {snt[:90]!r}')
print('adam cards re-sliced:', fixed)

json.dump(g, open(GP, 'w'), indent=1, ensure_ascii=False)
print('graph.json written')
