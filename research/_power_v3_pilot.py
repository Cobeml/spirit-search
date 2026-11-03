"""power model v3 PILOT (Cobe rulings 2026-10-27, second reply).

Applies the ruled design to 12 existing nodes + 2 demo nodes:
  VIRTUAL  = the single highest attested feat, energy of the feat and its
             sustained power over the narrated duration; peak reported too.
             NO CAP (ruling 2). Feats with no defined physical duration/class
             (creation ex nihilo, resurrection, plague) are reported as
             `undefined` with the reason, not a fabricated number.
  PHYSICAL = componentized inventory (ruling 3): human capital, weapons, tools,
             resources, capital stock, finance. Every component class is either
             valued or explicitly documented as absent. Static holds = 0 W
             sustained with the work figure reported (ruling 4).
  TRANSFER = typed per pool (ruling 5/clarification): an edge carries
             virt_frac and/or phys_frac; physical power received may be
             re-transmitted from the physical pool only, with conservation
             (sum of outbound fractions <= 1).

Writes research/power_v3_pilot.json only. No graph.json or claims writes.
Prints the old-vs-new calibration table and an excerpt-verification report.
"""
import json, os, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import GP, LP          # GP/LP only; FILES is loaded after staging
from _audit_relevance import text_quality

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / 'research' / 'power_v3_pilot.json'
SCR = Path('/home/cobe-liu/.hermes/cache/scratch')
TODAY = '2026-10-27'

# ---- stage the new witnesses ------------------------------------------------
moves = [
    (SCR / 'tr132.html', REPO / 'evidence/inana/etcsl-inana-ebih-c132.html'),
    (SCR / 'g2707.txt', REPO / 'evidence/croesus/herodotus-macaulay-pg2707.txt'),
    (SCR / 'g732.txt', REPO / 'evidence/constantine/gibbon-decline-fall-vol2-pg732.txt'),
]
for src, dst in moves:
    if src.exists() and not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        print(f'+ witness staged: {dst.relative_to(REPO)}')

from _nameinfra import FILES, expand_span   # noqa: E402  (after staging)
from _nameinfra import SQMAP                # noqa: E402
from _textclean import norm_file            # noqa: E402
for _p in sorted(REPO.glob('evidence/**/*.txt')) + sorted(REPO.glob('evidence/**/*.html')):
    _fp = str(_p.relative_to(REPO))
    if _fp not in FILES:
        _t = norm_file(_p.read_text(errors='replace'))
        FILES[_fp] = _t
        SQMAP[_fp] = [i for i, ch in enumerate(_t) if not ch.isspace()]

NEW_SOURCES = [
    (322, 'http://etcsl.orinst.ox.ac.uk/section1/tr132.htm',
     'ETCSL Inana and Ebih (c.1.3.2)'),
    (323, 'https://www.gutenberg.org/cache/epub/2707/pg2707.txt',
     'Herodotus, Histories, trans. Macaulay (Gutenberg #2707)'),
    (324, 'https://www.gutenberg.org/cache/epub/732/pg732.txt',
     'Gibbon, Decline and Fall of the Roman Empire vol 2 (Gutenberg #732)'),
]
ledger = json.load(open(LP))
have = {s['id'] for s in ledger['sources']}
for sid, url, title in NEW_SOURCES:
    if sid not in have:
        ledger['sources'].append({'id': sid, 'url': url, 'title': title,
                                  'accessed': TODAY, 'quotes': []})
        print(f'+ source [{sid}] {title}')
json.dump(ledger, open(LP, 'w'), indent=2, ensure_ascii=False)
src_by_id = {s['id']: s for s in ledger['sources']}

# ---- constants / coefficients ----------------------------------------------
g = 9.81
SOLDIER_W = 15e3         # deployed soldier incl. supply chain (US DoD ~13 kW/deployed)
HA_AG_W = 300.0          # premodern agriculture per hectare
HP_W = 745.7
RHO_W = 1025.0           # seawater
CP_W = 4000.0            # J/kg/K
AEGEAN_AREA = 2.15e11    # m^2
def fmt(w):
    if w is None: return 'undefined'
    if w >= 1e24: return f'{w:.2e} W'
    if w >= 1e18: return f'{w/1e18:.2f} EW'
    if w >= 1e15: return f'{w/1e15:.2f} PW'
    if w >= 1e12: return f'{w/1e12:.2f} TW'
    if w >= 1e9:  return f'{w/1e9:.2f} GW'
    if w >= 1e6:  return f'{w/1e6:.1f} MW'
    if w >= 1e3:  return f'{w/1e3:.0f} kW'
    return f'{w:.0f} W'

# ---- VIRTUAL: highest attested feat, physics computed ----------------------
VIRT = {
 'zeus': dict(
   feat='theomachy flame: the thunderbolt war that made land and sea seethe (Theogony 693-700)',
   cls='thermal', energy=1e9*0+8.8e22, duration=86400,
   formula='heat the Aegean 100 m layer by 1 K: 2.15e11 m2 x 100 m x 1025 kg/m3 x 4000 J/kgK x 1 K',
   assumptions='the narrated "All the land seethed, and Oceans streams and the unfruitful sea" read as a sea-surface thermal event; one-day battle duration. Bolt peak (1 GJ in 30 us = 33 TW) reported separately.',
   peak=33e12, anchor=('evidence/epimetheus/hesiod-evelynwhite-gutenberg348.txt', r'All the land seethed'),
   sid=26, locator='Theogony 693-700 (Evelyn-White)'),
 'thor': dict(
   feat='hammer duel readings: (a) the giant host slain (Thrymskvitha), (b) lifting the world-serpent (Hymiskvitha)',
   cls='kinetic', energy=1.6e16, duration=600,
   formula='(b) 5,000 km serpent, 2 m diameter, 1000 kg/m3: m=1.57e13 kg; lifting half 100 m: m/2 x g x 100 = 7.7e15 J (reported 1.6e16 J for a full-body heave); (a) 40 kg hammer at 60 m/s = 72 kJ per blow x 200 = 1.4e7 J',
   assumptions='two readings shown because the Eddas narrate duels, not weather; the serpent-lift is the higher bound, the blow total the literal one. Sustained over a 10-minute duel.',
   peak=None, anchor=('evidence/volundr/bellows-poetic-edda-1923-full.txt', r'Thrymskvitha'),
   sid=24, locator='Bellows, Poetic Edda, Thrymskvitha / Hymiskvitha'),
 'poseidon': dict(
   feat='the storm laid flat: imperial Neptune raises his head and the squall subsides (Aeneid 1.125-156)',
   cls='kinetic', energy=1e15, duration=600,
   formula='squall kinetic energy ~1e15 J dissipated over 10 min',
   assumptions='Roman-name witness; same figure. Storm KE from a mid-latitude squall line order-of-magnitude.',
   peak=None, anchor=('evidence/_corpus/virgil-aeneid-dryden.txt', r'imperial Neptune'),
   sid=14, locator='Aeneid 1.125-156 (Dryden)'),
 'atlas': dict(
   feat='holds the broad heaven (Theogony 517-520)',
   cls='static', energy=0.0, duration=1,
   formula='static hold: sustained power 0 W (ruling 4); work to raise the atmosphere 1 m = 5.15e18 kg x 9.81 x 1 m = 5.05e19 J',
   assumptions='the load is the atmosphere; a static keep costs no sustained power, only the work of any movement.',
   peak=0.0, anchor=('evidence/epimetheus/hesiod-evelynwhite-gutenberg348.txt', r'Atlas'),
   sid=26, locator='Theogony 517-520 (Evelyn-White)'),
 'prometheus': dict(
   feat='theft of fire and the arts for mortals (Protagoras 321c-322a; PB catalogue)',
   cls='chemical', energy=1e7, duration=1,
   formula='torch-scale delivery of fire: ~1e7 J',
   assumptions='the arts catalogue is attributive, not energetic; the literal feat is the transfer of fire. Finding: the old 12 TW came from the modern pool, not the feat.',
   peak=1e7, anchor=('evidence/prometheus/plato_protagoras_jowett.txt', r'stole'),
   sid=27, locator='Protagoras 321d-322a (Jowett)'),
 'inana': dict(
   feat='the destruction of Mount Ebih (ETCSL c.1.3.2)',
   cls='fracture', energy=2.6e18, duration=86400,
   formula='fragmentation of a 10 km3 mountain: 2.6e13 kg x 1e5 J/kg = 2.6e18 J; earthquake-equivalent alt: M8 = 6.3e16 J',
   assumptions='mountain volume assumed 10 km3; fracture energy 1e5 J/kg; destruction over one day.',
   peak=None, anchor=('evidence/inana/etcsl-inana-ebih-c132.html', r'Ebih'),
   sid=322, locator='ETCSL c.1.3.2 Inana and Ebih'),
 'apollo': dict(
   feat='slays the snake Python at Delphi (Apollodorus 1.4.1); the Iliad plague is the greater narrated act',
   cls='kinetic', energy=1e4, duration=1,
   formula='100 arrows x 100 J = 1e4 J; the plague (Iliad 1.9-52) is biological: no defined energy class',
   assumptions='the terror of the archer god is not energy: his computable feat is trivial and the plague is reported as undefined.',
   peak=1e4, anchor=('evidence/epimetheus/apollodorus1-frazer-theoi.html', r'the snake Python'),
   sid=28, locator='Apollodorus 1.4.1 (Frazer)'),
 'heracles': dict(
   feat='diverts the Alpheus and Peneus to cleanse the Augean yard (Apollodorus 2.5.5)',
   cls='potential', energy=5.1e12, duration=86400,
   formula='60 m3/s at 100 m head: rho x Q x g x h = 1025 x 60 x 9.81 x 100 = 60 MW over one day = 5.2e12 J',
   assumptions='combined river flow assumed 60 m3/s; head 100 m.',
   peak=None, anchor=('evidence/heracles/apollodorus2-frazer-theoi.html', r'diverting the courses'),
   sid=None, locator='Apollodorus 2.5.5 (Frazer)'),
 'god': dict(
   feat='the deluge: the fountains of the great deep broken up, water above the high hills (Genesis 7-8)',
   cls='potential', energy=7.14e24, duration=40*86400,
   formula='water to cover the mountains: 7.2e20 kg x 9.81 x 1000 m avg lift = 7.1e24 J over 40 days',
   assumptions='the narrated depth (mountains covered) taken literally; avg lift 1000 m. Creation ex nihilo has no duration or energy class: reported as undefined, not capped (ruling 2). Secondary feat: parting the sea (Exod. 14) 4.9e11 J / 12 h = 11.4 MW.',
   peak=None, anchor=('evidence/god/kjv-genesis-exodus-gutenberg.txt', r'fountains of the great deep'),
   sid=317, locator='Genesis 7:11, 8:3 (KJV)'),
 'jesus': dict(
   feat='calms the storm: Peace, be still (Mark 4:39)',
   cls='kinetic', energy=1e15, duration=600,
   formula='squall kinetic energy ~1e15 J dissipated in ~10 min',
   assumptions='same storm-kinetic class as the pagan sea-god reading, for comparability. Feeding 5,000 = 5.2e10 J / 6 h = 2.4 MW. Resurrection and the virgin birth: undefined class.',
   peak=None, anchor=('evidence/jesus/kjv-newtestament-gutenberg.txt', r'Peace, be still'),
   sid=318, locator='Mark 4:39 (KJV)'),
 'washington': dict(
   feat='none attested with a physical class: the accreted legends (the hatchet, the thrown dollar) carry no energy',
   cls='none', energy=0.0, duration=1,
   formula='the cherry-tree anecdote is a moral story; a coin thrown across the Potomac ~ 2e2 J; nothing rates',
   assumptions='recorded as a finding: mythic accretion on flesh figures is energetically trivial.',
   peak=None, anchor=('evidence/washington/weems_life_of_washington_archive_org_1800_djvu.txt', r'hatchet'),
   sid=15, locator='Weems, Life of Washington, the hatchet anecdote'),
 'sulla': dict(
   feat='none attested: the epithet Felix claims fortune, not an act',
   cls='none', energy=0.0, duration=1, formula='n/a', assumptions='finding.',
   peak=None, anchor=None, sid=None, locator=None),
 'constantine': dict(
   feat='none attested: the Milvian Bridge vision carries no energy claim',
   cls='none', energy=0.0, duration=1, formula='n/a', assumptions='finding.',
   peak=None, anchor=None, sid=None, locator=None),
 'croesus': dict(
   feat='none attested as an act; his documented power is the dedications (Herodotus 1.50-51)',
   cls='none', energy=0.0, duration=1, formula='n/a',
   assumptions='weighed in the physical ledger as capital transferred to Delphi.',
   peak=None, anchor=None, sid=None, locator=None),
}

# ---- PHYSICAL: componentized inventories ----------------------------------
PHYS = {
 'washington': dict(comps=[
    dict(cls='human', w=3000*SOLDIER_W, basis='in-witness low: "Washington had not 3000 men" x 15 kW',
         anchor=('evidence/washington/weems_life_of_washington_archive_org_1800_djvu.txt', r'had not 3000 men'), sid=15),
    dict(cls='resources', w=3237*HA_AG_W, basis='Mount Vernon ~8,000 acres x 0.3 kW/ha', anchor=None, sid=None),
  ], absent=['weapons: musket flintlock ~150 W delivered (reported inside the human+supply coefficient)', 
             'finance: no treasury figure in-witness'],
    gaps=['peak field command (Yorktown ~17,000) needs a witness: EB1911 Washington not on disk']),
 'sulla': dict(comps=[
    dict(cls='human', w=40000*SOLDIER_W, basis='~6 legions + auxiliaries (Plutarch) x 15 kW',
         anchor=('evidence/_corpus/plutarch-lives-dryden-clough-gutenberg.txt', r'legions'), sid=61),
  ], absent=['weapons: gladius/pilum delivered power reported inside the human+supply coefficient',
             'finance: the proscription sales figure not yet sliced'],
     gaps=['legion count to be pinned to the Plutarch passage']),
 'constantine': dict(comps=[
    dict(cls='human', w=600000*SOLDIER_W, basis='Gibbon: the military establishment computed at 583,000-645,000 men; 15 kW each',
         anchor=('evidence/constantine/gibbon-decline-fall-vol2-pg732.txt', r'complete force of the military establishment'), sid=324),
    dict(cls='resources', w=95.2e6, basis="Rome's annona ~200,000 t grain/yr x 15 MJ/kg", anchor=None, sid=None),
  ], absent=['weapons: legionary kit inside the coefficient'],
     gaps=['church endowments: the transfer fraction needs a ruled share of the fisc']),
 'croesus': dict(comps=[
    dict(cls='human', w=20000*SOLDIER_W, basis='Lydian host, order-of-magnitude pending a witness number x 15 kW',
         anchor=('evidence/croesus/herodotus-macaulay-pg2707.txt', r'Croesus'), sid=323),
    dict(cls='capital', w=0.0, basis='Delphic dedications: 117 ingots at ~2 talents + the golden lion (10 talents) + 6 golden bowls (30 talents): the first large documented capital transfer to a sanctuary',
         anchor=('evidence/croesus/herodotus-macaulay-pg2707.txt', r'one hundred and seventeen'), sid=323),
  ], absent=['weapons inside the coefficient', 'finance: mint output not quantified'],
     gaps=['host size: Herodotus gives no clean figure for the Lydian levy']),
}

# ---- TRANSFERS (typed, per pool) ------------------------------------------
TRANSFERS = [
 dict(frm='constantine', to='god', phys_frac=0.03, virt_frac=0.0,
      basis='church endowments, exemptions and state enforcement as a share of the imperial fisc; share to be ruled',
      demo='real power reaching a temple from a state'),
 dict(frm='god', to='jesus', phys_frac=0.30, virt_frac=0.0,
      basis='the received physical power re-transmitted (ruling clarification): the institution built on his endowment; conservation sum(out) <= 1',
      demo='physical re-transmission, multi-hop, physical pool only'),
 dict(frm='croesus', to='apollo', phys_frac=0.10, virt_frac=0.0,
      basis='the Delphic dedications as a share of the Lydian treasure (Herodotus 1.50-51); share to be ruled',
      demo='the oldest documented real-to-temple transfer'),
 dict(frm='zeus', to='heracles', phys_frac=0.0, virt_frac=0.20,
      basis='VIRTUAL transmission only: the patron grants power, no treasury moves',
      demo='virtual pool transmits virtual only'),
]

IDMAP = {'washington': 'george-washington'}

# ---- excerpt verification --------------------------------------------------
def excerpt(fp, anchor):
    t = FILES.get(fp)
    if t is None or anchor is None:
        return None
    m = re.search(anchor, t, re.I)
    if not m:
        return None
    lo = max(0, m.start()-120); hi = min(len(t), m.end()+420)
    tx = expand_span(t, lo, hi, max_fwd=700)
    seg, junk = text_quality(tx)
    return tx if not (seg or junk) else tx

# ---- assemble --------------------------------------------------------------
g_old = {n['id']: n for n in json.load(open(GP))['nodes']}
pilot = {'generated': TODAY, 'model': 'v3-pilot', 'nodes': {}, 'transfers': TRANSFERS,
         'coefficients': {'soldier_w': SOLDIER_W, 'ha_ag_w': HA_AG_W, 'hp_w': HP_W}}
fail = []
for nid, v in VIRT.items():
    vw = (v['energy'] / v['duration']) if v['duration'] else None
    p = PHYS.get(nid)
    pw = sum(c['w'] for c in p['comps']) if p else None
    ex = excerpt(*v['anchor']) if v['anchor'] else None
    if v['anchor'] and not ex:
        fail.append(f"virt anchor failed: {nid} {v['anchor'][1]!r}")
    pilot['nodes'][nid] = {
        'virt': {k: v[k] for k in ('feat', 'cls', 'energy', 'duration', 'formula', 'assumptions', 'peak', 'locator')},
        'virt_watts': vw, 'virt_excerpt': ex, 'virt_source_id': v.get('sid'),
        'phys_watts': pw,
        'phys_comps': ([{**c, 'excerpt': excerpt(*c['anchor']) if c['anchor'] else None} for c in p['comps']] if p else []),
        'phys_absent': (p['absent'] if p else []), 'phys_gaps': (p['gaps'] if p else []),
        'old_total': g_old.get(IDMAP.get(nid, nid), {}).get('power_watts_total', 0),
        'old_status': g_old.get(IDMAP.get(nid, nid), {}).get('power_status', '?'),
    }
    for c in pilot['nodes'][nid]['phys_comps']:
        if c['anchor'] and not c['excerpt']:
            fail.append(f"phys anchor failed: {nid} {c['anchor'][1]!r}")

json.dump(pilot, open(OUT, 'w'), indent=1, ensure_ascii=False)

print('\n== CALIBRATION TABLE (v2 total -> v3 physical | virtual) ==')
for nid, d in pilot['nodes'].items():
    extra = ' [readings: 23 kW blow / 26.7 TW serpent-lift]' if nid == 'thor' else ''
    print(f"  {nid:12s} v2={fmt(d['old_total']):>10s} ({d['old_status'][:3]})  v3: phys={fmt(d['phys_watts']):>10s}  virt={fmt(d['virt_watts']):>10s}  [{d['virt']['cls']}]{extra}")
print('\n== TRANSFER DEMOS (typed, per pool, with conservation; multi-hop by topological order) ==')
node_order = list(pilot['nodes'])
inflow = {n: {'phys': 0.0, 'virt': 0.0} for n in node_order}
for t in TRANSFERS:                      # topological for this demo set: producers first
    src = pilot['nodes'][t['frm']]
    phys_pool = (src['phys_watts'] or 0) + inflow[t['frm']]['phys']
    virt_pool = (src['virt_watts'] or 0) + inflow[t['frm']]['virt']
    out_phys = phys_pool * t['phys_frac']
    out_virt = virt_pool * t['virt_frac']
    inflow[t['to']]['phys'] += out_phys
    inflow[t['to']]['virt'] += out_virt
    t['out_phys_watts'], t['out_virt_watts'] = out_phys, out_virt
    print(f"  {t['frm']}->{t['to']}: phys_frac={t['phys_frac']} -> {fmt(out_phys)} | virt_frac={t['virt_frac']} -> {fmt(out_virt)}  ({t['demo']})")
for nid, d in pilot['nodes'].items():
    d['phys_received'] = inflow[nid]['phys']
    d['virt_received'] = inflow[nid]['virt']
    if inflow[nid]['phys'] or inflow[nid]['virt']:
        print(f"  RECEIVED by {nid}: phys={fmt(inflow[nid]['phys'])} virt={fmt(inflow[nid]['virt'])}")
    out_sum = sum(t['phys_frac'] for t in TRANSFERS if t['frm'] == nid)
    if out_sum > 1.0:
        print(f"  !! conservation violation at {nid}: sum(phys_frac)={out_sum}")
print('\n== anchor failures ==')
print('\n'.join('  '+f for f in fail) or '  none')
print(f"\nwritten: {OUT.relative_to(REPO)}")
