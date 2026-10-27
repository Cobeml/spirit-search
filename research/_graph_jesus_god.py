"""Add Jesus and God at Cobe's commission (thread 1564437497793085442, 2026-10-27).

Two nodes with essays and curated first cards, plus their edges discovered per
the standing methodology: co-occurrence slices from fetched witnesses, each
excerpt naming BOTH endpoints inside the 600-char window, quotes registered in
the ledger, influence fractions explicit in power_claims.json (0.0; pricing is
Cobe's gate), power proposals (never direct).

Witnesses (all on disk before this script runs):
  [317] KJV Genesis+Exodus   evidence/god/kjv-genesis-exodus-gutenberg.txt (1611)
  [318] KJV New Testament    evidence/jesus/kjv-newtestament-gutenberg.txt (1611)
  [319] Josephus, Antiquities evidence/jesus/josephus-antiquities-whiston-pg2848.txt (93)
  [320] Tacitus, Annals      evidence/jesus/tacitus-annals-mit.txt (116)
  [321] Pliny, Letters 10.96 evidence/jesus/pliny-trajan-georgetown.html (112)
  existing: [15] Weems 1800, [19] Ginzberg 1909, [40] Franklin Autobio 1771,
            [45] FDR First Inaugural 1933

Gutenberg KJV verse prefixes ('5:2') are edition navigation furniture; the
project convention (see the stored [18] Isaiah quotes) strips them from
slices. Idempotent on node id, source (url+title), edge (from,to,type).
"""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import FILES, expand_span, add_quote, GP, LP
from _audit_relevance import alias_patterns, text_quality

TODAY = '2026-10-27'
GOD = alias_patterns({'id': 'god', 'label': 'God'})
JESUS = alias_patterns({'id': 'jesus', 'label': 'Jesus of Nazareth'})

VERSES = re.compile(r"\s*\b\d{1,3}:\d{1,3}\b(?=\s+[A-Z])")

def strip_verses(text, kjv):
    return VERSES.sub('', text) if kjv else text

def hit_pos(text, pats):
    tc = ' ' + re.sub(r"[^a-z0-9]+", ' ', text.lower()).strip() + ' '
    tsq = re.sub(r"\s+", '', text.lower())
    best = None
    for p in pats:
        i = tc.find(p['na'])
        if i < 0 and p['long'] and p['sq'] in tsq:
            i = 10**6
        if i >= 0 and (best is None or i < best):
            best = i
    return best

def mentions(text, pats):
    return hit_pos(text, pats) is not None

def slice_clean(fp, anchor, pats_needed, kjv=True, occ=0, head=None,
                windows=((140, 520), (100, 420), (60, 320), (30, 240))):
    """Sentence-bounded slice around the anchor's occ-th match that names every
    pattern set in pats_needed and passes the seg/junk gate. head: optional
    regex; the stored slice starts at its first match (drops heading or
    preceding-verse carry-in from the sentence back-scan)."""
    t = FILES.get(fp)
    if t is None:
        raise SystemExit(f'!! missing evidence file: {fp}')
    ms = list(re.finditer(anchor, t, re.I))
    if not ms:
        raise SystemExit(f'!! anchor not found in {fp}: {anchor!r}')
    m = ms[min(occ, len(ms) - 1)]
    for back, fwd in windows:
        lo = max(0, m.start() - back)
        hi = min(len(t), m.end() + fwd)
        text = strip_verses(expand_span(t, lo, hi, max_fwd=800), kjv)
        if head is not None:
            hm = re.search(head, text)
            if hm and hm.start() > 0:
                text = text[hm.start():].lstrip()
        seg, junk = text_quality(text)
        if seg or junk:
            continue
        if all(mentions(text, pats) for pats in pats_needed):
            return text
    raise SystemExit(f'!! no clean slice for {anchor!r} in {fp}')

g = json.load(open(GP))
ledger = json.load(open(LP))
claims = json.load(open(Path(__file__).resolve().parent / 'power_claims.json'))
real = {n['id']: n for n in g['nodes']}

# ---------------- 1. ledger sources (idempotent on url+title) ----------------
NEW_SOURCES = [
    (317, 'https://www.gutenberg.org/cache/epub/10/pg10.txt',
     'KJV Bible, Genesis and Exodus (Gutenberg #10)'),
    (318, 'https://www.gutenberg.org/cache/epub/10/pg10.txt',
     'KJV Bible, New Testament (Gutenberg #10)'),
    (319, 'https://www.gutenberg.org/cache/epub/2848/pg2848.txt',
     'Josephus, Antiquities of the Jews, trans. Whiston (Gutenberg #2848)'),
    (320, 'http://classics.mit.edu/Tacitus/annals.mb.txt',
     'Tacitus, Annals, trans. Church and Brodribb (MIT Classics)'),
    (321, 'https://faculty.georgetown.edu/jod/texts/pliny.html',
     'Pliny, Letters 10.96-97, trans. from the Georgetown text'),
]
src_by_id = {s['id']: s for s in ledger['sources']}
for sid, url, title in NEW_SOURCES:
    if sid not in src_by_id:
        ledger['sources'].append({'id': sid, 'url': url, 'title': title,
                                   'accessed': TODAY, 'quotes': []})
        print(f'+ source [{sid}] {title}')
src_by_id = {s['id']: s for s in ledger['sources']}

def H(sid):
    s = src_by_id[sid]
    return {'source_id': sid, 'source_title': s['title'], 'source_url': s['url']}

def card(fp, anchor, sid, kjv=True, **kw):
    text = slice_clean(fp, anchor, [kw['names']], kjv=kjv,
                       occ=kw.get('occ', 0), head=kw.get('head'))
    add_quote(ledger, sid, text, TODAY)
    c = {'text': text, 'direct': True, 'manual': True}
    c.update(H(sid))
    return c

# ---------------- 2. nodes ----------------
GOD_ESSAY = (
    "The first sentence of the earliest fetched witness names him as the maker: "
    "'In the beginning God created the heaven and the earth' (Gen. 1:1) [317]. "
    "Genesis keeps him a speaker at every hinge of the generations: 'the LORD God "
    "called unto Adam, and said unto him, Where art thou' (Gen. 3:9) [317], and to "
    "the ninety-nine-year-old Abram, 'I am the Almighty God; walk before me, and be "
    "thou perfect' (Gen. 17:1) [317]. Exodus centers the revelation on the "
    "unmediated name: 'And God said unto Moses, I AM THAT I AM' (Exod. 3:14) [317]. "
    "The New Testament restates him as sender: 'For God so loved the world, that he "
    "gave his only begotten Son' (John 3:16) [318]. The flesh record reaches him "
    "through invocation: Weems's Washington campaigns 'with Jehovah, the God of "
    "Hosts' [15], Franklin's epitaph for his parents credits 'constant labor and "
    "industry, with God's blessing' [40], and Roosevelt's first inaugural closes "
    "'we humbly ask the blessing of God' [45].")

JESUS_ESSAY = (
    "Matthew opens by placing him at the end of a genealogy that runs through the "
    "Genesis cluster: 'The book of the generation of Jesus Christ, the son of "
    "David, the son of Abraham' (Matt. 1:1) [318]. The external record is three "
    "Roman notices. Josephus reports the execution under 'Pilate, at the "
    "suggestion of the principal men amongst us' and names 'the brother of Jesus, "
    "who was called Christ' (Ant. 18.3.3; 20.9.1) [319]. Tacitus dates the same "
    "event to 'the reign of Tiberius' at the hands of 'Pontius Pilatus' and calls "
    "the movement 'a most mischievous superstition' (Ann. 15.44) [320]. Pliny, "
    "interrogating adherents in Bithynia, finds them singing 'a hymn to Christ as "
    "to a god' before dawn (Ep. 10.96) [321]. The movement's own texts carry "
    "larger claims: 'All power is given unto me in heaven and in earth' (Matt. "
    "28:18) [318], and of the execution, 'Then said Jesus, Father, forgive them; "
    "for they know not what they do' (Luke 23:34) [318].")

GOD_NOTES = [(
    "Era 93: earliest fetched witness naming him is Josephus, Antiquities "
    "(composed 93/94 CE). The KJV enters the year table at 1611 as a document "
    "(settled with [18]); dating its Old Testament content to the Torah's "
    "redaction instead would move him to about -450, a one-line re-rule. Aliases "
    "exclude 'lord' alone: in the KJV New Testament 'the Lord' names Jesus; God "
    "takes the phrase forms ('the lord', 'lord god').")]
JESUS_NOTES = [(
    "Era 93: Josephus's Antiquities is the earliest fetched witness naming him; "
    "the gospels are older as content but enter as the 1611 KJV document. "
    "Neighbors discovered in the witnesses and held for the salience gate: "
    "Pontius Pilate (named by Tacitus, Josephus and the gospels), Tiberius, "
    "Trajan, Herod, Mary, Moses.")]

GE = 'evidence/god/kjv-genesis-exodus-gutenberg.txt'
NT = 'evidence/jesus/kjv-newtestament-gutenberg.txt'

GOD_CARDS = [
    (GE, r"In the beginning God created", 317, GOD, r"In the beginning God created"),
    (GE, r"formed man of the dust of the ground", 317, GOD, None),
    (GE, r"I AM THAT I AM", 317, GOD, None),
    (NT, r"For God so loved the world", 318, GOD, None),
]
JESUS_CARDS = [
    (NT, r"his name was called JESUS", 318, JESUS,
     r"And when eight days were accomplished"),
    (NT, r"Jesus came from Nazareth", 318, JESUS, None),
    (NT, r"Then said Jesus, Father, forgive them", 318, JESUS, None),
    ('evidence/jesus/josephus-antiquities-whiston-pg2848.txt',
     r"brother of Jesus, who was called Christ", 319, JESUS, None),
    ('evidence/jesus/tacitus-annals-mit.txt',
     r"Christus, from whom the name", 320, JESUS, None),
    ('evidence/jesus/pliny-trajan-georgetown.html',
     r"a hymn to Christ as to a god", 321, JESUS, r"They asserted, however"),
]

NODE_SPECS = [
    {'id': 'god', 'label': 'God', 'tradition': 'Hebrew Bible and Christian scripture',
     'era': 93, 'essay': GOD_ESSAY, 'notes': GOD_NOTES,
     'cards': GOD_CARDS},
    {'id': 'jesus', 'label': 'Jesus of Nazareth',
     'tradition': 'Judean flesh record, Christian scripture',
     'era': 93, 'essay': JESUS_ESSAY, 'notes': JESUS_NOTES,
     'cards': JESUS_CARDS},
]

for spec in NODE_SPECS:
    node = None
    for n in g['nodes']:
        if n['id'] == spec['id']:
            node = n
            break
    if node is None:
        g['nodes'].append({'id': spec['id'], 'label': spec['label'],
                           'tradition': spec['tradition'], 'batch': None,
                           'date_added': TODAY, 'era': spec['era']})
        node = g['nodes'][-1]
        print(f'+ node {spec["id"]}')
        for n in g['nodes']:
            if n['id'] == spec['id']:
                node = n
    if not node.get('essay'):
        node['essay'] = spec['essay']
        print(f'+ essay {spec["id"]}')
    if not node.get('notes'):
        node['notes'] = [{'date': TODAY, 'text': t} for t in spec['notes']]
    if not node.get('highlights'):
        cards = [card(fp, anc, sid, names=pats, head=head)
                 for fp, anc, sid, pats, head in spec['cards']]
        node['highlights'] = cards
        print(f'+ {len(cards)} highlight cards {spec["id"]}: first='
              f'{cards[0]["text"][:60]!r}')

# repair pass: the Pliny card originally sliced from 'They all worshipped...'
# and carried a stray page-marker ' p ' from the Georgetown HTML; re-slice it
# to start at the hymn passage.
for _n in g['nodes']:
    if _n['id'] != 'jesus':
        continue
    _h = _n.get('highlights', [])
    if _h and _h[-1]['source_id'] == 321 and ' p ' in _h[-1]['text']:
        _t = slice_clean('evidence/jesus/pliny-trajan-georgetown.html',
                         r"a hymn to Christ as to a god", [JESUS], kjv=False,
                         head=r"They asserted, however")
        add_quote(ledger, 321, _t, TODAY)
        _h[-1]['text'] = _t
        print('repaired jesus card 5:', _t[:70], '...')

# ---------------- 3. edges ----------------
# (frm, to, type, title, sid, era, file, anchor, [pattern sets]) ; kjv default
EDGE_SPECS = [
    ('god', 'adam', 'creation', 'Called their name Adam', 317, 1611, GE,
     r"generations of Adam", 'adam'),
    ('god', 'eve', 'interaction', 'I have gotten a man from the LORD', 317, 1611, GE,
     r"Adam knew Eve his wife", 'eve'),
    ('god', 'cain', 'interaction', 'Where is Abel thy brother', 317, 1611, GE,
     r"the LORD said unto Cain, Where is Abel thy brother", 'cain'),
    ('god', 'abel', 'interaction', 'The LORD had respect unto Abel', 317, 1611, GE,
     r"the LORD had respect unto Abel", 'abel'),
    ('god', 'noah', 'interaction', 'The end of all flesh is come before me',
     317, 1611, GE, r"God said unto Noah, The end of all flesh", 'noah'),
    ('god', 'abraham', 'interaction', 'I am the Almighty God; walk before me',
     317, 1611, GE,
     r"the LORD appeared to Abram, and said unto him, I am the Almighty God",
     'abraham'),
    ('god', 'isaac', 'interaction', 'Take now thy son, thine only son Isaac',
     317, 1611, GE, r"God did tempt Abraham", 'isaac'),
    ('god', 'jacob', 'interaction', 'Then shall the LORD be my God',
     317, 1611, GE, r"And Jacob vowed a vow", 'jacob'),
    ('god', 'joseph', 'interaction', 'The LORD was with Joseph',
     317, 1611, GE, r"the LORD was with Joseph", 'joseph'),
    ('god', 'enoch', 'interaction', 'Enoch walked with God',
     317, 1611, GE, r"Enoch lived sixty and five years", 'enoch'),
    ('god', 'lilith', 'conflict', 'God sent forth three angels',
     19, 1909, 'evidence/lilith/ginzberg-legends1-gutenberg.txt',
     r"God sent forth three angels", 'lilith'),
    ('god', 'jesus', 'kinship', 'The Son of God',
     318, 1611, NT, r"The beginning of the gospel of Jesus Christ", 'jesus'),
    ('god', 'george-washington', 'interaction', 'Jehovah, the God of Hosts, was with him',
     15, 1800, 'evidence/washington/weems_life_of_washington_archive_org_1800_djvu.txt',
     r"Jehovah, the God of Hosts", 'george-washington'),
    ('god', 'benjamin-franklin', 'interaction', 'Distrust not Providence',
     40, 1771, 'evidence/franklin/franklin-autobiography-pg20203.txt',
     r"with God's blessing", 'benjamin-franklin'),
]

has_edge = lambda f, t, ty: any(e['from'] == f and e['to'] == t and e['type'] == ty
                               for e in g['edges'])
added_edges = 0
for frm, to, ty, title, sid, era, fp, anchor, other in EDGE_SPECS:
    if has_edge(frm, to, ty):
        print(f'  skip edge {frm}->{to}')
        continue
    kjv = sid in (317, 318)
    other_pats = GOD if other == 'jesus' else (JESUS if other == 'god'
                                               else alias_patterns(real[other]))
    text = slice_clean(fp, anchor, [GOD, other_pats], kjv=kjv)
    pf, pt = hit_pos(text, GOD), hit_pos(text, other_pats)
    d = abs(pf - pt) if (pf is not None and pt is not None) else 9999
    if d > 600:
        raise SystemExit(f'!! {frm}->{to}: endpoints {d} apart, exceeds window')
    add_quote(ledger, sid, text, TODAY)
    s = src_by_id[sid]
    g['edges'].append({
        'from': frm, 'to': to, 'type': ty, 'title': title,
        'source': f"[{sid}] {s['title']}", 'essay': None,
        'date_added': TODAY, 'era': era, 'influence': None,
        'excerpts': [{'text': text, **H(sid)}]})
    added_edges += 1
    print(f'+ edge {frm}->{to} [{ty}] dist={d}: {text[:60]!r}')

# two-sided edge: the witness names God; Roosevelt is the speaker named by the
# document header (same convention as his first highlight card)
if not has_edge('god', 'fdr', 'interaction'):
    text = slice_clean('evidence/_corpus/fdr-first-inaugural.txt',
                       r"humbly ask the blessing of God", [GOD], kjv=False)
    add_quote(ledger, 45, text, TODAY)
    g['edges'].append({
        'from': 'god', 'to': 'fdr', 'type': 'interaction',
        'title': 'We humbly ask the blessing of God',
        'source': f"[45] {src_by_id[45]['title']}", 'essay': None,
        'date_added': TODAY, 'era': 1933, 'influence': None,
        'excerpts': [{'text': text, **H(45)}],
        'audit': {'ok': True, 'mode': 'two_sided'},
        'pairing_note': ('The address is Roosevelt\'s own act of dedication; the '
                         'Avalon document\'s header names him while the close '
                         'invokes God\'s blessing on the war-emergency office. '
                         'One witness carries both sides.'),
        'review': {'status': 'auto-added', 'date': TODAY}})
    added_edges += 1
    print(f'+ edge god->fdr [interaction, two_sided]: {text[:60]!r}')

# ---------------- 4. influence fractions (explicit, pricing is the gate) ------
inf_keys = {(e['from'], e['to'], e['type']) for e in claims['influence']}
for e in g['edges']:
    if e['from'] == 'god' or e['to'] == 'god':
        key = (e['from'], e['to'], e['type'])
        if key not in inf_keys:
            claims['influence'].append({'from': e['from'], 'to': e['to'],
                                        'type': e['type'], 'fraction': 0.0})
            print(f'+ influence 0.0 {e["from"]}->{e["to"]} [{e["type"]}]')

# ---------------- 5. power proposals (gate report, never direct) --------------
props = claims.setdefault('proposals', {})
if 'god' not in props:
    props['god'] = {
        'pool': 'P_authority', 'share': 0.0001, 'witness': 1.0,
        'role': 'named sovereign of the scriptural corpus',
        'why': ("King of kings in the fetched texts (Rev. 19:16 [318]); the "
                "flesh-record invocations address him as the seat of authority "
                "(Weems [15], Franklin [40], Roosevelt [45]). Share at the "
                "Tier-2 anchor; rescale by ruling."),
        'witness_files': [GE, NT,
                          'evidence/jesus/josephus-antiquities-whiston-pg2848.txt',
                          'evidence/lilith/ginzberg-legends1-gutenberg.txt']}
    print('+ proposal god P_authority 0.0001')
if 'jesus' not in props:
    props['jesus'] = {
        'pool': 'P_health', 'share': 0.00005, 'witness': 1.0,
        'role': 'healing practice and the authority claim',
        'why': ("The gospels document the healing practice ('they brought unto "
                "him all that were diseased', Matt. 4:24 [318]) and the authority "
                "claim ('All power is given unto me', Matt. 28:18 [318]); Pliny "
                "documents the cult addressing him 'as to a god' [321]. Health "
                "pool proposed; an authority share is the alternative; rescale "
                "by ruling."),
        'witness_files': [NT,
                          'evidence/jesus/josephus-antiquities-whiston-pg2848.txt',
                          'evidence/jesus/tacitus-annals-mit.txt',
                          'evidence/jesus/pliny-trajan-georgetown.html']}
    print('+ proposal jesus P_health 0.00005')

# ---------------- 6. write ----------------
shutil.copy(GP, GP.with_suffix('.json.bakJG'))
shutil.copy(LP, LP.with_suffix('.json.bakJG'))
json.dump(g, open(GP, 'w'), indent=2, ensure_ascii=False)
json.dump(ledger, open(LP, 'w'), indent=2, ensure_ascii=False)
json.dump(claims, open(Path(__file__).resolve().parent / 'power_claims.json', 'w'),
          indent=2, ensure_ascii=False)
print(f'DONE: {len(g["nodes"])} nodes, {len(g["edges"])} edges '
      f'(+{added_edges} this run)')
