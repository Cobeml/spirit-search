#!/usr/bin/env python3
"""Great-works pass, batch 2. Idempotent."""
import json
p = '/home/cobe-liu/Developing/spirit-search/research/graph.json'
g = json.load(open(p))
nodes = {n['id']: n for n in g['nodes']}

def add_para(nid, marker, text):
    n = nodes[nid]
    if marker in n['essay']:
        print('skip', nid); return
    n['essay'] += '\n\n' + text
    print('add', nid)

add_para('asclepius', 'gentle craftsman', """Pindar's third Pythian, older than any other full account, prices the healer honestly. Asclepius is 'that gentle craftsman who drove pain from the limbs that he healed, that hero who cured all types of diseases', working his whole case list in turn, 'tending some of them with gentle incantations, others with soothing potions, or by wrapping remedies all around their limbs, and others he set right with surgery' [69]. Then the practice fails in the one direction it cannot be allowed to go: 'But even skill is enthralled by the love of gain. Gold shining in his hand turned even that man, for a handsome price, to bring back from death a man who was already caught. And so the son of Cronus hurled his shaft with his hands through both of them' [69]. The first documented medical fee is a resurrection fee, and the tradition's pricing is immediate: medicine may push the boundary of death only at the cost of the doctor.""")

add_para('chiron', 'beast of the wilds whose mind was friendly', """Pindar keeps the wish simple: 'I would want Cheiron the son of Philyra to be alive again... the beast of the wilds whose mind was friendly to men', since with him alive 'I would have persuaded him to send even now a healer to cure noble men of their feverish diseases' [69]. The centaur's obituary is a staffing gap; the tradition measures his goodness by the clinic that could no longer be staffed after him.""")

add_para('hephaestus', 'festooned the bed-posts', """In the Odyssey's most performed lay, the forge turns its skill on its own household. Tipped off by the Sun, he 'went to his smithy brooding mischief, got his great anvil into its place, and began to forge some chains which none could either unloose or break', and 'festooned the bed-posts all over with chains like cobwebs' [54]. Workmanship serving jealousy: the one fine specimen of divine engineering in Homer spent on matrimonial evidence. The scene pays in the currency he commands, the whole assembly of gods coming to his bedroom to view the catch, and compensation negotiated in person with the sea god standing bond.""")

add_para('thetis', 'such prizes as silver-footed Thetis', """The Odyssey hears of her last rite for the son. Agamemnon's ghost recalls that after the fall of the Achaean dead, 'you never saw such prizes as silver-footed Thetis offered in your honour; for the gods loved you well' [54]. Her power registers at the one moment power cannot help: purse and games, love's expenditure upon a fixed grave.""")

add_para('hector', 'war is man', """The Iliad writes him at the doorway as the war's civil price. To Andromache's pleading he answers the single most quoted order in the poem: 'Go, then, within the house, and busy yourself with your daily duties, your loom, your distaff, and the ordering of your servants; for war is man's matter, and mine above all others of them that have been born in Ilius' [1]. The poem's finest soldier orders his household to stand down and takes the job description himself; the war is 'man's matter', and his most of all. Vergil keeps the receipt. In Aeneas' dream the hero appears as casualty returns: 'When Hector's ghost before my sight appears: A bloody shroud he seem'd, and bath'd in tears', dragged body 'black with dust', so unlike the man 'who return'd from toils Of war, triumphant' [35]. The Roman founder's night is haunted by the defender he had to replace.""")

add_para('paris-alexandrus', 'decides in favour of Aphrodite', """The Cypria summary preserves the judgment scene whole: 'The three are led by Hermes at the command of Zeus to Alexandrus on Mount Ida for his decision, and Alexandrus, lured by his promised marriage with Helen, decides in favour of Aphrodite' [26]. The tradition's own valuation: he is the one man whose taste could start the war, bribed by a wedding. The Aeneid, putting the cost where its enemy can pay it, lodges the deepest Roman scar in Juno's breast: 'Deep graven in her heart the doom remain'd Of partial Paris' [35]. The great poems agree that his one durable act was an aesthetic purchase.""")

add_para('heracles', 'the ancient god Hercules is', """Odysseus meets him twice over in the underworld, and the poem states the split outright: 'mighty Hercules, but it was his phantom only, for he is feasting ever with the immortal gods, and has lovely Hebe to wife' [54]. The tradition's earliest double-entry: the shadow below, scowling with bow drawn, the person above at table 'feasting ever'. Herodotus, checking the name abroad, adjudicates the confusion four centuries later: 'These researches show plainly that there is an ancient god Hercules; and my own opinion is that those Greeks act most wisely who build and maintain two temples of Hercules, in the one of which the Hercules worshipped is known by the name of Olympian, and has sacrifice offered to him as an immortal, while in the other the honours paid are such as are due to' a hero [55]. The historian's fieldwork in Tyre and Thasos institutionalizes what the Odyssey already knew: two Heracleses, and the books must be kept separately.""")

add_para('eurypylus-telephid', 'handsomest man I ever saw', """Odysseus, dead, remembers killing him: 'that valiant hero Eurypylus son of Telephus, who was the handsomest man I ever saw except Memnon; many others also of the Ceteians fell around him by reason of a woman's bribes' [54]. The afterlife notice ratifies the catalogue's judgment: beauty and a bought war, dead among the Ceteians, carried into Homer by the one Achaean whose trade was the memory.""")

new_edges = []
# Atlas: done in batch 1. Poseidon: done. Themis/styx are sturdily covered.
json.dump(g, open(p, 'w'), indent=2, ensure_ascii=False)
print('nodes', len(g['nodes']), 'edges', len(g['edges']))
