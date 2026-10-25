"""Clean the fdr witness file: keep the document block (header + date + address)
from the full Avalon page text; drop the nav header list and the footer boilerplate."""
import re, json

FP = '/home/cobe-liu/Developing/spirit-search/evidence/_corpus/fdr-first-inaugural.txt'
LP = '/home/cobe-liu/Developing/spirit-search/research/ledger.json'
t = open(FP, encoding='utf-8').read()

# document block: the 'First Inaugural Address...' heading followed by SATURDAY
m = re.search(r'\n(First Inaugural Address of Franklin D\. Roosevelt\s*\n+\s*SATURDAY, MARCH 4, 1933)', t)
assert m, 'document header not found'
start = m.start() + 1
end_m = re.search(r'May He guide me in the days to come\.', t)
assert end_m, 'address end not found'
end = end_m.end()
clean = t[start:end].strip()
norm = re.sub(r'\s+', ' ', clean)
assert 'Franklin D. Roosevelt' in norm and 'fear itself' in norm

ledger = json.load(open(LP))
s45 = next(s for s in ledger['sources'] if s['id'] == 45)
for q in s45['quotes']:
    qn = re.sub(r'\s+', ' ', q['text']).strip()
    assert qn in norm, 'quote lost: ' + qn[:60]
print('all [45] quotes verified in cleaned witness')

open(FP, 'w', encoding='utf-8').write(clean + '\n')
print('cleaned witness written:', len(clean), 'chars')
print('--- head ---')
print(norm[:200])
print('--- tail ---')
print(norm[-160:])
