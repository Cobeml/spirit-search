"""Witness availability probe for unpriced power-holders (2026-10-21).

Counts padded (word-boundary) mentions per evidence file for each Tier-1
flesh-record node, so power proposals can carry a defensible witness-strength.
"""
import os, re, collections

EV = '/home/cobe-liu/Developing/spirit-search/evidence/'
NAMES = {
    'henry-knox': ['Knox'], 'alexander-hamilton': ['Hamilton'],
    'thomas-jefferson': ['Jefferson'], 'john-jay': ['Jay'],
    'benedict-arnold': ['Arnold'], 'charles-lee': ['Charles Lee', 'Gen. Lee'],
    'aaron-burr': ['Burr'], 'james-wilson': ['James Wilson'],
    'edward-braddock': ['Braddock'], 'newton': ['Newton'],
    'faraday': ['Faraday'], 'galen': ['Galen'],
    'cincinnatus': ['Cincinnatus'], 'sulla': ['Sulla'],
    'fabius-maximus': ['Fabius'], 'marcellus': ['Marcellus'],
    'marcius-coriolanus': ['Coriolanus'], 'numa-pompilius': ['Numa'],
    'romulus': ['Romulus'], 'cato-elder': ['Cato'],
    'valerius-publicola': ['Publicola', 'Poplicola'],
    'aemilius-paullus': ['Aemilius', 'Paullus'], 'maelgwn': ['Maelgwn'],
    'adam-smith': ['Adam Smith'],
}

files = []
for root, _, fns in os.walk(EV):
    for fn in fns:
        if fn.endswith(('.txt', '.html', '.imposter')) or fn.startswith('_'):
            if fn.endswith('.imposter'):
                continue
            files.append(os.path.join(root, fn))

texts = {}
for fp in files:
    try:
        raw = open(fp, encoding='utf-8', errors='ignore').read()
        if len(raw) > 3_000_000:  # skip monsters for speed? keep them, they matter
            pass
        texts[fp] = raw
    except Exception:
        pass

for nid, variants in NAMES.items():
    hits = collections.Counter()
    for fp, raw in texts.items():
        sq = re.sub(r'\s+', ' ', raw)  # OCR-squeezed view for padded matching
        n = 0
        for v in variants:
            n += len(re.findall(r'(?<![A-Za-z])' + re.escape(v) + r'(?![A-Za-z])', sq, re.I))
        if n:
            hits[os.path.relpath(fp, EV)] = n
    top = ', '.join(f'{os.path.basename(f)}:{c}' for f, c in hits.most_common(4))
    print(f"{nid:22s} total={sum(hits.values()):5d}  {top}")
