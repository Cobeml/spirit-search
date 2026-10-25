"""Queue work 2026-10-21, batch 5: Greek Titan catalogue (tethys, theia, crius).
Evelyn-White Hesiod [26]. Idempotent on essay presence."""
import json

ROOT = '/home/cobe-liu/Developing/spirit-search/research'
g = json.load(open(ROOT + '/graph.json'))
TODAY = '2026-10-21'

ESSAYS = {
    'tethys': (
        "The catalogue births her among the eldest of Earth's children: Earth lay with "
        "Heaven 'and bare deep-swirling Oceanus, Coeus and Crius and Hyperion and Iapetus, "
        "Theia and Rhea, Themis and Mnemosyne and gold-crowned Phoebe and lovely Tethys' "
        "[26]. Her work is the world's water: 'And Tethys bare to Ocean eddying rivers, "
        "Nilus, and Alpheus, and deep-swirling Eridanus, Strymon, and Meander, and the "
        "fair stream of Ister' [26]. Among the eldest daughters of that bed the poem ranks "
        "'Styx who is the chiefest of them all', and counts 'three thousand neat-ankled "
        "daughters of Ocean who are dispersed far and wide' [26]."),
    'theia': (
        "One line gives her the sky's lights: 'And Theia was subject in love to Hyperion "
        "and bare great Helius (Sun) and clear Selene (Moon) and Eos (Dawn) who shines "
        "upon all that are on earth and upon the deathless Gods who live in the wide "
        "heaven' [26]. The birth catalogue names her among the first children of Heaven "
        "and Earth; 'After them was born Cronos the wily, youngest and most terrible of "
        "her children' [26]."),
    'crius': (
        "Born in the first catalogue of Heaven's children, 'Coeus and Crius and Hyperion "
        "and Iapetus' [26], his marriage line runs one sentence in the poem: 'And Eurybia, "
        "bright goddess, was joined in love to Crius and bare great Astraeus, and Pallas, "
        "and Perses who also was eminent among all men in wisdom' [26]. Through Astraeus "
        "the line continues into the weather: 'And Eos bare to Astraeus the strong-hearted "
        "winds, brightening Zephyrus, and Boreas, headlong in his course, and Notus' [26]."),
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
