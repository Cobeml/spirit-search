"""Post the v3 pilot calibration to the commissioning thread (attaches the pilot JSON)."""
import json, os, urllib.request, urllib.error, uuid

TOKEN = None
for line in open(os.path.expanduser('~/.hermes/.env')):
    if line.strip().startswith('DISCORD_BOT_TOKEN='):
        TOKEN = line.strip().split('=', 1)[1].strip().strip('"').strip("'")
assert TOKEN, 'no DISCORD_BOT_TOKEN'
CHANNEL = '1564437497793085442'
UA = 'DiscordBot (https://github.com/discord/discord-api-docs, 10)'
DATA = '/home/cobe-liu/Developing/spirit-search/research/power_v3_pilot.json'

MSG1 = (
"**v3 pilot: 14 nodes, two ledgers, typed transfers. Data attached (power_v3_pilot.json).**\n\n"
"Applied per your rulings: virtual = highest attested feat with the physics computed, "
"no cap, peak and sustained both recorded; physical = component inventory "
"(human/weapons/tools/resources/capital/finance, absent classes recorded); static "
"holds 0 W; transfers typed per pool with conservation and multi-hop.\n\n"
"Calibration, v2 -> v3 (physical | virtual):\n"
"- zeus 7.52 TW -> virt **1.02 EW** (theomachy: land and sea seethed, thermal bound)\n"
"- god 1.50 GW -> virt **2.07 EW** (deluge) + phys 272.9 MW received\n"
"- inana 300 GW -> virt **30.1 TW** (Mount Ebih fractured, 10 km3 at 1e5 J/kg)\n"
"- thor 0 W -> virt **26.7 TW** serpent-lift, or 23 kW for the blow total\n"
"- poseidon 0 W -> virt 1.67 TW (storm laid flat); jesus 5 MW -> virt 1.67 TW "
"(storm calmed: same kinetic class, so the two traditions read equal here)\n"
"- prometheus 14.25 TW -> virt 10 MW (torch); heracles 3.75 GW -> virt 59 MW "
"(Augean diversion)\n"
"- apollo 7.50 GW -> virt 10 kW (Python); the plague reported undefined\n"
"- atlas 376.5 GW -> virt 0 W sustained (5.05e19 J to raise the sky 1 m)\n"
"- washington 180 GW -> phys 46 MW; sulla 6.08 GW -> phys 600 MW\n"
"- constantine (new) -> phys 9.10 GW; croesus (new) -> phys 300 MW\n\n"
"Transfers: constantine->god phys 3% = 272.9 MW; god->jesus phys 30% of received = "
"81.9 MW (your clarification's case: physical pool only, multi-hop, conservation "
"checked); croesus->apollo phys 10% = 30 MW (the Delphi dedications, Herodotus "
"1.50-51); zeus->heracles virt 20% = 203.7 PW.")

MSG2 = (
"Five items before the wave migration:\n"
"1. Feat-reading spread: Thor reads 23 kW for the narrated blow total vs 26.7 TW "
"for lifting the world-serpent. Report the pair with the largest act as the "
"headline (recommended) or pin one convention?\n"
"2. Undefined-class feats (creation ex nihilo, resurrection, Apollo's plague): "
"reported 'undefined' with the reason and no number. Show a symbolic row or leave "
"unlisted?\n"
"3. Weapons and resources: currently folded into the 15 kW/soldier coefficient. "
"Proposal: explicit rows wherever the witness documents them (artillery batteries, "
"fleets, engines) plus resource rows (lands, mines, oil) in the wave pass.\n"
"4. Transfer shares are proposals: constantine->god 3% of the fisc, god->jesus 30% "
"of received, croesus->apollo 10% of the treasure, zeus->heracles 20% virt. Ruling "
"or rescale; sum of outbound fractions <= 1 per pool is enforced.\n"
"5. Witness gaps for the wave pass: Washington's peak command (Weems documents the "
"low, 'not 3000 men'), Croesus's host and mint, Constantine's establishment "
"(Gibbon's 583,000-645,000 range). OK to fetch EB1911 Washington and a Lydian "
"source?\n\n"
"No graph writes yet: the pilot is a data file. On your word I freeze the wave plan "
"and run the 14-node wave into graph.json with the v3 fields beside the frozen v2 "
"numbers, then flip the site lens once you accept the table.")


def post(payload, filepath=None):
    boundary = uuid.uuid4().hex
    body = b''
    for k, v in payload.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    if filepath:
        fn = os.path.basename(filepath)
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="files[0]"; filename="{fn}"\r\n'
                 f'Content-Type: application/json\r\n\r\n').encode()
        body += open(filepath, 'rb').read() + b'\r\n'
    body += f'--{boundary}--\r\n'.encode()
    req = urllib.request.Request(
        f'https://discord.com/api/v10/channels/{CHANNEL}/messages', data=body,
        headers={'Authorization': f'Bot {TOKEN}', 'User-Agent': UA,
                 'Content-Type': f'multipart/form-data; boundary={boundary}'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode()).get('id')
    except urllib.error.HTTPError as e:
        print('HTTP', e.code, e.read().decode()[:400])
        raise


print('lens', len(MSG1), len(MSG2))
s, mid = post({'content': MSG1}, DATA)
print('v3 pilot part 1 posted:', s, mid)
s, mid = post({'content': MSG2})
print('v3 pilot part 2 posted:', s, mid)
