"""Queue work 2026-10-21, batch 1: American flesh record (hamilton, benedict-arnold).
Essays set only where missing (idempotent); no edges added; no power edits.
Sources: [15] Weems 1800 djvu (registered)."""
import json

ROOT = '/home/cobe-liu/Developing/spirit-search/research'
g = json.load(open(ROOT + '/graph.json'))
TODAY = '2026-10-21'

ESSAYS = {
    'alexander-hamilton': (
        "Weems fixes his office in the cabinet roster among the men Washington 'prudently "
        "rallied around him': 'Col. Hamilton, Secretary of the Treasury' [15]. The moralist "
        "then prices the man at his own scale: 'There was the gallant general Hamilton also "
        "— a gigantic genius — a statesman fit to rule the mightiest monarchy — a soldier "
        "fit to stand by Washington and give command.' [15]. The biography's next breath "
        "registers the fall, Hamilton conscripted into the object lesson of 'the Arnolds "
        "and Lees, the Hamiltons and Burrs of the earth', evidence that 'no valour, no "
        "genius alone can make men great' [15]. Weems gives the office, the genius, and the "
        "damnation, and stops there; the Treasury's day-to-day record was never his subject. "
        "The roster line is the document: the first Secretary of the Treasury, named in the "
        "same breath as the first Secretary of War and the first Chief Justice, the "
        "financial arm of the new state installed in one sentence [15]."),
    'benedict-arnold': (
        "Weems stages him as the case study in valour without religion: 'There was Benedict "
        "Arnold — while strutting a brigadier general on the public state, he could play you "
        "the great man', who 'out-marched Hannibal, and out-fought Burgoyne', who 'chased the "
        "British like curlews, or cooped them up like chickens!' [15]. The field record runs "
        "with the praise: 'Washington hurried on Gates and Arnold with their furious legions' "
        "[15], and when Morgan was driven back, 'Arnold then moved on to support Morgan; and, "
        "in a short time, with nine heavy regiments was closely engaged with the whole of the "
        "British army' [15]. The verdict on the castaway is Weems' own: 'cast out from the "
        "Eden of our republic, and amerced of greatness for ever' [15]. The gallantry and "
        "the treason live in the same witness, and the moralist needs both: without the "
        "out-marching of Hannibal, the cast-out means nothing."),
}

nodes = {n['id']: n for n in g['nodes']}
changed = []
for nid, essay in ESSAYS.items():
    n = nodes.get(nid)
    if n is None:
        print(f'!! node missing: {nid}')
        continue
    if not n.get('essay'):
        n['essay'] = essay
        changed.append(nid)
    else:
        print(f'  skip (essay exists): {nid}')

json.dump(g, open(ROOT + '/graph.json', 'w'), indent=2, ensure_ascii=False)
print('essays set:', changed)
