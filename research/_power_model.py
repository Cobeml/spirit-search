"""Power model v2 for the High Drama spirit graph.

Methodology (documented, revisable):
1. POOLS. Modern industry is partitioned into named power pools measured in watts
   as continuous energy throughput (estimates, order-of-magnitude, cited as assumed).
   Pool values live in research/power_claims.json (claims as reviewable data).
2. DIRECT POWER = pool x claim-share (which spirits the pool's activity cites/descends
   from) x witness-strength (documentary grounding in our corpus: 1.0 multiple primary
   witnesses, 0.75 one primary plus secondary, 0.5 secondary only, 0.25 conjecture).
   Direct claims are entered ONLY by Cobe's ruling (the pricing gate); proposals
   accumulate in power_claims.json.proposals until he rules.
3. PROXY POWER (influence): an edge with influence fraction i routes i x P_direct
   of the downstream node to the upstream node, SINGLE HOP ONLY (R6): the 'from'
   node collects from the 'to' node, and only the 'to' node's DIRECT power is
   routable. No recursion: influence-of-influence is excluded by design, so a
   chain A->B->C routes nothing to A unless B carries a direct claim. Conflict
   cycles therefore cannot inflate.
4. POWER STATUS. Every node is stamped power_status:
     'direct'   - carries a ruled pool claim (in power_claims.json.direct)
     'routed'   - no claim, but influence edges deliver proxy watts
     'unpriced' - no claim and no proxy: a GATE STATE, not a finding of zero power.
   The site renders 'unpriced' as unpriced, never as '0 W'. Documented
   office-holders that sit unpriced are flagged by research/_audit_power.py
   with concrete proposals for the gate (rule R7).
5. ERA SCALING. watts_at_era = watts_now x pop(era)/pop(2026): the coin of their
   own time. Population is log-linear between the cited anchors in
   power_claims.json.pop_anchors (the old two-endpoint curve mispriced 1800
   by ~6x and -750 by ~2x).

RECALCULATION RULES (run on every graph change):
R1 node split   - if a new node inherits power previously attributed to an old node,
                  subtract that share from the old node's claim before recomputing.
R2 new edge     - recomputes all proxy flows (single-hop re-run).
R3 witness upgrade - if a witness-strength changes (new fetch), direct power re-derives.
R4 pool revision - pools are assumptions; changing a pool value re-derives everything below.
R5 era correction - correcting an era re-values watts_at_era only.
R6 single-hop    - influence routes i x downstream DIRECT power upstream, no recursion;
                  cycle-safe by construction.
R7 pricing gate  - no pool share enters power_claims.json.direct without Cobe's ruling;
                  every graph change must be followed by _power_model.py then
                  research/_audit_power.py, and no documented commander or
                  office-holder may ship a wave while silently reading 0 W
                  (the audit must have surfaced a proposal for them).

Claims file: research/power_claims.json (pools, direct, influence, pop_anchors,
proposals). graph.json power fields are OUTPUT of this script; never hand-edit them.
"""
import json, math, hashlib, bisect, datetime

R = '/home/cobe-liu/Developing/spirit-search/research/'
p = R + 'graph.json'
g = json.load(open(p))
claims_raw = open(R + 'power_claims.json').read()
C = json.loads(claims_raw)
POOLS = {k: float(v) for k, v in C['pools'].items()}
DIRECT = {k: (v['pool'], v['share'], v['witness'], v['why']) for k, v in C['direct'].items()}
INF = {(e['from'], e['to'], e['type']): e['fraction'] for e in C['influence']}
POP_ANCH = {int(k): float(v) for k, v in C['pop_anchors'].items()}
YEAR_NOW = 2026
CLAIMS_SHA = hashlib.sha256(claims_raw.encode()).hexdigest()[:16]


def pop_factor(year):
    """pop(year)/pop(2026): log-linear between cited population anchors."""
    ys = sorted(POP_ANCH)
    y = ys[0] if year is None else year
    if y <= ys[0]:
        pop = POP_ANCH[ys[0]]
    elif y >= ys[-1]:
        pop = POP_ANCH[ys[-1]]
    else:
        i = bisect.bisect_right(ys, y) - 1
        y0, y1 = ys[i], ys[i + 1]
        p0, p1 = POP_ANCH[y0], POP_ANCH[y1]
        t = (y - y0) / (y1 - y0)
        pop = p0 * math.exp(t * math.log(p1 / p0)) if p1 != p0 else p0
    return pop / POP_ANCH[ys[-1]]


nodes = {n['id']: n for n in g['nodes']}
Pw = {}  # direct watts now
for nid in nodes:
    Pw[nid] = 0.0
for nid, (pool, share, strength, why) in DIRECT.items():
    Pw[nid] = POOLS[pool] * share * strength
    nodes[nid]['power_rationale'] = why
    nodes[nid]['power_pool'] = pool
    nodes[nid]['power_witness_strength'] = strength

# influence: explicit claims-file fractions; typed transmission/kinship edges
# without an explicit entry take the default 0.2; everything else defaults 0.0
for e in g['edges']:
    key = (e['from'], e['to'], e['type'])
    if key in INF:
        e['influence'] = INF[key]
    elif e['type'] in ('transmission', 'kinship', 'kinship+interaction'):
        e['influence'] = 0.2
    else:
        e['influence'] = 0.0

# SINGLE-HOP proxy (R6): upstream commands i x P_direct(downstream)
P = {}
for nid in nodes:
    P[nid] = Pw[nid]
for e in g['edges']:
    i = e.get('influence', 0.0)
    if i:
        P[e['from']] = P.get(e['from'], 0) + i * Pw.get(e['to'], 0.0)

for nid, n in nodes.items():
    n['power_watts_direct'] = round(Pw[nid], 3)
    n['power_watts_total'] = round(P.get(nid, 0), 3)
    n['power_watts_proxy'] = round(P.get(nid, 0) - Pw[nid], 3)
    if nid in DIRECT:
        n['power_status'] = 'direct'
    elif P.get(nid, 0) > 0:
        n['power_status'] = 'routed'
    else:
        n['power_status'] = 'unpriced'
    era = n.get('era')
    n['power_watts_at_era'] = round((P.get(nid, 0)) * pop_factor(era if era is not None else 2000), 3) if P.get(nid, 0) else 0

g['power_model'] = {
    'version': 2, 'year': YEAR_NOW,
    'pools': POOLS,
    'method': 'pool x claim-share x witness-strength = direct; influence edges route i x downstream DIRECT power upstream, single-hop only (R6: no recursion, cycle-safe); power_status per node: direct | routed | unpriced (gate state, not a zero-power finding)',
    'claims_file': 'research/power_claims.json',
    'claims_sha': CLAIMS_SHA,
    'computed_at': datetime.datetime.now().isoformat(timespec='seconds'),
    'recalc_rules': ['R1 node split: subtract inherited share from old node before recompute',
                     'R2 new edge: re-run single-hop proxy',
                     'R3 witness-strength change: re-derive direct',
                     'R4 pool revision: re-derive everything',
                     'R5 era correction: re-derive watts_at_era only',
                     'R6 single-hop: influence routes direct power only, no recursion, cycle-safe',
                     'R7 pricing gate: direct claims only by Cobe ruling; _audit_power.py must surface proposals for documented office-holders before a wave ships']}
g['version'] = 6
json.dump(g, open(p, 'w'), indent=2, ensure_ascii=False)


def fmt(w):
    if w >= 1e12: return f'{w/1e12:.1f} TW'
    if w >= 1e9:  return f'{w/1e9:.1f} GW'
    if w >= 1e6:  return f'{w/1e6:.1f} MW'
    if w >= 1e3:  return f'{w/1e3:.0f} kW'
    return f'{w:.0f} W'

counts = {'direct': 0, 'routed': 0, 'unpriced': 0}
for nid, n in sorted(nodes.items(), key=lambda kv: -kv[1].get('power_watts_total', 0)):
    counts[n['power_status']] += 1
    if n.get('power_watts_total', 0) > 0:
        print(f"{nid:22s} {n['power_status'][:3]} direct={fmt(n['power_watts_direct']):>9s} proxy={fmt(n['power_watts_proxy']):>9s} total={fmt(n['power_watts_total'])}")
print(f"\nstatus: {counts['direct']} direct / {counts['routed']} routed / {counts['unpriced']} unpriced  (claims {CLAIMS_SHA})")
