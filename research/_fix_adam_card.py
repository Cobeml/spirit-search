"""Re-slice adam's mid-sentence Ginzberg card (2nd attempt): locate the card head
with a whitespace-tolerant regex in the RAW evidence text (offsets valid), then
take the whole scrubbed sentence via sentence_at."""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import FILES, sentence_at, GP

g = json.load(open(GP))
byid = {n['id']: n for n in g['nodes']}
adam = byid['adam']
fp = 'evidence/lilith/ginzberg-legends1-gutenberg.txt'
t = FILES[fp]

rx = re.compile(r'Later\s+on\s+God\s+made\s+the\s+plants\s+dependent\s+upon\s+the\s+rain')
m = rx.search(t)
assert m, 'card head not found in raw text'
snt = sentence_at(t, m.start())
assert snt and len(snt) > 60, f'bad sentence slice: {snt!r}'
print('re-sliced card ->', repr(snt[:160]))

fixed = 0
for h in adam.get('highlights', []):
    if re.sub(r'\s+', ' ', h['text']).startswith('Later on God made the plants'):
        h['text'] = snt
        h.setdefault('audit', {})
        h['audit'].pop('seg', None)
        h['audit'].pop('junk', None)
        fixed += 1
print('cards fixed:', fixed)

json.dump(g, open(GP, 'w'), indent=1, ensure_ascii=False)
print('graph.json written')
