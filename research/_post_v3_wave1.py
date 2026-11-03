"""Post the v3 wave-1 report (rulings applied, 14 ledgers live beside v2) to the thread."""
import json, os, urllib.request, urllib.error, uuid

TOKEN = None
for line in open(os.path.expanduser('~/.hermes/.env')):
    if line.strip().startswith('DISCORD_BOT_TOKEN='):
        TOKEN = line.strip().split('=', 1)[1].strip().strip('"').strip("'")
assert TOKEN, 'no DISCORD_BOT_TOKEN'
CHANNEL = '1564437497793085442'
UA = 'DiscordBot (https://github.com/discord/discord-api-docs, 10)'

MSG1 = (
"**Wave 1 shipped: 14 nodes carry v3 ledgers beside the frozen v2 numbers, 210 nodes / "
"258 edges. All five rulings applied.**\n\n"
"Creative physics, adopted where I agree it holds:\n"
"- creation ex nihilo: E = mc2 for the earth as narrated, divided by the account's own "
"six days = **1.04e36 W** (red-flagged; the witness supplies the duration)\n"
"- resurrection: traversable wormhole, exotic matter c^4/G x b for a 1 m throat, one-"
"second act = **1.21e44 W** (red-flagged; the Landauer information bound, 3.0 GJ, stays "
"in the row for contrast)\n"
"- Apollo's plague: pathogen host-drain at peak, 20,000 stricken bodies = **400 kW**, "
"which is the honest size of the archer god's terror\n"
"Both flagged entries carry the full reasoning in their v3 block for the panel.\n\n"
"Pairs report headline-first: thor **26.7 TW** serpent-lift with the 23 kW blow total "
"in the row; zeus 1.02 EW keeping the 33 TW bolt; jesus 1.21e44 W keeping the storm at "
"1.67 TW.\n\n"
"Edges now typed: 256 stamped **symbiotic** (mutual reinforcement, no pool draw), 2 "
"**parasitic** transfers added: constantine->god 3% of his 9.10 GW = **273 MW** of real "
"power reaching God, croesus->apollo 10% of 300 MW = **30 MW** (the Delphi dedications). "
"The god->jesus physical re-transmission (30% of what God received = 82 MW) is proposed "
"on the existing kinship edge; say the word and it goes parasitic.")

MSG2 = (
"constantine and croesus are real nodes now: cards, essays, wiki pages, and Tier-1 "
"pricing proposals (3.0 GW each for the two emperors, 300 MW for the Lydian). Six "
"proposals await your gate: tiberius, constantine, moses, croesus, herod-antipas, "
"pontius-pilate.\n\n"
"Two findings from the extract work:\n"
"- The documented window for real power reaching God is Gibbon's edict passage: 'a "
"secret and sincere reverence for the name of Christ, and for the God of the "
"Christians', next to the repeal of the persecution edicts. The 3% fisc share is an "
"estimate; the mechanism (endowments, exemptions, enforcement) is documented.\n"
"- Croesus's era lands at -560 from EB1911's own dating ('last king of Lydia, of the "
"Mermnad dynasty, 560-546 B.C.'), which puts the oldest documented real-to-temple "
"transfer in the graph in the sixth century BC.\n\n"
"Gates: relevance 0 first-card failures / 0 seg / 0 junk; power claims fresh; wiki "
"resolved for both new nodes. The site still renders the v2 lens; the v3 fields sit in "
"graph.json waiting for your read of the table. Accept and I flip the lens, then run "
"the remaining 196 nodes in waves of twenty.")
