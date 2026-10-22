"""Apply Cobe's 2026-10-21 ruling: 'Do power scaling for all the ones awaiting'.

Promotes all Tier-1 proposals into power_claims.json.direct, prices the 13 Tier-2
role-attested epic/mythic figures (epic command earns claims per this ruling),
and prices the dead-route targets (apollo, mercury, paris, atlas) so all 7 dead
influence routes activate under R6. Shares are documented anchors; every line
stays individually rescalable. Idempotent: re-running adds nothing new.
"""
import json

P = '/home/cobe-liu/Developing/spirit-search/research/power_claims.json'
C = json.load(open(P))
RULED = '2026-10-21'

# --- 1. promote every pending Tier-1 proposal into direct ---
promoted = 0
for nid, pr in list(C['proposals'].items()):
    if nid in C['direct']:
        del C['proposals'][nid]
        continue
    C['direct'][nid] = {
        'pool': pr['pool'], 'share': pr['share'], 'witness': pr['witness'],
        'why': pr['why'], 'role': pr['role'],
        'witness_files': pr.get('witness_files', []),
        'proposed': pr.get('date', RULED), 'ruled': RULED,
    }
    del C['proposals'][nid]
    promoted += 1

# --- 2. Tier-2 role-attested figures (epic/mythic command; smaller shares than
#        flesh record; witness = corpus grounding of the role) ---
TIER2 = {
    'agamemnon':      ('P_military',  0.0001,  1.0, 'Leader of the host at Troy; the epic archcommander whose summons binds the Achaean kings.', 'Commander of the Achaean host', ['plutarch-lives-dryden-clough-gutenberg.txt']),
    'priam':          ('P_authority', 0.0001,  1.0, 'King of Troy; the throne the whole Iliad pressures.', 'King of Troy', ['plutarch-lives-dryden-clough-gutenberg.txt']),
    'aeneas':         ('P_authority', 0.0001,  1.0, 'Founder-commander carrying the household gods to Latium; the exile-claim at the root of the Roman order.', 'Founder-commander of the Trojans', ['virgil-aeneid-dryden.txt', 'serviusaeneid.txt']),
    'evander':        ('P_authority', 0.00005, 1.0, 'Arcadian king on the future site of Rome; hosts the Trojan remnant.', 'Arcadian king', ['virgil-aeneid-dryden.txt']),
    'latinus':        ('P_authority', 0.00005, 1.0, 'Latin king whose daughter transfers the kingship line.', 'King of the Latins', ['virgil-aeneid-dryden.txt']),
    'odin':           ('P_authority', 0.0005,  1.0, 'The All-Father; hanged for wisdom, one-eyed for the runes; sovereign of the Norse pantheon.', 'All-Father, sovereign of the Aesir', ['poeticedda00belluoft_djvu.txt', 'bellows-poetic-edda-1923-full.txt']),
    'math':           ('P_authority', 0.0002,  0.5, 'Lord of Gwynedd in the Fourth Branch; the name-making and flower-making uncle holds the northern throne.', 'Lord of Gwynedd', ['guest-mabinogion-1877-full.txt']),
    'maelgwn':        ('P_authority', 0.0001,  0.5, 'Historical king of Gwynedd cast in the Taliesin tale as captor and judge of poets.', 'King of Gwynedd', ['guest-mabinogion-1877-full.txt']),
    'nuada':          ('P_authority', 0.0002,  0.5, 'King of the Tuatha De Danann; the hand-lost king re-armed in silver, the sovereignty that must be whole.', 'King of the Tuatha', ['macculloch-religion-ancient-celts-1911.txt']),
    'balor':          ('P_authority', 0.0001,  0.5, 'Fomorian king whose death-eye held a host; the tyrant-eye his grandson closes at Moytura.', 'Fomorian king', ['macculloch-religion-ancient-celts-1911.txt']),
    'manannan':       ('P_authority', 0.00005, 0.5, 'Sea-lord named in the euhemerist lists; the otherworld ferryman-king.', 'Sea-lord', ['macculloch-religion-ancient-celts-1911.txt']),
    'hel':            ('P_authority', 0.00005, 1.0, 'Half-dead ruler of the ninth world and its low house; the underworld throne Odin granted her.', 'Ruler of the ninth world', ['poeticedda00belluoft_djvu.txt']),
    'nithuths-queen': ('P_authority', 0.00005, 1.0, 'The queen who reads the ring and commands the hamstringing; the instigating throne beside Nithuth.', 'Queen beside the throne', ['poeticedda00belluoft_djvu.txt']),
}
for nid, (pool, share, wit, why, role, files) in TIER2.items():
    if nid in C['direct']:
        continue
    C['direct'][nid] = {'pool': pool, 'share': share, 'witness': wit, 'why': why,
                        'role': role, 'witness_files': files, 'ruled': RULED}

# --- 3. dead-route targets: price so the 7 explicit routes activate under R6 ---
# repair: the first pass wrote 'paris'; the graph node is 'paris-alexandrus'
if 'paris' in C['direct']:
    C['direct']['paris-alexandrus'] = C['direct'].pop('paris')
TARGETS = {
    'apollo':  ('P_health',   0.02,    0.75, 'The archer whose arrows are plague and whose son is Asclepius; the healing claim the Pythian voice disciplined. Pricing activates the sibyl and Sulla routes.', ['virgil-aeneid-dryden.txt', 'serviusaeneid.txt']),
    'mercury': ('P_authority', 0.0002, 0.5, 'God of merchants and messengers; the exchange-coordination archetype the market still invokes. Pricing activates the Adam Smith route.', ['eb1911-adam-smith.txt', 'boswell-life-of-johnson-vol2.txt']),
    'paris-alexandrus': ('P_authority', 0.00005, 1.0, 'The judgment of the apple: the binding decision among the bribes of three goddesses that launched the war. Pricing activates the Hector route.', ['plutarch-lives-dryden-clough-gutenberg.txt']),
    'atlas':   ('P_energy',   0.0001, 0.75, 'The sky-bearer; every atlas of maps and every load-bearing name descends from the Titan condemned to carry. Pricing activates the Iopas route.', ['virgil-aeneid-dryden.txt']),
}
for nid, (pool, share, wit, why, files) in TARGETS.items():
    if nid in C['direct']:
        continue
    C['direct'][nid] = {'pool': pool, 'share': share, 'witness': wit, 'why': why,
                        'witness_files': files, 'ruled': RULED}

# --- 4. rulings log (idempotent: one entry per ruling text) ---
if not any(r.get('ruling', '').startswith("Cobe: 'Do power scaling") for r in C.get('rulings', [])):
    C.setdefault('rulings', []).append({
        'date': RULED,
        'ruling': "Cobe: 'Do power scaling for all the ones awaiting'",
        'applied': '21 Tier-1 proposals promoted to direct; 13 Tier-2 role-attested '
                   'figures priced (epic command earns claims); 4 dead-route targets priced '
                   '(apollo, mercury, paris-alexandrus, atlas) activating all 7 explicit '
                   'dead routes under R6 single-hop.',
        'rescalable': 'Every line individually rescalable; name a node and a new share.'})
C['updated'] = RULED

json.dump(C, open(P, 'w'), indent=1, ensure_ascii=False)
print(f"promoted {promoted} Tier-1; added {len(TIER2)} Tier-2 + {len(TARGETS)} targets; "
      f"direct now holds {len(C['direct'])} claims; proposals pending: {len(C['proposals'])}")
