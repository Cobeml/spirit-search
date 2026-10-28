"""Apply Cobe's 2026-10-27 ruling: 'Continue watt pricing and edge expansion
of Jesus and God. I like the progress so far. build it out.'

Promotes the two Tier-1 proposals he saw in the thread report into direct:
god P_authority 0.0001 (1.5 GW), jesus P_health 0.00005 (5 MW). Validates ids
against graph.json before writing; appends exactly one rulings-log entry.
Idempotent; every line individually rescalable.
"""
import json

R = '/home/cobe-liu/Developing/spirit-search/research/'
P = R + 'power_claims.json'
C = json.load(open(P))
g = json.load(open(R + 'graph.json'))
graph_ids = {n['id'] for n in g['nodes']}
RULED = '2026-10-27'
RULING = ("Cobe: 'Continue watt pricing and edge expansion of Jesus and God. "
          "I like the progress so far. build it out. Built build build'")

promoted = 0
for nid in ('god', 'jesus'):
    pr = C.get('proposals', {}).get(nid)
    if nid not in graph_ids:
        raise SystemExit(f'!! node {nid} missing from graph.json')
    if nid in C['direct']:
        if nid in C.get('proposals', {}):
            del C['proposals'][nid]
        print(f'  already direct: {nid}')
        continue
    if not pr:
        raise SystemExit(f'!! no proposal for {nid}')
    C['direct'][nid] = {
        'pool': pr['pool'], 'share': pr['share'], 'witness': pr['witness'],
        'why': pr['why'], 'role': pr['role'],
        'witness_files': pr.get('witness_files', []),
        'proposed': '2026-10-27', 'ruled': RULED,
    }
    del C['proposals'][nid]
    promoted += 1
    print(f'+ promoted {nid}: {pr["pool"]} x {pr["share"]} x w={pr["witness"]}')

if not any(r.get('ruling', '').startswith("Cobe: 'Continue watt pricing") for r in C.get('rulings', [])):
    C.setdefault('rulings', []).append({
        'date': RULED, 'ruling': RULING,
        'applied': 'Round-1 Tier-1 proposals promoted to direct: god '
                   'P_authority 0.0001 (1.5 GW), jesus P_health 0.00005 '
                   '(5 MW). Round-2 neighborhood nodes left as proposals for '
                   'the next gate.',
        'rescalable': 'Every line individually rescalable; name a node and a '
                      'new share.'})
C['updated'] = RULED
json.dump(C, open(P, 'w'), indent=1, ensure_ascii=False)
print(f'promoted {promoted}; direct now holds {len(C["direct"])} claims; '
      f'proposals pending: {len(C.get("proposals", {}))}')
