"""Queue work 2026-10-21: upgrade the fdr witness file (v3).

Replace evidence/_corpus/fdr-first-inaugural.txt with the full Avalon page
(header naming Roosevelt + salutation + address). The two surviving [45] quote
attachments (the wiki-layer thumb-captions are dropped as furniture) are
RE-SLICED from the new witness so every [45] quote is verbatim in the file that
evidences it, and a naming-header quote is attached for the first card."""
import html as H, json, re

ROOT = '/home/cobe-liu/Developing/spirit-search/research'
FP = ROOT + '/../evidence/_corpus/fdr-first-inaugural.txt'
SRC = '/home/cobe-liu/.hermes/cache/scratch/froos1.html'
LP = ROOT + '/ledger.json'
TODAY = '2026-10-21'
ledger = json.load(open(LP))
s45 = next(s for s in ledger['sources'] if s['id'] == 45)

raw = open(SRC, encoding='utf-8', errors='ignore').read()
raw = re.sub(r'<(style|script)[^>]*>.*?</\1>', ' ', raw, flags=re.S | re.I)
raw = re.sub(r'<!--.*?-->', ' ', raw, flags=re.S)
raw = re.sub(r'<br\s*/?>', '\n', raw, flags=re.I)
raw = re.sub(r'</(p|div|h\d)>', '\n\n', raw, flags=re.I)
raw = re.sub(r'<[^>]+>', ' ', raw)
raw = H.unescape(raw)
lines = [re.sub(r'\s+', ' ', ln).strip() for ln in raw.split('\n')]
text = '\n\n'.join(ln for ln in lines if ln)
text = re.sub(r'(?<=[a-z,!?"\')])--(?=[a-z])', '—', text)
norm = re.sub(r'\s+', ' ', text).strip()
assert 'Franklin D. Roosevelt' in norm, 'naming header lost in conversion'


def reslice(anchor, fwd=430):
    i = norm.find(anchor)
    assert i >= 0, 'anchor missing: ' + anchor
    s = norm[i:i + fwd]
    m = re.search(r'(?<=[.!?]) (?=[A-Z"“])', s[120:])
    if m:
        s = s[:120 + m.start() + 1].rstrip()
    return s.strip()


# drop wiki-layer furniture quotes; re-slice the survivors from this witness
keep, dropped = [], 0
for q in s45['quotes']:
    if 'thumb|' in q['text']:
        dropped += 1
        continue
    anchor = q['text'][:42]
    new_text = reslice(anchor)
    keep.append(dict(text=new_text, added=q.get('added', TODAY)))
print('dropped captions:', dropped, '| re-sliced:', len(keep))
for q in keep:
    print('  re-sliced:', q['text'][:88], '...')

hdr = reslice('Franklin D. Roosevelt', 240)
keep.append(dict(text=hdr, added=TODAY))
s45['quotes'] = keep
print('naming quote:', hdr[:130], '...')

open(FP, 'w', encoding='utf-8').write(text + '\n')
json.dump(ledger, open(LP, 'w'), indent=2, ensure_ascii=False)
print('witness + ledger written')
print('--- head of witness ---')
print(norm[:240])
