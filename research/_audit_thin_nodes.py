"""Thin-node audit (2026-10-21): existing nodes added from edges but never fleshed out.

The excerpt-first doctrine says highlights are primary and essays are anchors;
'fleshed out' therefore means: highlights whose FIRST card NAMES the node, edges
carrying excerpts that name both endpoints, a ledger-registered witness, an era,
and an honest power_status. This audit enumerates every node's flesh state,
ranks the thin ones by neighbor watts (post-scaling values), and publishes the
ranked thin-queue into research/_queue.json (key 'thin_nodes').
"""
import json, collections

R = '/home/cobe-liu/Developing/spirit-search/research/'
g = json.load(open(R + 'graph.json'))
rel = json.load(open(R + 'audit_relevance.json'))
q = json.load(open(R + '_queue.json'))

nodes = {n['id']: n for n in g['nodes']}
rel_nodes = {r['id']: r for r in rel.get('nodes', [])}
rel_edges = {(r.get('frm'), r.get('to')) or (r.get('from'), r.get('to')): r
             for r in rel.get('edges', [])}

deg_edges = collections.defaultdict(list)
for e in g['edges']:
    deg_edges[e['from']].append(e)
    deg_edges[e['to']].append(e)

def neighbor_watts(nid):
    tot = 0.0
    for e in deg_edges[nid]:
        other = e['to'] if e['from'] == nid else e['from']
        tot += nodes.get(other, {}).get('power_watts_total', 0) or 0
    return tot

rows = []
for n in g['nodes']:
    nid = n['id']
    essay = bool(n.get('essay'))
    hl = n.get('highlights') or []
    rn = rel_nodes.get(nid, {})
    flags = rn.get('flags') or []
    first_ok = flags[0] if flags else None
    my_edges = deg_edges[nid]
    edges_w_exc = sum(1 for e in my_edges if e.get('excerpts'))
    row = {
        'id': nid, 'label': n.get('label'), 'era': n.get('era'),
        'date_added': n.get('date_added'), 'tradition': n.get('tradition'),
        'essay': essay, 'n_highlights': len(hl),
        'first_hl_names': first_ok, 'audit_mode': rn.get('mode'),
        'n_proposals': len(n.get('proposals') or []),
        'edges': len(my_edges), 'edges_w_excerpts': edges_w_exc,
        'review': (n.get('review') or {}).get('status'),
        'wiki': bool(n.get('wiki')), 'power_status': n.get('power_status'),
        'neighbor_GW': round(neighbor_watts(nid) / 1e9, 2),
    }
    # flesh tier: 0 stub (no essay, no highlights) / 1 excerpt-thin (first card
    # fails to name the node, or <2 cards and no essay) / 2 edge-debt (some edge
    # lacks excerpts) / 3 ok
    if not essay and not hl:
        row['tier'] = 0
    elif first_ok is False or (not essay and len(hl) < 2):
        row['tier'] = 1
    elif edges_w_exc < len(my_edges):
        row['tier'] = 2
    else:
        row['tier'] = 3
    rows.append(row)

thin = [r for r in rows if r['tier'] < 3]
thin.sort(key=lambda r: (r['tier'], -r['neighbor_GW']))
ok = [r for r in rows if r['tier'] == 3]

out = {
    'date': '2026-10-21',
    'note': 'flesh tiers: 0 stub (no essay, no highlights) / 1 excerpt-thin (first card '
            'fails the name rule or <2 cards) / 2 edge-debt (edges without excerpts) / 3 ok. '
            'Rank within tier by neighbor watts (post power-scaling values).',
    'counts': dict(collections.Counter(r['tier'] for r in rows)),
    'thin': thin, 'ok_count': len(ok),
}
json.dump(out, open(R + 'thin_nodes_audit.json', 'w'), indent=1, ensure_ascii=False)

q['thin_nodes'] = [[r['id'], r['tier'], r['neighbor_GW']] for r in thin]
q['thin_nodes_note'] = ('2026-10-21 thin-node audit: graph nodes added from edges but not '
                        'fleshed out, ranked by neighbor watts after the power scaling. Work '
                        'top-down per queue-mode; Cobe gates salience before each batch.')
json.dump(q, open(R + '_queue.json', 'w'), indent=2, ensure_ascii=False)

print(f"flesh state of {len(rows)} nodes: {out['counts']}")
print(f"tier 0 stubs ({sum(1 for r in thin if r['tier']==0)}):")
for r in [x for x in thin if x['tier'] == 0]:
    print(f"  {r['id']:24s} nbr={r['neighbor_GW']:>10.2f} GW  era={r['era']:>6} added={r['date_added']}  pw={r['power_status']}")
print(f"tier 1 excerpt-thin ({sum(1 for r in thin if r['tier']==1)}):")
for r in [x for x in thin if x['tier'] == 1]:
    print(f"  {r['id']:24s} nbr={r['neighbor_GW']:>10.2f} GW  hl={r['n_highlights']} essay={int(r['essay'])} first_names={r['first_hl_names']} era={r['era']}")
print(f"tier 2 edge-debt ({sum(1 for r in thin if r['tier']==2)}):")
for r in [x for x in thin if x['tier'] == 2][:25]:
    print(f"  {r['id']:24s} nbr={r['neighbor_GW']:>10.2f} GW  edges {r['edges_w_excerpts']}/{r['edges']} excerpted")
