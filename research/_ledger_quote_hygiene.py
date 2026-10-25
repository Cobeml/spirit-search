"""Queue work 2026-10-21: ledger quote hygiene for [45] (fdr) and [270] (Livy 1).

[45] naming quote re-sliced from the document header block (First Inaugural
Address of Franklin D. Roosevelt / SATURDAY, MARCH 4, 1933 / opening sentence)
instead of the page-title/nav text. [270]'s quotes re-sliced starting AT their
anchors (no mid-word back-context, no wiki [ edit ] furniture). Verifies every
quote of both sources is verbatim in its witness file."""
import html as H, json, re

ROOT = '/home/cobe-liu/Developing/spirit-search/research'
LP = ROOT + '/ledger.json'
FP45 = ROOT + '/../evidence/_corpus/fdr-first-inaugural.txt'
FP270 = ROOT + '/../evidence/_corpus/livy1-roberts.txt'
ledger = json.load(open(LP))
S = {s['id']: s for s in ledger['sources']}
TODAY = '2026-10-21'


def norm(fp):
    raw = open(fp, encoding='utf-8', errors='ignore').read()
    if raw.count('<') > 100:
        raw = re.sub(r'<(style|script)[^>]*>.*?</\1>', ' ', raw, flags=re.S | re.I)
        raw = re.sub(r'<!--.*?-->', ' ', raw, flags=re.S)
        raw = re.sub(r'<[^>]+>', ' ', raw)
        raw = H.unescape(raw)
    return re.sub(r'\s+', ' ', raw).strip()


def reslice(sq, anchor, fwd=460, stop=140):
    i = sq.find(anchor)
    assert i >= 0, 'anchor missing: ' + anchor[:50]
    s = sq[i:i + fwd]
    m = re.search(r'(?<=[.!?]) (?=[A-Z"“(])', s[stop:])
    if m:
        s = s[:stop + m.start() + 1]
    return s.strip()


# --- [45] naming quote from the document header block ---
n45 = norm(FP45)
q45 = S[45]['quotes']
hdr = reslice(n45, 'First Inaugural Address of Franklin D. Roosevelt SATURDAY, MARCH 4, 1933', fwd=380, stop=160)
assert 'Franklin D. Roosevelt' in hdr and 'impels' in hdr
q45 = [q for q in q45 if 'Avalon Home' not in q['text']]
if not any(q['text'] == hdr for q in q45):
    q45.append(dict(text=hdr, added=TODAY))
S[45]['quotes'] = q45
print('[45] naming quote:', hdr[:150], '...')

# --- [270] quotes re-sliced from clean anchors ---
n270 = norm(FP270)
anchors = [
    'There was living, in those days, at Cures, a Sabine city',
    'After the government of Alba was thus transferred to Numitor',
    'He was invited to Rome, and following the precedent set by Romulus',
]
new270 = [dict(text=reslice(n270, a), added=TODAY) for a in anchors]
S[270]['quotes'] = new270
for q in new270:
    assert '[ edit ]' not in q['text'] and ' [1' not in q['text']
    print('[270] quote:', q['text'][:120], '...')

# --- verify every quote of both sources is verbatim in its witness ---
for sid, fp in ((45, FP45), (270, FP270)):
    sq = norm(fp)
    for q in S[sid]['quotes']:
        qn = re.sub(r'\s+', ' ', q['text']).strip()
        assert qn in sq, f'[{sid}] quote not in witness: ' + qn[:60]
print('all [45] + [270] quotes verified verbatim in their witness files')

json.dump(ledger, open(LP, 'w'), indent=2, ensure_ascii=False)
print('ledger written')
