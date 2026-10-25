"""Queue work 2026-10-21, batch 2: Roman exempla (numa-pompilius, romulus, cato-elder).
Registers Livy Book 1 (Wikisource, Canon Roberts) as a new ledger source with
programmatically sliced verbatim quotes. Idempotent on essay presence + source url."""
import json, re

ROOT = '/home/cobe-liu/Developing/spirit-search/research'
g = json.load(open(ROOT + '/graph.json'))
ledger = json.load(open(ROOT + '/ledger.json'))
TODAY = '2026-10-21'
LIVY1_URL = 'https://en.wikisource.org/wiki/From_the_Founding_of_the_City/Book_1'
LIVY1_FILE = ROOT + '/../evidence/_corpus/livy1-roberts.txt'

ESSAYS = {
    'numa-pompilius': (
        "Livy introduces him through the choice of the commons: 'There was living, in those "
        "days, at Cures, a Sabine city, a man of renowned justice and piety - Numa Pompilius. "
        "He was as conversant as any one in that age could be with all divine and human law.' "
        "[62]. Crowned by his predecessor's precedent, 'following the precedent set by "
        "Romulus, when he obtained his crown through the augury which sanctioned the founding "
        "of the City, Numa ordered that in his case also the gods should be consulted' [62]. "
        "Plutarch, whose Life begins from the noble pedigrees that 'go back in exact form as "
        "far as Numa Pompilius', shows the king turning a war people into farmers: 'Numa, "
        "therefore, hoping agriculture would be a sort of charm to captivate the affections "
        "of his people to peace' divided all the lands into parishes [61]. Even the sacred "
        "fire of Vesta is contested between the founders: 'Romulus was the first that "
        "consecrated holy fire, and instituted holy virgins to keep it, called vestals; "
        "others ascribe it to Numa Pompilius' [61]."),
    'romulus': (
        "Livy carries the founding through the twins: 'After the government of Alba was thus "
        "transferred to Numitor, Romulus and Remus were seized with the desire of building a "
        "city in the locality where they had been exposed' [62]. Plutarch preserves the "
        "wet-nurse etymology inside the name itself: 'they were called Romulus and Remus, "
        "(from ruma, the dug,) as we had before, because they were found sucking the wolf' "
        "[61]. He pairs the founder with Theseus, 'Theseus seemed to me to resemble Romulus "
        "in many particulars', both born out of wedlock, both 'had the repute of being "
        "sprung from the gods' [61]. The birth stories Plutarch reports and refuses are "
        "part of the record: some make him 'son to Aeneas and Dexithea', others the child of "
        "'Aemilia, daughter of Aeneas and Lavinia, had him by the god Mars; and others give "
        "you mere fables of his origin' [61]. The augury that legitimated the crown became "
        "the precedent Numa invoked at his own [62]."),
    'cato-elder': (
        "Plutarch opens the Life at Tusculum: 'Marcus Cato, we are told, was born at "
        "Tusculum, though (till he betook himself to civil and military affairs) he lived and "
        "was bred up in the country of the Sabines, where his father's estate lay' [61]. A "
        "soldier first: 'When Fabius Maximus took Tarentum, Cato, being then but a youth, was "
        "a soldier under him', lodged with the Pythagorean Nearchus and hearing the doctrine "
        "that 'pleasure is evil's chief bait; the body the principal calamity of the soul' "
        "[61]. The censor's voice Plutarch keeps in an aphorism: 'Cato Major, hearing some "
        "commend one that was rash, and inconsiderately daring in a battle, said, \"There is "
        "a difference between a man's prizing valor at a great rate, and valuing life at "
        "little\"' [61]. And the frame of the man is the discipline: 'everybody admired Cato, "
        "when they saw others sink under labors, and grow effeminate by pleasures; and yet "
        "beheld him unconquered by either', not only young and hungry for honor 'but also "
        "when old and greyheaded, after a consulship and triumph' [61]."),
}


def slice_quote(fp, anchor, back=40, fwd=520):
    """HTML-tolerant programmatic slice: strip tags if file is HTML-ish, squeeze
    whitespace, locate the anchor, cut a clean window, return the exact substring."""
    raw = open(fp, encoding='utf-8', errors='ignore').read()
    if raw.count('<') > 100:
        raw = re.sub(r'<style.*?</style>', ' ', raw, flags=re.S | re.I)
        raw = re.sub(r'<script.*?</script>', ' ', raw, flags=re.S | re.I)
        raw = re.sub(r'<[^>]+>', ' ', raw)
        raw = re.sub(r'&nbsp;', ' ', raw)
    sq = re.sub(r'\s+', ' ', raw).strip()
    i = sq.lower().find(anchor.lower())
    assert i >= 0, f'anchor not found: {anchor[:50]}'
    s = sq[i - back:i + fwd]
    s = s.strip()
    # end at a sentence boundary where possible
    m = re.search(r'[.!?](?=\s[A-Z\"])', s[80:])
    if m:
        s = s[:80 + m.end()]
    return s


# --- register Livy Book 1 with sliced verbatims (idempotent on url) ---
new_id = None
if not any(s.get('url') == LIVY1_URL for s in ledger['sources']):
    q1 = slice_quote(LIVY1_FILE, 'There was living, in those days, at Cures')
    q2 = slice_quote(LIVY1_FILE, 'After the government of Alba was thus transferred to Numitor')
    q3 = slice_quote(LIVY1_FILE, 'following the precedent set by Romulus')
    new_id = max(s['id'] for s in ledger['sources']) + 1
    ledger['sources'].append(dict(
        id=new_id, url=LIVY1_URL,
        title='Livy, Ab Urbe Condita Book 1, trans. Canon Roberts 1905 (Wikisource)',
        accessed=TODAY,
        quotes=[dict(text=q, added=TODAY) for q in (q1, q2, q3)]))
    print('livy1 registered as', f'[{new_id}]')
    for q in (q1, q2, q3):
        print('  quote:', q[:90], '...')
else:
    new_id = next(s['id'] for s in ledger['sources'] if s.get('url') == LIVY1_URL)
    print('livy1 already registered as', f'[{new_id}]')

# fix citation ids in the essays above to the actual ledger id
ESSAYS['numa-pompilius'] = ESSAYS['numa-pompilius'].replace('[62]', f'[{new_id}]')
ESSAYS['romulus'] = ESSAYS['romulus'].replace('[62]', f'[{new_id}]')

nodes = {n['id']: n for n in g['nodes']}
changed = []
for nid, essay in ESSAYS.items():
    n = nodes.get(nid)
    if n is None:
        print(f'!! node missing: {nid}')
        continue
    if not n.get('essay'):
        n['essay'] = essay
        changed.append(nid)
    else:
        print(f'  skip (essay exists): {nid}')

json.dump(g, open(ROOT + '/graph.json', 'w'), indent=2, ensure_ascii=False)
json.dump(ledger, open(ROOT + '/ledger.json', 'w'), indent=2, ensure_ascii=False)
print('essays set:', changed)
