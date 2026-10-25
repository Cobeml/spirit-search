"""Queue work 2026-10-21, batch 3: Irish myth cluster, all from MacCulloch 1911 [23].
diancecht, goibniu, dagda, brigit, miach, manannan, morrigan, balor.
Idempotent on essay presence. Miach carries a thin-witness note."""
import json

ROOT = '/home/cobe-liu/Developing/spirit-search/research'
g = json.load(open(ROOT + '/graph.json'))
TODAY = '2026-10-21'

ESSAYS = {
    'diancecht': (
        "The surgeon's record is kept in MacCulloch's summary: 'Diancecht, whose name may "
        "mean \"swift in power,\" was god of medicine, and, with Creidne's help, fashioned a "
        "silver hand for Nuada' [23]. At the second battle of Mag-tured he 'presided over a "
        "healing-well containing magic herbs', where the power of spells 'caused the mortally "
        "wounded who were placed in it to recover', and so the well was named: 'Hence it was "
        "called \"the spring of health\"' [23]. The healing fame survived the paganism: 'He "
        "is also referred to in the S. Gall MS., where his healing powers are extolled' [23]."),
    'goibniu': (
        "The smith-god's craft is defined at the battle: 'Such a god is Goibniu, eponymous "
        "god of smiths (Old Ir. goba \"smith\"), and the divine craftsman at the battle of "
        "Mag-tured, making spears which never failed to kill' [23]. His uncanny reputation "
        "held even under the new religion: 'S. Patrick prayed against the \"spells of women, "
        "smiths, and Druids\"', and an eighth-century butter spell 'appeals to his "
        "\"science\"' [23]. He is cook as well as armorer: 'Goibniu is also connected with "
        "the culinary art in myth, and, like Hephaistos, prepares the feast of the gods, "
        "while his ale preserves their immortality' [23]. The trace runs into the "
        "building-trade legend of the Gobhan Saer, 'to whom the building of round towers is "
        "ascribed' [23]."),
    'dagda': (
        "MacCulloch seats him at the head of the pantheon: 'An early chief of the gods is "
        "Dagda', so called in the battle-story 'because he promised to do more than all the "
        "other gods together', whence the saying \"It is thou art the good hand\" (dag-dae) "
        "[23]. The same scholar reads him as the Celtic Dispater, the earth-father from whom "
        "the old genealogies of the gods descend, and whose consort the mother-goddess "
        "became [23]. Of the four treasures the Tuatha brought from their learning-cities, "
        "his is 'the Dagda's inexhaustible cauldron' [23]."),
    'brigit': (
        "The goddess of culture is defined by her following: 'Danu is also identified with "
        "Brigit, goddess of knowledge (dan), perhaps through a folk-etymology. She was "
        "worshipped by poets, and had two sisters of the same name connected with leechcraft "
        "and smithwork' [23]. The fire association placed her with the perpetual flames: "
        "'she may have been associated with a cult of fire, like Brigit and like another "
        "goddess Sul, equated with Minerva at Bath' [23]. The battle-tradition gives her "
        "grief its precedence: her son Ruadan, sent to spy for Bres, was slain, and 'His "
        "mother's wailing for him was the first mourning wail ever heard in Erin' [23]."),
    'miach': (
        "The son outdid the surgeon and paid for it: 'His son Miach replaced this by a magic "
        "restoration of the real hand, and in jealousy his father slew him' [23]. The "
        "medicine kept coming from the grave: 'Three hundred and sixty-five herbs grew from "
        "his grave, and were arranged according to their properties by his sister Airmed, "
        "but Diancecht again confused them, \"so that no one knows their proper cures\"' "
        "[23]. Two sentences carry the whole record of him: the restoration, the jealous "
        "father, the herbs, the deliberate confusion. A tradition that gives him no words of "
        "his own defines him entirely by what his hands grew back, and by the reading of "
        "MacCulloch's source the slaying is 'a version of the Maerchen formula of the "
        "jealous master' [23]."),
    'manannan': (
        "The sea-god's son is placed by descent: 'The sea-god Lir is probably the Liur of "
        "Ossianic ballads, and his son Manannan is perhaps \"the Son of the Sea\" in a "
        "Gaelic song' [23]. His gift defines the gods' fate: after the Dagda's death, "
        "'Manannan is said to have conferred immortality upon the Tuatha De Danann' [23]. "
        "Among the side, the divine people of the mounds, 'Manannan is Fand's consort' "
        "[23]."),
    'morrigan': (
        "The war-goddess appears as one of three: 'war-goddesses are more prominent, "
        "usually as a group of three - Morrigan, Neman, and Macha' [23]. The fourth name, "
        "Badb, 'sometimes takes the place of one of these, or is identical with Morrigan' "
        "[23]. The bird is the form: 'Badb means \"a scald-crow,\" under which form the "
        "war-goddesses appeared, probably because these birds were seen near the slain' "
        "[23]. The name itself may rank her above the battle: 'The name Morrigan may mean "
        "\"great queen\"' [23]."),
    'balor': (
        "The Fomorian's weapon was his eye: 'His one eye had become evil by contact with "
        "the poisonous fumes of a concoction which his father's Druids were preparing. The "
        "eyelid required four men to raise it, when his evil eye destroyed all on whom its "
        "glance fell' [23]. His consort shared the venom: 'Balor had a consort Cethlenn, "
        "whose venom killed Dagda' [23]. The death that closes his claim is his "
        "grandson's: MacCulloch notes the Gaulish hammer-god read 'as the equivalent of the "
        "Irish Lug slaying Balor' [23]."),
}

NOTES = {
    'miach': "2026-10-21 queue pass: thin witness; two MacCulloch passages carry his whole "
             "record. Under-definition is a finding, not a flaw.",
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
    if nid in NOTES:
        have = any(x.get('date') == TODAY for x in (n.get('notes') or []))
        if not have:
            n.setdefault('notes', []).append(dict(date=TODAY, text=NOTES[nid]))

json.dump(g, open(ROOT + '/graph.json', 'w'), indent=2, ensure_ascii=False)
print('essays set:', changed)
