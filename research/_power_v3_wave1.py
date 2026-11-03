"""power model v3 WAVE 1 (Cobe rulings 2026-10-27, third reply).

Writes v3 fields beside the frozen v2 numbers on the pilot's 14 nodes, and builds
constantine + croesus as real nodes with cards, essays, wiki and typed edges.

Rulings applied:
 1. pair reporting: headline = the largest reading; the literal reading stays in the row
 2. creative physics where defensible; magnitudes that rest on unverified physics
    (ex nihilo creation, traversable-wormhole resurrection) are RED-FLAGGED with the
    reasoning stored on the node
 3. physical ledger is componentized and complete (human, weapons, tools, resources,
    capital, finance; absent classes recorded)
 4. static holds: 0 W sustained, work reported
 5. edges carry `mode`: parasitic (draws down the source's pool, carries fractions) or
    symbiotic (mutual reinforcement, no pool draw, no fractions)
Idempotent on node id and edge (from,to,type). v2 fields untouched.
"""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import GP, LP
from _audit_relevance import alias_patterns, text_quality
from _textclean import norm_file
from _nameinfra import FILES, SQMAP, expand_span, positions

REPO = Path(__file__).resolve().parent.parent
CP = Path(__file__).resolve().parent / 'power_claims.json'
TODAY = '2026-10-27'

# strip the Wikisource stylesheet blob from freshly fetched EB1911 pages (the page's
# CSS lands in the text layer and poisons excerpt back-scans)
for _f in ('evidence/washington/eb1911-washington.txt',
           'evidence/croesus/eb1911-croesus.txt',
           'evidence/constantine/eb1911-constantine.txt'):
    _p = REPO / _f
    if _p.exists():
        _t = _p.read_text(errors='replace')
        if 'mw-parser-output' in _t:
            _t = re.sub(r'[^{}]*\{[^{}]*\}', ' ', _t)
            _m = re.search(r'\b(WASHINGTON|CONSTANTINE|CROESUS)\b', _t, re.I)
            if _m and _m.start() > 0:
                _t = _t[_m.start():]
            _t = re.sub(r'\s+', ' ', _t).strip()
            _p.write_text(_t)
            print(f'cleaned CSS from {_f} ({len(_t)} chars)')

# refresh FILES with any witness staged since import
for _p in sorted(REPO.glob('evidence/**/*.txt')) + sorted(REPO.glob('evidence/**/*.html')):
    _fp = str(_p.relative_to(REPO))
    if _fp not in FILES:
        _t = norm_file(_p.read_text(errors='replace'))
        FILES[_fp] = _t
        SQMAP[_fp] = [i for i, ch in enumerate(_t) if not ch.isspace()]

g = json.load(open(GP))
ledger = json.load(open(LP))
claims = json.load(open(CP))
nodes = {n['id']: n for n in g['nodes']}
src_by_id = {s['id']: s for s in ledger['sources']}

# ---- sources ---------------------------------------------------------------
NEW_SOURCES = [
    (325, 'https://en.wikisource.org/wiki/1911_Encyclop%C3%A6dia_Britannica/Washington,_George',
     'EB1911, Washington, George (Wikisource)'),
    (326, 'https://en.wikisource.org/wiki/1911_Encyclop%C3%A6dia_Britannica/Croesus',
     'EB1911, Croesus (Wikisource)'),
    (327, 'https://en.wikisource.org/wiki/1911_Encyclop%C3%A6dia_Britannica/Constantine_(emperors)',
     'EB1911, Constantine (emperors) (Wikisource)'),
]
for sid, url, title in NEW_SOURCES:
    if sid not in src_by_id:
        ledger['sources'].append({'id': sid, 'url': url, 'title': title,
                                  'accessed': TODAY, 'quotes': []})
        print(f'+ source [{sid}] {title}')
src_by_id = {s['id']: s for s in ledger['sources']}
def H(sid):
    s = src_by_id[sid]
    return {'source_id': sid, 'source_title': s['title'], 'source_url': s['url']}

def excerpt(fp, anchor, back=140, fwd=430, head=None):
    t = FILES.get(fp)
    if t is None or anchor is None:
        return None
    m = re.search(anchor, t, re.I)
    if not m:
        return None
    tx = expand_span(t, max(0, m.start()-back), min(len(t), m.end()+fwd), max_fwd=800)
    if head:
        hm = re.search(head, tx)
        if hm and hm.start() > 0:
            tx = tx[hm.start():].lstrip()
    return tx

def add_q(sid, text):
    s = next(x for x in ledger['sources'] if x['id'] == sid)
    if all(q['text'][:60] != text[:60] for q in s.get('quotes', [])):
        s.setdefault('quotes', []).append({'text': text, 'added': TODAY})

# ---- constants -------------------------------------------------------------
C2 = (2.998e8)**2
MC2_EARTH = 5.972e24 * C2            # creation reading (mass of the earth as narrated)
WORMHOLE_J = (2.998e8)**4 / 6.674e-11   # c^4/G x throat radius (m)
LANDAUER_HUMAN = 2.97e-21 * 1e30       # kT ln2 x ~1e30 bits (body-state information)
PLAGUE_W = 20000 * 0.2 * 100           # 20,000 stricken bodies, +20% host metabolism

# ---- v3 node ledgers -------------------------------------------------------
V3 = {
 'zeus': dict(virt=1.02e18, cls='thermal', flag=False,
   feat='theomachy: the thunderbolt war that made land and sea seethe (Theogony 693-700)',
   readings=[('1.02 EW', 'heat the Aegean 100 m layer by 1 K over a one-day battle'),
             ('33 TW', 'single bolt peak (1 GJ in 30 us)')],
   formula='2.15e11 m2 x 100 m x 1025 kg/m3 x 4000 J/kgK x 1 K = 8.8e22 J / 86400 s',
   src=(26, 'Theogony 693-700 (Evelyn-White)'),
   ex=('evidence/epimetheus/hesiod-evelynwhite-gutenberg348.txt', r'All the land seethed')),
 'god': dict(virt=MC2_EARTH/ (6*86400), cls='ex-nihilo', flag=True,
   feat='creation ex nihilo: the making of the heavens and the earth (Genesis 1)',
   readings=[('1.04e36 W', 'E = mc2 for the earth as narrated, over the six days of the account'),
             ('2.07 EW', 'the deluge (Genesis 7-8): water above the high hills over 40 days')],
   formula='5.972e24 kg x c^2 = 5.37e41 J, divided by 6 days (518,400 s). The witness supplies the duration. Creation ex nihilo has no verified process; the mc2 reading prices the mass, not the act.',
   src=(317, 'Genesis 1:1-2:4, 7:11-8:3 (KJV)'),
   ex=('evidence/god/kjv-genesis-exodus-gutenberg.txt', r'In the beginning God created')),
 'jesus': dict(virt=WORMHOLE_J, cls='wormhole', flag=True,
   feat='the resurrection (Mark 16; 1 Cor. 15)',
   readings=[('1.21e44 W', 'traversable wormhole of 1 m throat: exotic-matter requirement c^4/G x b, as a one-second act'),
             ('3.0 GJ', 'Landauer bound: kT ln2 x ~1e30 bits of body-state information'),
             ('1.67 TW', 'calming the storm (Mark 4:39), the physical act in the row')],
   formula='c^4/G = 1.21e44 J per metre of throat radius; the resurrection act read as one second. The Landauer reading prices information restoration at body temperature. Neither process is verified physics; the flag is explicit.',
   src=(318, 'Mark 16:1-8 (KJV)'),
   ex=('evidence/jesus/kjv-newtestament-gutenberg.txt', r'he is risen')),
 'thor': dict(virt=1.6e16/600, cls='kinetic', flag=False,
   feat='the world-serpent heave (Hymiskvitha) and the giant host slain (Thrymskvitha)',
   readings=[('26.7 TW', 'lifting half the serpent (5,000 km, 2 m diameter) 100 m, over a ten-minute duel'),
             ('23 kW', 'the narrated blow total: 40 kg hammer at 60 m/s, 200 blows')],
   formula='m/2 x g x 100 m = 7.7e15 J reported at 1.6e16 J for a full heave / 600 s; the literal blow row kept',
   src=(24, 'Bellows, Poetic Edda, Thrymskvitha / Hymiskvitha'),
   ex=('evidence/volundr/bellows-poetic-edda-1923-full.txt', r'Thrymskvitha')),
 'poseidon': dict(virt=1.67e12, cls='kinetic', flag=False,
   feat='the storm laid flat (Aeneid 1.125-156)',
   readings=[('1.67 TW', 'squall kinetic energy ~1e15 J dissipated in ten minutes')],
   formula='1e15 J / 600 s',
   src=(14, 'Aeneid 1.125-156 (Dryden)'),
   ex=('evidence/_corpus/virgil-aeneid-dryden.txt', r'imperial Neptune')),
 'atlas': dict(virt=0.0, cls='static', flag=False,
   feat='holds the broad heaven (Theogony 517-520)',
   readings=[('0 W', 'static hold, per ruling'), ('5.05e19 J', 'work to raise the atmosphere one metre')],
   formula='5.15e18 kg x 9.81 m/s2 x 1 m',
   src=(26, 'Theogony 517-520 (Evelyn-White)'),
   ex=('evidence/epimetheus/hesiod-evelynwhite-gutenberg348.txt', r'Atlas')),
 'prometheus': dict(virt=1e7, cls='chemical', flag=False,
   feat='theft of fire for mortals (Protagoras 321d-322a)',
   readings=[('10 MW', 'torch-scale delivery read as a one-second act'), ('10 MJ', 'the energy of the fire delivered')],
   formula='~1e7 J / 1 s; the arts catalogue is attributive, not energetic',
   src=(27, 'Protagoras 321d-322a (Jowett)'),
   ex=('evidence/prometheus/plato_protagoras_jowett.txt', r'stole')),
 'inana': dict(virt=2.6e18/86400, cls='fracture', flag=False,
   feat='the destruction of Mount Ebih (ETCSL c.1.3.2)',
   readings=[('30.1 TW', 'fragmentation of a 10 km3 mountain over one day'), ('1.05 PW', 'M8 earthquake equivalent over 60 s')],
   formula='2.6e13 kg x 1e5 J/kg = 2.6e18 J / 86400 s',
   src=(322, 'ETCSL c.1.3.2 Inana and Ebih'),
   ex=('evidence/inana/etcsl-inana-ebih-c132.html', r'Ebih')),
 'apollo': dict(virt=PLAGUE_W, cls='biological', flag=False,
   feat='the plague on the Greek camp (Iliad 1.9-52); the Python slaying (Apollodorus 1.4.1)',
   readings=[('400 kW', 'pathogen load at peak: 20,000 stricken bodies carrying a +20% host metabolic drain'),
             ('10 kW', 'the Python slaying: 100 arrows x 100 J as a one-second act')],
   formula='20,000 x 0.2 x 100 W; the archer god\'s terror is metabolic, not kinetic',
   src=(1, 'Iliad 1.9-52 (Butler)'),
   ex=('evidence/epimetheus/apollodorus1-frazer-theoi.html', r'the snake Python')),
 'heracles': dict(virt=5.1e12/86400, cls='potential', flag=False,
   feat='diverts the Alpheus and Peneus to cleanse the Augean yard (Apollodorus 2.5.5)',
   readings=[('59 MW', '60 m3/s at 100 m head over one day'), ('5.2e12 J', 'total work of the diversion')],
   formula='1025 kg/m3 x 60 m3/s x 9.81 x 100 m',
   src=(28, 'Apollodorus 2.5.5 (Frazer)'),
   ex=('evidence/heracles/apollodorus2-frazer-theoi.html', r'diverting the courses')),
 'washington': dict(virt=0.0, cls='none', flag=False,
   feat='none attested with a physical class: the hatchet and the thrown dollar carry no energy',
   readings=[('0 W', 'no computable feat: mythic accretion on flesh figures is energetically trivial')],
   formula='the hatchet anecdote is a moral story',
   src=(15, 'Weems, Life of Washington'),
   ex=('evidence/washington/weems_life_of_washington_archive_org_1800_djvu.txt', r'hatchet'),
   phys=[dict(cls='human', w=3000*15e3, basis='in-witness low: "Washington had not 3000 men" x 15 kW',
              src=(15, 'Weems, Life of Washington', 'evidence/washington/weems_life_of_washington_archive_org_1800_djvu.txt',
                   r'had not 3000 men')),
         dict(cls='resources', w=3237*300, basis='Mount Vernon ~8,000 acres x 0.3 kW/ha',
              src=(15, 'Weems, Life of Washington', 'evidence/washington/weems_life_of_washington_archive_org_1800_djvu.txt', r'Mount Vernon')),
         dict(cls='weapons', w=0.0, basis='musket flintlock ~150 W delivered per man, reported inside the human+supply coefficient; EB1911 Washington now on disk for the peak-command figure',
              src=(325, 'EB1911, Washington, George', 'evidence/washington/eb1911-washington.txt', r'commander-in-chief'))],
   absent=['finance: no treasury figure in-witness'],
   gaps=['peak field command (Yorktown) to be sliced from EB1911 Washington']),
 'sulla': dict(virt=0.0, cls='none', flag=False,
   feat='none attested: the epithet Felix claims fortune, not an act',
   readings=[('0 W', 'no feat in the witnesses')], formula='n/a',
   src=(61, 'Plutarch, Sulla'), ex=None,
   phys=[dict(cls='human', w=40000*15e3, basis='~6 legions + auxiliaries x 15 kW',
              src=(61, 'Plutarch, Sulla', 'evidence/_corpus/plutarch-lives-dryden-clough-gutenberg.txt', r'legions'))],
   absent=['weapons: gladius and pilum inside the coefficient'],
   gaps=['legion count to be pinned to the Plutarch passage', 'proscription proceeds not yet quantified']),
 'constantine': dict(virt=0.0, cls='none', flag=False,
   feat='none attested as an act: the Milvian vision carries no energy claim',
   readings=[('0 W', 'no feat in the witnesses')], formula='n/a',
   src=(327, 'EB1911, Constantine'), ex=None,
   phys=[dict(cls='human', w=600000*15e3, basis='Gibbon: the military establishment computed at 583,000-645,000 men; 600,000 x 15 kW',
              src=(324, 'Gibbon, Decline and Fall vol 2', 'evidence/constantine/gibbon-decline-fall-vol2-pg732.txt', r'complete force of the military establishment')),
         dict(cls='resources', w=95.2e6, basis="Rome's annona ~200,000 t grain/yr x 15 MJ/kg",
              src=(324, 'Gibbon, Decline and Fall vol 2', 'evidence/constantine/gibbon-decline-fall-vol2-pg732.txt', r'annona|grain')),
         dict(cls='weapons', w=0.0, basis='legionary kit inside the human+supply coefficient; the fiscal endowment line is the transfer row, not a command row',
              src=(327, 'EB1911, Constantine', 'evidence/constantine/eb1911-constantine.txt', r'army'))],
   absent=['finance: the imperial revenue total is not in the fetched witnesses'],
   gaps=['church-endowment share of the fisc (transfer fraction, Cobe to rule)']),
 'croesus': dict(virt=0.0, cls='none', flag=False,
   feat='none attested as an act; the documented power is the dedications and the alliances',
   readings=[('0 W', 'no feat in the witnesses')], formula='n/a',
   src=(326, 'EB1911, Croesus'), ex=None,
   phys=[dict(cls='human', w=20000*15e3, basis='Lydian host order of magnitude, pending a witness number x 15 kW',
              src=(323, 'Herodotus', 'evidence/croesus/herodotus-macaulay-pg2707.txt', r'Croesus')),
         dict(cls='finance', w=0.0, basis='Delphic dedications (117 ingots at ~2 talents, the golden lion, six bowls) and the alliance subsidies to Greek states whose fleets supplemented his army',
              src=(326, 'EB1911, Croesus', 'evidence/croesus/eb1911-croesus.txt', r'securing alliances with the Greek states'))],
   absent=['weapons inside the coefficient', 'mint output not quantified'],
   gaps=['host size: no clean figure in Herodotus or EB1911']),
}

# ---- the two demo nodes, built in full -------------------------------------
NEW_NODE_SPECS = [
 dict(id='constantine', label='Constantine', tradition='Roman emperor, flesh record',
      era=306,
      essay=("The army made him first: 'on the 25th of July 306, the army acclaimed his son "
             "as Augustus' (EB1911) [327], and the establishment he inherited ran to "
             "'six hundred and forty-five thousand' men in Gibbon's accounting [324]. "
             "The Christian turn is documented in the same witnesses: the edict of Milan "
             "returned the churches their property, and the fisc paid for the basilicas. "
             "The imperial revenues that followed the conversion are the real power that "
             "reaches the graph's God node, and the machinery of the state, not the vision, "
             "is what carried it."),
      cards=[('evidence/constantine/eb1911-constantine.txt', r"the army acclaimed his son as Augustus", 327, None),
             ('evidence/constantine/gibbon-decline-fall-vol2-pg732.txt', r"complete force of the military establishment", 324, None),
             ('evidence/constantine/eb1911-constantine.txt', r"edict of Milan|Milan", 327, None)],
      note=("Era 306: accession acclaimed by the army (EB1911). Physical ledger: army 600,000 "
            "x 15 kW = 9.0 GW + annona 95 MW; the state's power is the largest real command in "
            "the graph. Transfers real power to God (endowments, mode parasitic). "
            "Pricing proposal filed; unpriced pending the gate.")),
 dict(id='croesus', label='Croesus', tradition='Lydian king, flesh record', era=-560,
      essay=("His wealth was the instrument: 'His wealth, due to trade, was proverbial, and he "
             "used part of it in securing alliances with the Greek states whose fleets might "
             "supplement his own army' (EB1911) [326]. The dedications to Delphi are the oldest "
             "large documented transfer of real capital to a sanctuary: 'their number was one "
             "hundred and seventeen', with four of pure gold 'weighing two talents and a half "
             "each' (Herodotus 1.50-51) [323]. The wealth bought oracles and allies, and the "
             "oracle answered: the empire ended at the Halys."),
      cards=[('evidence/croesus/eb1911-croesus.txt', r"CROESUS, last king of Lydia", 326, None),
             ('evidence/croesus/herodotus-macaulay-pg2707.txt', r"one hundred and seventeen", 323, None),
             ('evidence/croesus/eb1911-croesus.txt', r"Delphic oracles Croesus marched", 326, None)],
      note=("Era -560: reign dated to the mid-sixth century; EB1911 and Herodotus are the "
            "witnesses. Physical ledger: host (order of magnitude, flagged) + finance rows "
            "(dedications, alliance subsidies). Transfers real capital to Apollo (mode "
            "parasitic). Pricing proposal filed; unpriced pending the gate.")),
]
for spec in NEW_NODE_SPECS:
    node = nodes.get(spec['id'])
    if node is None:
        g['nodes'].append({'id': spec['id'], 'label': spec['label'],
                           'tradition': spec['tradition'], 'batch': None,
                           'date_added': TODAY, 'era': spec['era'],
                           'review': {'status': 'auto-added', 'date': TODAY},
                           'notes': [{'date': TODAY, 'text': spec['note']}]})
        node = g['nodes'][-1]
        nodes[spec['id']] = node
        print(f"+ node {spec['id']}")
    if not node.get('essay'):
        node['essay'] = spec['essay']
        print(f"+ essay {spec['id']}")
    if not node.get('highlights'):
        cards = []
        for fp, anc, sid, head in spec['cards']:
            t = excerpt(fp, anc, head=head)
            if not t:
                print(f'!! card anchor failed: {spec["id"]} {anc!r}')
                continue
            add_q(sid, t)
            cards.append({'text': t, 'direct': True, 'manual': True, **H(sid)})
        if cards:
            node['highlights'] = cards
            print(f"+ {len(cards)} cards {spec['id']}: first={cards[0]['text'][:60]!r}")

IDMAP = {'washington': 'george-washington'}
for nid, v in V3.items():
    node = nodes.get(IDMAP.get(nid, nid))
    if node is None:
        print(f'!! pilot node missing from graph: {nid}')
        continue
    nid = IDMAP.get(nid, nid)
    node['v3'] = {
        'virt_watts': v['virt'], 'virt_class': v['cls'], 'beyond_physics': v['flag'],
        'virt_feat': v['feat'], 'virt_readings': v['readings'],
        'virt_formula': v['formula'], 'virt_locator': v['src'][1],
        'virt_source_id': v['src'][0], 'ruled': TODAY,
    }
    ex = excerpt(*v['ex']) if v.get('ex') else None
    if ex:
        node['v3']['virt_excerpt'] = ex
        add_q(v['src'][0], ex)
    elif v.get('ex'):
        print(f'!! virt excerpt failed: {nid}')
    if v.get('phys'):
        comps = []
        for c in v['phys']:
            e = excerpt(*c['src'][2:4]) if c['src'][2] else None
            if c['src'][2] and not e:
                print(f'!! phys excerpt failed: {nid} {c["cls"]} {c["src"][3]!r}')
            comps.append({'cls': c['cls'], 'w': c['w'], 'basis': c['basis'],
                          'source_id': c['src'][0], 'source_title': c['src'][1],
                          'excerpt': e})
            if e:
                add_q(c['src'][0], e)
        node['v3']['phys_watts'] = sum(c['w'] for c in comps)
        node['v3']['phys_components'] = comps
        node['v3']['phys_absent'] = v.get('absent', [])
        node['v3']['phys_gaps'] = v.get('gaps', [])
    else:
        node['v3']['phys_watts'] = None
        node['v3']['phys_components'] = []
        node['v3']['phys_absent'] = ['all classes: no documented command (a spirit of the myths)']
        node['v3']['phys_gaps'] = []
    print(f"v3 {nid:12s} virt={v['virt']:.3g} flag={v['flag']} phys={node['v3']['phys_watts']}")

# ---- typed edges (parasitic carries fractions; symbiotic does not) ---------
NEW_EDGES = [
 dict(frm='constantine', to='god', ty='transmission', mode='parasitic',
      phys_frac=0.03, virt_frac=0.0,
      title='The fisc endows the church', sid=324, era=313,
      anchor=('evidence/constantine/gibbon-decline-fall-vol2-pg732.txt', r"the God of the Christians",
              'The son of Constantius immediately suspended', 'constantine', 'god'),
      note='Endowments, exemptions and enforcement drawn from the imperial fisc; the share is Cobe\'s to rule.'),
 dict(frm='croesus', to='apollo', ty='transmission', mode='parasitic',
      phys_frac=0.10, virt_frac=0.0,
      title='The dedications at Delphi', sid=323, era=-550,
      anchor=('evidence/croesus/herodotus-macaulay-pg2707.txt', r"buying gold there with purpose of using it",
              'Thus did Croesus announce to the Lacedemonians', 'croesus', 'apollo'),
      note='Real capital transferred to the sanctuary (Herodotus 1.50-51); the share is Cobe\'s to rule.'),
]
PAT = {n['id']: alias_patterns(n) for n in g['nodes']}

def _hits(fp, pats):
    """alias positions in RAW text coordinates (positions() is length-preserving)."""
    return [i for i, _a in positions(FILES[fp], SQMAP[fp], pats)]

def best_pair(fp, a, b, window=600):
    """tightest both-name co-occurrence in one file, sentence-bounded (audit's measure)."""
    t = FILES.get(fp)
    if t is None:
        return None
    A, B = _hits(fp, PAT[a]), _hits(fp, PAT[b])
    cands = []
    for i in A:
        for j in B:
            d = abs(i - j)
            if d <= window:
                cands.append((d, i, j))
    cands.sort()
    for d, i, j in cands[:8]:
        for back, fwd in ((60, 260), (30, 200), (0, 160)):
            tx = expand_span(t, max(0, min(i, j) - back), max(i, j) + fwd, max_fwd=700)
            seg, junk = text_quality(tx)
            if both_names(tx, a, b) and not seg and not junk:
                return tx
    return None
def both_names(text, a, b):
    def hit(pats):
        tc = ' ' + re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip() + ' '
        return any(p['na'] in tc for p in pats)
    return hit(PAT[a]) and hit(PAT[b])
has_edge = lambda f, t, ty: any(e['from'] == f and e['to'] == t and e['type'] == ty for e in g['edges'])
for spec in NEW_EDGES:
    if has_edge(spec['frm'], spec['to'], spec['ty']):
        print(f"  skip edge {spec['frm']}->{spec['to']}")
    else:
        fp, anc, head, a, b = spec['anchor']
        t = excerpt(fp, anc, back=320, fwd=520, head=head)
        if not t or not both_names(t, a, b):
            t2 = best_pair(fp, a, b)
            t = t2 if (t2 and both_names(t2, a, b)) else None
        if not t:
            print(f"!! edge excerpt failed both-name gate: {spec['frm']}->{spec['to']}")
            continue
        add_q(spec['sid'], t)
        g['edges'].append({'from': spec['frm'], 'to': spec['to'], 'type': spec['ty'],
                           'title': spec['title'], 'mode': spec['mode'],
                           'phys_frac': spec['phys_frac'], 'virt_frac': spec['virt_frac'],
                           'source': f"[{spec['sid']}] {src_by_id[spec['sid']]['title']}",
                           'essay': None, 'date_added': TODAY, 'era': spec['era'],
                           'influence': 0.0,
                           'review': {'status': 'auto-added', 'date': TODAY},
                           'excerpts': [{'text': t, **H(spec['sid'])}],
                           'pairing_note': spec['note']})
        print(f"+ edge {spec['frm']}->{spec['to']} [{spec['mode']}] phys_frac={spec['phys_frac']}")

# mode normalization: parasitic where a fraction exists, symbiotic otherwise
changed = 0
for e in g['edges']:
    frac = (e.get('phys_frac') or 0) + (e.get('virt_frac') or 0)
    want = 'parasitic' if frac > 0 else 'symbiotic'
    if e.get('mode') != want:
        e['mode'] = want
        changed += 1
print(f'mode normalization: {changed} edges stamped')

# influence 0.0 for the new edges (v2 layer stays clean); proposals for both nodes
inf_keys = {(e['from'], e['to'], e['type']) for e in claims['influence']}
for spec in NEW_EDGES:
    key = (spec['frm'], spec['to'], spec['ty'])
    if key not in inf_keys:
        claims['influence'].append({'from': spec['frm'], 'to': spec['to'],
                                    'type': spec['ty'], 'fraction': 0.0})
print('influence entries ensured for new edges')
props = claims.setdefault('proposals', {})
if 'constantine' not in props:
    props['constantine'] = {
        'pool': 'P_authority', 'share': 0.0002, 'witness': 1.0,
        'role': 'Roman emperor',
        'why': ('The state whose army ran to 600,000 men (Gibbon [324]) and whose fisc funded '
                'the church; the largest documented real command in the graph. Share at the '
                'Tier-2 ceiling; rescale by ruling.'),
        'witness_files': ['evidence/constantine/gibbon-decline-fall-vol2-pg732.txt',
                          'evidence/constantine/eb1911-constantine.txt']}
    print('+ proposal constantine P_authority 0.0002')
if 'croesus' not in props:
    props['croesus'] = {
        'pool': 'P_authority', 'share': 0.00002, 'witness': 1.0,
        'role': 'Lydian king',
        'why': ('Proverbial wealth deployed as alliance subsidies and sanctuary dedications '
                '(EB1911 [326]; Herodotus 1.50-51 [323]); a regional kingdom, so a small share.'),
        'witness_files': ['evidence/croesus/eb1911-croesus.txt',
                          'evidence/croesus/herodotus-macaulay-pg2707.txt']}
    print('+ proposal croesus P_authority 0.00002')

shutil.copy(GP, GP.with_suffix('.json.bakV3'))
shutil.copy(LP, LP.with_suffix('.json.bakV3'))
json.dump(g, open(GP, 'w'), indent=2, ensure_ascii=False)
json.dump(ledger, open(LP, 'w'), indent=2, ensure_ascii=False)
json.dump(claims, open(CP, 'w'), indent=2, ensure_ascii=False)
v3n = sum(1 for n in g['nodes'] if 'v3' in n)
print(f'DONE: {len(g["nodes"])} nodes ({v3n} with v3 ledgers), {len(g["edges"])} edges')
