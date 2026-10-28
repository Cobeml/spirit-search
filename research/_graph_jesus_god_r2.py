"""Round 2 of the Jesus/God commission (Cobe 2026-10-27: 'Continue watt pricing
and edge expansion of Jesus and God... build it out').

Six neighbor nodes discovered in the on-disk witnesses, all review-tagged
auto-added: pontius-pilate, moses, mary, tiberius, herod-antipas,
john-the-baptist. Every excerpt names both endpoints inside 600 chars of
FIRST-HIT positions (the audit's measure). Kinship/transmission edges get
explicit 0.0 influence entries so nothing silently routes 20% when the
office-holders get priced.

Witnesses all registered in round 1: [317] KJV Genesis-Exodus, [318] KJV NT,
[319] Josephus, [320] Tacitus. Idempotent on node id, edge (from,to,type),
proposal id.
"""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import FILES, expand_span, add_quote, GP, LP
from _audit_relevance import alias_patterns, text_quality

TODAY = '2026-10-27'
CP = Path(__file__).resolve().parent / 'power_claims.json'

def P(i, l):
    return alias_patterns({'id': i, 'label': l})

GOD = P('god', 'God')
JESUS = P('jesus', 'Jesus of Nazareth')
PATS = {nid: P(nid, lab) for nid, lab in [
    ('pontius-pilate', 'Pontius Pilate'), ('moses', 'Moses'),
    ('mary', 'Mary (mother of Jesus)'), ('tiberius', 'Tiberius'),
    ('herod-antipas', 'Herod Antipas'), ('john-the-baptist', 'John the Baptist')]}

VERSES = re.compile(r"\s*\b\d{1,3}:\d{1,3}\b(?=\s+[A-Z])")

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
        text = expand_span(t, lo, hi, max_fwd=800)
        if kjv:
            text = VERSES.sub('', text)
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
claims = json.load(open(CP))
src_by_id = {s['id']: s for s in ledger['sources']}

def H(sid):
    s = src_by_id[sid]
    return {'source_id': sid, 'source_title': s['title'], 'source_url': s['url']}

GE = 'evidence/god/kjv-genesis-exodus-gutenberg.txt'
NT = 'evidence/jesus/kjv-newtestament-gutenberg.txt'
JOS = 'evidence/jesus/josephus-antiquities-whiston-pg2848.txt'
TAC = 'evidence/jesus/tacitus-annals-mit.txt'

# ---------------- nodes: essays, cards, notes ----------------
NODES = [
 {'id': 'pontius-pilate', 'label': 'Pontius Pilate',
  'tradition': 'Roman prefect of Judaea, flesh record', 'era': 93,
  'essay': (
    "Matthew places the delivery at morning: 'all the chief priests and elders "
    "of the people took counsel against Jesus to put him to death. And when "
    "they had bound him, they led him away, and delivered him to Pontius "
    "Pilate the governor' (Matt. 27:1-2) [318]. Josephus names him inside the "
    "execution report: 'when Pilate, at the suggestion of the principal men "
    "amongst us, had condemned him to the cross' (Ant. 18.3.3) [319]. Tacitus "
    "gives him the imperial title and the responsibility: the movement's "
    "founder 'suffered the extreme penalty during the reign of Tiberius at "
    "the hands of one of our procurators, Pontius Pilatus' (Ann. 15.44) [320]. "
    "Luke dates his governorship by the emperor: 'Now in the fifteenth year of "
    "the reign of Tiberius Caesar, Pontius Pilate being governor of Judaea' "
    "(Luke 3:1) [318]. Matthew preserves the absolution gesture: 'When Pilate "
    "saw that he could prevail nothing, but that rather a tumult was made, he "
    "took water, and washed his hands before the multitude, saying, I am "
    "innocent of the blood of this just person' (Matt. 27:24) [318]."),
  'cards': [
    (NT, r"took counsel against Jesus to put him to death", 318,
     'When the morning was come'),
    (JOS, r"at the suggestion of the principal men", 319, 'And when Pilate'),
    (TAC, r"suffered the extreme penalty", 320, 'Christus, from whom'),
    (NT, r"he took water, and washed his hands", 318, None)],
  'note': ("Era 93: Josephus's Antiquities names him (Ant. 18.3.1-3). Office "
           "documented in three witnesses (Tacitus procurator, Josephus "
           "procurator, Luke 3:1 governor); pricing proposal filed.")},
 {'id': 'moses', 'label': 'Moses', 'tradition': 'Hebrew Bible, flesh record',
  'era': 93,
  'essay': (
    "The bush episode puts the address in doubled words: 'God called unto him "
    "out of the midst of the bush, and said, Moses, Moses. And he said, Here "
    "am I' (Exod. 3:4) [317]. The commission follows, and the reluctance with "
    "it: 'And Moses said unto God, Who am I, that I should go unto Pharaoh, "
    "and that I should bring forth the children of Israel out of Egypt?' "
    "(Exod. 3:11) [317]. Josephus reads him as a lawgiver working from a "
    "theology: 'Moses deemed it exceeding necessary, that he who would "
    "conduct his own life well, and give laws to others, in the first place "
    "should consider the Divine nature' (Ant. 2) [319]. The New Testament "
    "stages him at the transfiguration: 'there appeared unto them Moses and "
    "Elias talking with him' (Matt. 17:3) [318]."),
  'cards': [
    (GE, r"God called unto him out of the midst of the bush", 317,
     'And the angel of the LORD appeared'),
    (GE, r"Who am I, that I should go", 317, 'And Moses said unto God, Who am I'),
    (JOS, r"Moses deemed it exceeding necessary", 319, None),
    (NT, r"there appeared unto them Moses and Elias", 318, 'And after six days')],
  'note': ("Era 93: Josephus's Antiquities (Books 2-4 are the Moses history) "
           "names him 466 times; the KJV counts as the 1611 document. Host "
           "command documented ([317] the Exodus commission); pricing "
           "proposal filed.")},
 {'id': 'mary', 'label': 'Mary (mother of Jesus)', 'tradition': 'Christian scripture',
  'era': 1611,
  'essay': (
    "The annunciation carries the naming and her consent: 'the angel said "
    "unto her, Fear not, Mary: for thou hast found favour with God. And, "
    "behold, thou shalt conceive in thy womb, and bring forth a son, and "
    "shalt call his name JESUS' (Luke 1:30-31) [318]. Matthew fixes her "
    "position in the legal genealogy of the child: 'Now the birth of Jesus "
    "Christ was on this wise: When as his mother Mary was espoused to "
    "Joseph, before they came together, she was found with child of the Holy "
    "Ghost' (Matt. 1:18) [318]. Her own voice survives in the Magnificat: "
    "'And Mary said, My soul doth magnify the Lord, And my spirit hath "
    "rejoiced in God my Saviour' (Luke 1:46-47) [318]. Luke records the "
    "keeping: 'But Mary kept all these things, and pondered them in her "
    "heart' (Luke 2:19) [318]."),
  'cards': [
    (NT, r"Fear not, Mary: for thou hast found favour with God", 318,
     'And the angel said unto her, Fear not'),
    (NT, r"My soul doth magnify the Lord", 318, 'And Mary said, My soul'),
    (NT, r"the birth of Jesus Christ was on this wise", 318,
     'Now the birth of Jesus Christ'),
    (NT, r"kept all these things, and pondered them in her heart", 318,
     'But Mary kept all these things')],
  'note': ("Era 1611: the earliest fetched witness naming her is the KJV New "
           "Testament; Josephus prints no 'Mary' (the Herodian Mariamne is a "
           "different name-form). Alias 'mary' also matches Magdalene in NT "
           "windows; curated cards only. No office: no pricing proposal.")},
 {'id': 'tiberius', 'label': 'Tiberius', 'tradition': 'Roman emperor, flesh record',
  'era': 93,
  'essay': (
    "Tacitus fixes the execution inside his reign: 'Christus, from whom the "
    "name had its origin, suffered the extreme penalty during the reign of "
    "Tiberius at the hands of one of our procurators, Pontius Pilatus' (Ann. "
    "15.44) [320]. Luke opens John's ministry on the same reign: 'Now in the "
    "fifteenth year of the reign of Tiberius Caesar, Pontius Pilate being "
    "governor of Judaea, and Herod being tetrarch of Galilee' (Luke 3:1) "
    "[318]. Josephus shows the frontier wars reaching his desk: 'So Herod "
    "wrote about these affairs to Tiberius, who being very angry at the "
    "attempt made by Aretas, wrote to Vitellius to make war upon him' (Ant. "
    "18.5.1) [319]."),
  'cards': [
    (TAC, r"suffered the extreme penalty", 320, 'Christus, from whom'),
    (NT, r"fifteenth year of the reign of Tiberius", 318,
     'Now in the fifteenth year'),
    (JOS, r"So Herod wrote about these affairs to Tiberius", 319, None)],
  'note': ("Era 93: Josephus names Tiberius 90 times. The princeps under whom "
           "the execution notice falls in both Roman witnesses; pricing "
           "proposal filed.")},
 {'id': 'herod-antipas', 'label': 'Herod Antipas',
  'tradition': 'Tetrarch of Galilee, flesh record', 'era': 93,
  'essay': (
    "Luke places him over Galilee at the same date as Pilate's governorship: "
    "'Now in the fifteenth year of the reign of Tiberius Caesar, Pontius "
    "Pilate being governor of Judaea, and Herod being tetrarch of Galilee' "
    "(Luke 3:1) [318]. The trial scene gives him his one audience: 'And when "
    "Herod saw Jesus, he was exceeding glad... and he questioned with him in "
    "many words; but he answered him nothing' (Luke 23:8-9) [318]. Matthew "
    "reports the identification rumor: 'At that time Herod the tetrarch "
    "heard of the fame of Jesus, And said unto his servants, This is John "
    "the Baptist; he is risen from the dead' (Matt. 14:1-2) [318]. Josephus "
    "gives the Baptist's death its politics: 'Herod, who feared lest the "
    "great influence John had over the people might put it into his power "
    "and inclination to raise a rebellion, thought it best, by putting him "
    "to death, to prevent any mischief he might do' (Ant. 18.5.2) [319]."),
  'cards': [
    (NT, r"And when Herod saw Jesus", 318, 'And as soon as he knew that he belonged'),
    (NT, r"At that time Herod the tetrarch heard", 318, 'At that time Herod'),
    (JOS, r"Herod, who feared lest the great influence", 319, None),
    (NT, r"fifteenth year of the reign of Tiberius", 318,
     'Now in the fifteenth year')],
  'note': ("Era 93: Josephus's Antiquities 18 names 'Herod the tetrarch'. "
           "Alias 'herod' also matches Herod the Great (Matt. 2) and "
           "Archelaus's reign; this node is the tetrarch of the trial, the "
           "Baptist's death, and Josephus 18.5. Curated windows only. "
           "Tetrarch office documented; pricing proposal filed.")},
 {'id': 'john-the-baptist', 'label': 'John the Baptist',
  'tradition': 'Judean prophet, flesh record', 'era': 93,
  'essay': (
    "Matthew introduces him by the full style: 'In those days came John the "
    "Baptist, preaching in the wilderness of Judaea' (Matt. 3:1) [318]. The "
    "baptism is his office's central act: 'Then cometh Jesus from Galilee to "
    "Jordan unto John, to be baptized of him. But John forbad him, saying, I "
    "have need to be baptized of thee, and comest thou to me?' (Matt. 3:13-14) "
    "[318]. Josephus reports the same man under the tetrarch's custody: "
    "'John, that was called the Baptist... commanded the Jews to exercise "
    "virtue... was sent a prisoner, out of Herod's suspicious temper, to "
    "Macherus... and there put to death' (Ant. 18.5.2) [319]."),
  'cards': [
    (NT, r"came John the Baptist, preaching", 318,
     'In those days came John the Baptist'),
    (NT, r"Then cometh Jesus from Galilee to Jordan", 318, 'Then cometh Jesus'),
    (JOS, r"John, that was called the Baptist", 319,
     'Now some of the Jews thought'),
    (NT, r"At that time Herod the tetrarch heard", 318, 'At that time Herod')],
  'note': ("Era 93: Josephus 18.5.2 names him. Alias 'john' also matches the "
           "apostle in NT windows; curated cards only (the wilderness, the "
           "baptism, Josephus's prisoner, the Herod rumor). No office: no "
           "pricing proposal.")},
]

for spec in NODES:
    node = next((n for n in g['nodes'] if n['id'] == spec['id']), None)
    if node is None:
        g['nodes'].append({'id': spec['id'], 'label': spec['label'],
                           'tradition': spec['tradition'], 'batch': None,
                           'date_added': TODAY, 'era': spec['era'],
                           'review': {'status': 'auto-added', 'date': TODAY},
                           'notes': [{'date': TODAY, 'text': spec['note']}]})
        node = g['nodes'][-1]
        print(f'+ node {spec["id"]}')
    if not node.get('essay'):
        node['essay'] = spec['essay']
        print(f'+ essay {spec["id"]}')
    if not node.get('highlights'):
        cards = []
        for fp, anc, sid, head in spec['cards']:
            kjv = fp in (GE, NT)
            text = slice_clean(fp, anc, [PATS[spec['id']]], kjv=kjv, head=head)
            add_quote(ledger, sid, text, TODAY)
            cards.append({'text': text, 'direct': True, 'manual': True, **H(sid)})
        node['highlights'] = cards
        print(f'+ {len(cards)} cards {spec["id"]}: first={cards[0]["text"][:60]!r}')

# ---------------- edges ----------------
EDGES = [
    # frm, to, type, title, sid, era, file, anchor, other
    ('god', 'moses', 'interaction', 'Moses, Moses', 317, 1611, GE,
     r"God called unto him out of the midst of the bush", 'moses'),
    ('moses', 'jesus', 'transmission', 'Moses and Elias, talking with him',
     318, 1611, NT, r"there appeared unto them Moses and Elias", 'jesus'),
    ('pontius-pilate', 'jesus', 'interaction',
     'Delivered him to Pontius Pilate the governor', 318, 1611, NT,
     r"took counsel against Jesus to put him to death", 'jesus'),
    ('tiberius', 'jesus', 'interaction',
     'The extreme penalty in the reign of Tiberius', 320, 116, TAC,
     r"suffered the extreme penalty", 'jesus'),
    ('tiberius', 'pontius-pilate', 'agency',
     'Governor of Judaea under Tiberius Caesar', 318, 1611, NT,
     r"fifteenth year of the reign of Tiberius", 'pontius-pilate'),
    ('tiberius', 'herod-antipas', 'agency',
     'Tetrarch of Galilee under Tiberius Caesar', 318, 1611, NT,
     r"fifteenth year of the reign of Tiberius", 'herod-antipas'),
    ('mary', 'jesus', 'kinship', 'Shalt call his name JESUS', 318, 1611, NT,
     r"Fear not, Mary: for thou hast found favour with God", 'jesus'),
    ('god', 'mary', 'interaction', 'Thou hast found favour with God',
     318, 1611, NT, r"Fear not, Mary: for thou hast found favour with God",
     'mary'),
    ('herod-antipas', 'jesus', 'interaction', 'When Herod saw Jesus',
     318, 1611, NT, r"And when Herod saw Jesus", 'jesus'),
    ('herod-antipas', 'john-the-baptist', 'conflict',
     'Out of Herod\'s suspicious temper', 319, 93, JOS,
     r"Herod, who feared lest the great influence", 'john-the-baptist'),
    ('john-the-baptist', 'jesus', 'interaction', 'To be baptized of him',
     318, 1611, NT, r"Then cometh Jesus from Galilee to Jordan", 'jesus'),
    ('pontius-pilate', 'herod-antipas', 'interaction',
     'Belonged unto Herod\'s jurisdiction', 318, 1611, NT,
     r"And when Herod saw Jesus", 'herod-antipas'),
]

PAT_FOR = {'god': GOD, 'jesus': JESUS, **PATS}
has_edge = lambda f, t, ty: any(e['from'] == f and e['to'] == t and e['type'] == ty
                               for e in g['edges'])
added = 0
for frm, to, ty, title, sid, era, fp, anchor, other in EDGES:
    if has_edge(frm, to, ty):
        print(f'  skip edge {frm}->{to}')
        continue
    kjv = fp in (GE, NT)
    pa, pb = PAT_FOR[frm], PAT_FOR[to]
    text = slice_clean(fp, anchor, [pa, pb], kjv=kjv)
    pf, pt = hit_pos(text, pa), hit_pos(text, pb)
    d = abs(pf - pt) if (pf is not None and pt is not None) else 9999
    if d > 600:
        raise SystemExit(f'!! {frm}->{to}: first-hit distance {d} exceeds 600')
    add_quote(ledger, sid, text, TODAY)
    g['edges'].append({
        'from': frm, 'to': to, 'type': ty, 'title': title,
        'source': f"[{sid}] {src_by_id[sid]['title']}", 'essay': None,
        'date_added': TODAY, 'era': era, 'influence': None,
        'review': {'status': 'auto-added', 'date': TODAY},
        'excerpts': [{'text': text, **H(sid)}]})
    added += 1
    print(f'+ edge {frm}->{to} [{ty}] dist={d}: {text[:56]!r}')

# ---------------- explicit influence fractions (kinship/transmission) -------
inf_keys = {(e['from'], e['to'], e['type']) for e in claims['influence']}
for frm, to, ty in [('mary', 'jesus', 'kinship'), ('moses', 'jesus', 'transmission')]:
    if (frm, to, ty) not in inf_keys:
        claims['influence'].append({'from': frm, 'to': to, 'type': ty,
                                    'fraction': 0.0})
        print(f'+ influence 0.0 {frm}->{to} [{ty}]')

# ---------------- proposals (gate report; NOT direct) ----------------
props = claims.setdefault('proposals', {})
PROPOSALS = {
    'pontius-pilate': ('P_authority', 0.000005, 1.0, 'Prefect of Judaea',
        "Procurator in Tacitus [320] and Josephus [319], governor of Judaea in "
        "Luke 3:1 [318]; the office that passed the death sentence in all four "
        "witnesses. Small share for a small province's command.",
        [NT, JOS, TAC]),
    'tiberius': ('P_authority', 0.0002, 1.0, 'Roman emperor',
        "The princeps named by Tacitus as the reign of the execution (Ann. "
        "15.44) [320] and by Luke as the dating emperor (Luke 3:1) [318]; "
        "Josephus routes the frontier war orders through him (Ant. 18.5.1) "
        "[319]. Tier-2 ceiling share.",
        [TAC, NT, JOS]),
    'herod-antipas': ('P_authority', 0.00001, 1.0, 'Tetrarch of Galilee',
        "Tetrarch under Tiberius (Luke 3:1) [318]; Josephus documents the "
        "Baptist's killing as his security decision (Ant. 18.5.2) [319].",
        [NT, JOS]),
    'moses': ('P_authority', 0.00005, 1.0, 'Host-leader of the Exodus',
        "The Exodus commission is a host command in the witness: 'I will send "
        "thee unto Pharaoh, that thou mayest bring forth my people the "
        "children of Israel out of Egypt' (Exod. 3:10) [317]; Josephus frames "
        "him as the lawgiver [319].",
        [GE, JOS]),
}
for nid, (pool, share, wit, role, why, files) in PROPOSALS.items():
    if nid not in props:
        props[nid] = {'pool': pool, 'share': share, 'witness': wit, 'role': role,
                      'why': why, 'witness_files': files}
        print(f'+ proposal {nid} {pool} {share}')

# ---------------- write ----------------
shutil.copy(GP, GP.with_suffix('.json.bakR2'))
shutil.copy(LP, LP.with_suffix('.json.bakR2'))
json.dump(g, open(GP, 'w'), indent=2, ensure_ascii=False)
json.dump(ledger, open(LP, 'w'), indent=2, ensure_ascii=False)
json.dump(claims, open(CP, 'w'), indent=2, ensure_ascii=False)
print(f'DONE: {len(g["nodes"])} nodes, {len(g["edges"])} edges (+{added} this run)')
