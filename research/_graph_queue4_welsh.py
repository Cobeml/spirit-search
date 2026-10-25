"""Queue work 2026-10-21, batch 4: Welsh cluster (math, dylan, aranrod, maelgwn).
Guest vol 3 [21], Guest 1877 [66], MacCulloch [23]. Idempotent on essay presence."""
import json

ROOT = '/home/cobe-liu/Developing/spirit-search/research'
g = json.load(open(ROOT + '/graph.json'))
TODAY = '2026-10-21'

ESSAYS = {
    'math': (
        "The Fourth Branch opens on the throne: 'Math the son of Mathonwy was lord over "
        "Gwynedd, and Pryderi the son of Pwyll was lord over the one and twenty Cantrevs of "
        "the South' [21]. The king's condition is the tale's strangest law: 'Math the son of "
        "Mathonwy could not exist unless his feet were in the lap of a maiden, except only "
        "when he was prevented by the tumult of war' [21]. The maiden held was Goewin, "
        "'the fairest maiden of her time' [21]. The making hand shows twice: the "
        "punishment of the brothers, and the wife made for Llew, for 'By magic, Math and "
        "Gwydion form a wife for Llew' out of flowers [23]."),
    'dylan': (
        "Math names him at the baptism: 'Verily, said Math the son of Mathonwy, concerning "
        "the fine yellow-haired boy, \"I will cause this one to be baptized, and Dylan is "
        "the name I will give him.\" So they had the boy baptized, and as they baptized him "
        "he plunged into the sea.' [66]. The sea took him as its own: 'when he was in the "
        "sea, he took its nature, and swam as well as the best fish that was therein. And "
        "for that reason was he called Dylan, the son of the Wave. Beneath him no wave ever "
        "broke.' [66]. The death is numbered in the family's blows: 'And the blow whereby "
        "he came to his death, was struck by his uncle Govannon. The third fatal blow was "
        "it called.' [66]."),
    'aranrod': (
        "Gwydion names her for the throne's test: 'seek Arianrod, the daughter of Don, thy "
        "niece, thy sister's daughter' [21]. The wand decides: 'Then he took up his magic "
        "wand, and bent it. \"Step over this,\" said he, \"and I shall know if thou art "
        "the maiden.\"' [21]. The shaming follows her refusal to name her son: at her "
        "castle 'Arianrod arose to meet him', and Gwydion answered her anger with \"This "
        "youth, he is thy son\" [21]. MacCulloch keeps the wider genealogy, the children "
        "of Don with 'her sons, Dylan and Llew' [23]."),
    'maelgwn': (
        "The Taliesin tale seats him at the Christmas court: 'Elphin son of Gwyddno went by "
        "a Christmas invitation to his uncle, Maelgwn Gwynedd, who some time after this "
        "held open court at Christmastide in the castle of Dyganwy' [66]. The flattery the "
        "tale puts in his lords' mouths is the king's own measure: 'Is there in the whole "
        "world a king so great as Maelgwn, or one on whom Heaven has bestowed so many "
        "spiritual gifts as upon him?' [66]. His line carries the prerogative: Rhun his "
        "son, 'a man whose prerogative it is, that he may join in counsel with all' [66]."),
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
