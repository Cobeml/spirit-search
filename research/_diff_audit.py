"""Diff the relevance audit before/after the queue-work regen (2026-10-21).
Prints first-card regressions and the seg/junk failure ids."""
import json

R = '/home/cobe-liu/Developing/spirit-search/research/'
old = {n['id']: n for n in json.load(open('/home/cobe-liu/.hermes/cache/scratch/audit_relevance_pre.json'))['nodes']}
new = json.load(open(R + 'audit_relevance.json'))
newn = {n['id']: n for n in new['nodes']}

print('FIRST-CARD REGRESSIONS (True->False):')
for nid, n in newn.items():
    o = old.get(nid)
    if o is None:
        print(f'  + NEW {nid}: flags={n.get("flags")} mode={n.get("mode")}')
        continue
    of, nf = (o.get('flags') or [None])[0], (n.get('flags') or [None])[0]
    if of is True and nf is not True:
        print(f'  {nid}: first {of} -> {nf}  mode {o.get("mode")} -> {n.get("mode")}')
print('\nFIRST-CARD IMPROVEMENTS (False->True):')
for nid, n in newn.items():
    o = old.get(nid)
    if o is None: continue
    of, nf = (o.get('flags') or [None])[0], (n.get('flags') or [None])[0]
    if of is not True and nf is True:
        print(f'  {nid}: first {of} -> {nf}  hl={len(n.get("flags") or [])}')

print('\nSEG/JUNK failing items (new audit):')
def walk(items, kind):
    for it in items:
        seg = (it.get('audit') or {}).get('seg')
        junk = (it.get('audit') or {}).get('junk')
        if seg or junk:
            label = it.get('id') or (it.get('frm'), it.get('to'))
            print(f'  {kind} {label}: seg={seg} junk={junk} :: {(it.get("text") or it.get("excerpt") or "")[:70]}')
walk(newn.values(), 'node')
for e in new.get('edges', []):
    seg = (e.get('audit') or {}).get('seg')
    junk = (e.get('audit') or {}).get('junk')
    if seg or junk:
        print(f'  edge {e.get("frm")}->{e.get("to")}: seg={seg} junk={junk}')

print('\nQUEUE-21 status in new audit:')
Q21 = ['fdr', 'alexander-hamilton', 'numa-pompilius', 'romulus', 'cato-elder',
       'diancecht', 'goibniu', 'dagda', 'brigit', 'miach', 'manannan', 'morrigan',
       'balor', 'math', 'dylan', 'aranrod', 'maelgwn', 'tethys', 'theia', 'crius', 'benedict-arnold']
for nid in Q21:
    n = newn.get(nid, {})
    f = n.get('flags') or []
    print(f'  {nid:22s} mode={n.get("mode"):8s} flags={f}')
