"""Adam card, final fix: span from 'Later on God made the plants' through the
Adam-naming sentence ('...only after Adam was created.'), scrubbed of the [n]
locator furniture, so the first card names him and ends at a sentence boundary."""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _textclean as TC
from _nameinfra import GP

g = json.load(open(GP))
byid = {n['id']: n for n in g['nodes']}
t = open('/home/cobe-liu/Developing/spirit-search/evidence/lilith/ginzberg-legends1-gutenberg.txt',
         encoding='utf-8', errors='ignore').read()

i1 = re.search(r'Later\s+on\s+God\s+made\s+the\s+plants', t)
assert i1
s = TC._prev_boundary(t, i1.start())
i2 = t.find('only after Adam was created')
assert i2 > 0
e = TC._next_boundary(t, i2 + 10)
assert e and e > s, (s, e)
span = TC.scrub_slice(t[s:e])
assert span and 'Adam was created' in span and 'Later on God made the plants' in span
print('new card:', repr(span[:180]))

adam = byid['adam']
fixed = 0
for h in adam.get('highlights', []):
    if h['text'].startswith('Later on God made the plants'):
        h['text'] = span
        h.setdefault('audit', {})
        h['audit'].pop('seg', None)
        h['audit'].pop('junk', None)
        fixed += 1
assert fixed == 1, fixed
json.dump(g, open(GP, 'w'), indent=1, ensure_ascii=False)
print('adam first card replaced; graph.json written')
