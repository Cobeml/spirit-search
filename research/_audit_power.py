"""Power gate audit (R7) — run after _power_model.py on every graph change.

Surfaces, as a standing gate report (research/power_audit.json + stdout):
  A. Tier-1 proposals: concrete pool/share/witness claims awaiting Cobe's ruling
     (from power_claims.json.proposals), with the watts they would carry.
  B. Tier-2 roles: unpriced nodes whose attested role is command/office/kingship
     or a cult with a natural pool, detected by lexicon + curated hints. These
     need a doctrine ruling (does epic/mythic command earn pool claims?), so
     they are listed, not priced.
  C. Dead routes: explicit influence claims that deliver 0 W because the
     downstream node has no direct power (single-hop R6 consequence).
  D. Unreviewed inheritance: nodes whose watts arrive ONLY through the 0.2
     kinship/transmission default (no explicit claims-file fraction).
  E. Staleness: graph.json power fields vs the claims file (claims_sha).

Cobe doctrine: pools/shares/witnesses are his gate. This audit never writes
power fields; it prices nothing silently.
"""
import json, hashlib, re, collections

R = '/home/cobe-liu/Developing/spirit-search/research/'
g = json.load(open(R + 'graph.json'))
raw = open(R + 'power_claims.json').read()
C = json.loads(raw)
POOLS = {k: float(v) for k, v in C['pools'].items()}
INF = {(e['from'], e['to'], e['type']): e['fraction'] for e in C['influence']}
nodes = {n['id']: n for n in g['nodes']}
Pw = {n['id']: n.get('power_watts_direct', 0) for n in g['nodes']}

# curated pool hints for Tier-2 figures whose role maps onto an existing pool
POOL_HINTS = {
    'ares': 'P_military', 'helios': 'P_energy', 'thor': 'P_energy', 'odin': 'P_authority',
    'agamemnon': 'P_military', 'hector': 'P_military', 'priam': 'P_authority',
    'achilles': 'P_military', 'odysseus': 'P_military', 'diomedes': 'P_military',
    'aeneas': 'P_authority', 'dido': 'P_authority', 'atli': 'P_authority',
    'sigurd': 'P_military', 'nuada': 'P_authority', 'dagda': 'P_authority',
    'lugh': 'P_authority', 'balor': 'P_authority', 'pwyll': 'P_authority',
    'arawn': 'P_authority', 'math': 'P_authority', 'bran': 'P_authority',
    'maelgwn': 'P_authority', 'romulus': 'P_authority',
}
ROLE_WORDS = re.compile(
    r'\b(king|queen|dictator|consul|emperor|tyrant|general|commander|commanded|command|'
    r'chief|secretary|president|justice|judge|master|lord|ruler|sovereign|prince|'
    r'leader of the host|All-Father|founder)\b', re.I)

def role_score(n):
    """2 per curated field hit (label/tradition/notes), 1 total for prose hits.
    Quote text alone never qualifies: biblical 'Lord' and 'in general' are noise."""
    score, where = 0, []
    cur = ' '.join([n.get('label', ''), n.get('tradition', '')] +
                   [x.get('text', '') for x in (n.get('notes') or [])])
    if ROLE_WORDS.search(cur):
        score += 2; where.append('curated')
    if ROLE_WORDS.search((n.get('essay') or '') + ' ' +
                          ' '.join(h.get('text', '') for h in (n.get('highlights') or []))):
        score += 1; where.append('prose')
    return score, where


def fmt(w):
    if w >= 1e12: return f'{w/1e12:.2f} TW'
    if w >= 1e9:  return f'{w/1e9:.2f} GW'
    if w >= 1e6:  return f'{w/1e6:.1f} MW'
    if w >= 1e3:  return f'{w/1e3:.1f} kW'
    return f'{w:.0f} W'

report = {}

# --- E. staleness ---
sha_now = hashlib.sha256(raw.encode()).hexdigest()[:16]
sha_stored = (g.get('power_model') or {}).get('claims_sha')
stale = sha_stored != sha_now
report['staleness'] = {'claims_sha_now': sha_now, 'claims_sha_in_graph': sha_stored,
                       'stale': stale,
                       'fix': 'rerun research/_power_model.py' if stale else None}

# --- A. Tier-1 proposals ---
props = []
for nid, pr in C.get('proposals', {}).items():
    n = nodes.get(nid)
    if not n:
        continue
    w = POOLS[pr['pool']] * pr['share'] * pr['witness']
    props.append({'id': nid, 'label': n.get('label'), 'pool': pr['pool'], 'share': pr['share'],
                  'witness': pr['witness'], 'watts_if_ruled': round(w, 1),
                  'role': pr['role'], 'why': pr['why'], 'witness_files': pr.get('witness_files', []),
                  'status': n.get('power_status')})
props.sort(key=lambda x: -x['watts_if_ruled'])
report['tier1_proposals'] = props

# --- B. Tier-2 roles (unpriced, role-attested, not yet proposed) ---
proposed = set(C.get('proposals', {}))
tier2 = []
for n in g['nodes']:
    if n['id'] in proposed or n.get('power_status') != 'unpriced':
        continue
    txt_score, where = role_score(n)
    if txt_score < 2:
        continue
    m = ROLE_WORDS.search(' '.join([n.get('label', ''), n.get('tradition', '')] +
                                   [x.get('text', '') for x in (n.get('notes') or [])])) \
        or ROLE_WORDS.search((n.get('essay') or '') + ' ' +
                              ' '.join(h.get('text', '') for h in (n.get('highlights') or [])))
    tier2.append({'id': n['id'], 'label': n.get('label'), 'era': n.get('era'),
                  'role_word': (m.group(0) if m else '').lower(),
                  'matched': '+'.join(where),
                  'pool_hint': POOL_HINTS.get(n['id'])})
report['tier2_roles'] = tier2

# --- C. dead routes (explicit fractions delivering 0) ---
dead = []
for e in g['edges']:
    key = (e['from'], e['to'], e['type'])
    i = e.get('influence', 0.0)
    if key in INF and INF[key] > 0 and not Pw.get(e['to']):
        dead.append({'from': e['from'], 'to': e['to'], 'type': e['type'],
                     'fraction': INF[key],
                     'why': f"target {e['to']} has no direct power; single-hop R6 routes 0"})
report['dead_routes'] = dead

# --- D. unreviewed inheritance (watts only via default fractions) ---
inherited = []
for n in g['nodes']:
    if n.get('power_status') != 'routed':
        continue
    edges_in = [(e['from'], e['to'], e['type'], e.get('influence')) for e in g['edges']
                if e['from'] == n['id'] and e.get('influence')]
    if not edges_in:
        continue
    defaults = [ed for ed in edges_in if (ed[0], ed[1], ed[2]) not in INF]
    if len(defaults) == len(edges_in):
        inherited.append({'id': n['id'], 'label': n.get('label'),
                          'total': n.get('power_watts_total'),
                          'default_edges': [f"{a}->{b}:{t}={i}" for a, b, t, i in defaults]})
inherited.sort(key=lambda x: -(x['total'] or 0))
report['unreviewed_inheritance'] = inherited

# --- status summary ---
counts = collections.Counter(n.get('power_status') for n in g['nodes'])
report['status_counts'] = dict(counts)
json.dump(report, open(R + 'power_audit.json', 'w'), indent=1, ensure_ascii=False)

# ---------- stdout report ----------
print(f"POWER GATE AUDIT  (claims {sha_now}{' STALE - rerun model' if stale else ' fresh'})")
print(f"status: {counts.get('direct',0)} direct / {counts.get('routed',0)} routed / {counts.get('unpriced',0)} unpriced\n")
print(f"A. TIER-1 PROPOSALS awaiting ruling ({len(props)}):")
for x in props:
    print(f"  {x['id']:22s} {x['pool']:<11s} share={x['share']:<7g} w={x['witness']}  -> {fmt(x['watts_if_ruled']):>9s}   {x['role']}")
print(f"\nB. TIER-2 ROLE-ATTESTED, unpriced, no proposal yet ({len(tier2)}):")
for x in tier2:
    print(f"  {x['id']:24s} era={x['era']:>6}  role~{x['role_word']:<12s} [{x['matched']}] pool_hint={x['pool_hint'] or '-'}")
print(f"\nC. DEAD ROUTES, explicit fraction delivers 0 W ({len(dead)}):")
for x in dead:
    print(f"  {x['from']:>22s} -> {x['to']:<22s} {x['fraction']}  ({x['why']})")
print(f"\nD. UNREVIEWED INHERITANCE, watts only via 0.2 default ({len(inherited)}):")
for x in inherited:
    print(f"  {x['id']:22s} total={fmt(x['total']):>9s}  via {', '.join(x['default_edges'])}")
