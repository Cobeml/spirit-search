"""Post-recalc zero-power audit + staleness measure vs graph.json.bak (2026-10-21)."""
import json, os

R = '/home/cobe-liu/Developing/spirit-search/research/'
g = json.load(open(R + 'graph.json'))
bak = R + 'graph.json.bak'

# staleness: how many nodes' power_watts_total differed between .bak (what the site
# last shipped, roughly) and the fresh recalc?
stale = 0
if os.path.exists(bak):
    try:
        old = {n['id']: n for n in json.load(open(bak))['nodes']}
        for n in g['nodes']:
            o = old.get(n['id'])
            if o and (o.get('power_watts_total') or 0) != (n.get('power_watts_total') or 0):
                stale += 1
                if stale <= 15:
                    print(f"STALE {n['id']:22s} {o.get('power_watts_total')} -> {n.get('power_watts_total')}")
        print(f"stale totals vs .bak: {stale}")
    except Exception as ex:
        print('bak unreadable:', ex)

zero = [n for n in g['nodes'] if not n.get('power_watts_total')]
routed = [n for n in g['nodes'] if n.get('power_watts_total') and not n.get('power_pool')]
direct = [n for n in g['nodes'] if n.get('power_pool')]
print(f"\npost-recalc: direct-priced={len(direct)} routed-only={len(routed)} unpriced(0W)={len(zero)} of {len(g['nodes'])}")

# every unpriced node with edges (connectivity) — the candidates for role review
inc = {}
for e in g['edges']:
    if e.get('influence'):
        inc.setdefault(e['from'], []).append((e['to'], e.get('influence')))
print("\nUNPRICED with at least one edge (id | degree | incoming-infl-edges):")
deg = {}
for e in g['edges']:
    deg[e['from']] = deg.get(e['from'], 0) + 1
    deg[e['to']] = deg.get(e['to'], 0) + 1
for n in sorted(zero, key=lambda x: -deg.get(x['id'], 0)):
    d = deg.get(n['id'], 0)
    if d:
        print(f"  {n['id']:24s} deg={d:2d} infl-in={len(inc.get(n['id'],[]))} era={n.get('era')}")

print("\nDEAD ROUTES (influence edges whose downstream has zero DIRECT power => routes 0 W):")
Pw = {n['id']: n.get('power_watts_direct', 0) for n in g['nodes']}
seen = set()
for e in g['edges']:
    i = e.get('influence', 0)
    if i and not Pw.get(e['to']):
        k = (e['from'], e['to'], e['type'], i)
        if k in seen: continue
        seen.add(k)
        print(f"  {e['from']:>20} -> {e['to']:<20} type={e['type']:<18} infl={i} delivers={fmt if (fmt:=0) else '0 W'}")

print("\nDEFAULT-ROUTED nodes (watts arrive ONLY via the 0.2 kinship/transmission default, no INF entry):")
INF_KEYS = None
import re
src = open(R + '_power_model.py').read()
INF_KEYS = set()
# collect explicit INF keys from source
for m in re.finditer(r"INF\[\('([^']+)','([^']+)','([^']+)'\)\]=([0-9.]+)", src):
    INF_KEYS.add((m.group(1), m.group(2), m.group(3)))
for m in re.finditer(r"\('([^']+)','([^']+)','([^']+)'\):([0-9.]+)", src):
    INF_KEYS.add((m.group(1), m.group(2), m.group(3)))
for n in sorted(g['nodes'], key=lambda x: -(x.get('power_watts_total') or 0)):
    if n.get('power_pool') or not n.get('power_watts_total'): continue
    srcs = [(e['from'], e['to'], e['type'], e.get('influence')) for e in g['edges']
            if e['from'] == n['id'] and e.get('influence')]
    defaults = [s for s in srcs if (s[0], s[1], s[2]) not in INF_KEYS]
    if defaults:
        tot = n.get('power_watts_total')
        print(f"  {n['id']:22s} total={tot/1e12:.2f} TW" if tot >= 1e12 else
              f"  {n['id']:22s} total={tot/1e9:.2f} GW" if tot >= 1e9 else
              f"  {n['id']:22s} total={tot/1e6:.1f} MW", "| default edges:",
              ", ".join(f"{a}->{b}:{t}={i}" for a, b, t, i in defaults))
