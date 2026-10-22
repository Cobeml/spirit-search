"""Post the power-gate overhaul report + rebuilt site HTML to the spirit-search thread (2026-10-21)."""
import json, os, urllib.request, urllib.error, uuid

TOKEN = None
for line in open(os.path.expanduser('~/.hermes/.env')):
    if line.strip().startswith('DISCORD_BOT_TOKEN='):
        TOKEN = line.strip().split('=', 1)[1].strip().strip('"').strip("'")
assert TOKEN, 'no DISCORD_BOT_TOKEN in hermes env'
CHANNEL = '1562619411972759553'  # thread: Knox 0 W
UA = 'DiscordBot (https://github.com/discord/discord-api-docs, 10)'
HTML = '/home/cobe-liu/Developing/spirit-search/docs/index.html'

MSG1 = (
"**Knox at 0 W - what happened**\n"
"He entered in the Weems cabinet wave (10-14) noted \"power unpriced pending Cobe's gate\", and three "
"defects hid that state:\n"
"- No pool claim existed, and his only edge (washington->knox, interaction, influence 0) routes power the "
"wrong way to reach him: the *from* node collects, so nothing ever arrived.\n"
"- The UI printed \"0 W\": a verdict, not a gate state.\n"
"- The site was also serving stale power fields: themis, cronos, rhea, iapetus and sarpedon shipped 0 W "
"because growth waves never reran the power model.\n\n"
"**Similar oversights (144 of 200 nodes read unpriced):**\n"
"- Knox-class documented office-holders at 0: Hamilton, Jefferson, Jay, Burr, Wilson, Arnold, Lee, "
"Braddock, Newton, Faraday, Cincinnatus, Sulla, Romulus, Numa, Fabius, Marcellus, Coriolanus, "
"Aemilius Paullus, Cato, Publicola\n"
"- 7 dead influence routes: explicit fractions delivering 0 W because the target carries no direct power "
"(ampere->faraday 0.3, adam-smith->mercury 0.3, sulla->apollo 0.3, sibyl->apollo 0.3, hector->paris 0.3, "
"iopas->atlas 0.2, heimdall->odin 0.1)\n"
"- 11 unreviewed inheritances: the 0.2 kinship default into priced gods routes terawatts nobody ruled; "
"Sarpedon (one Iliad arc) sat at 1.5 TW, ~8000x Washington\n"
"- the era curve was ~6x over at 1800, ~2x under at -750\n\n"
"**Overhaul shipped (methodology only, no share touched):**\n"
"- claims as data in research/power_claims.json (pools, direct, influence, pop anchors, proposals); "
"graph.json power fields are model output, never hand-edited\n"
"- power_status per node: 22 direct / 34 routed / 144 unpriced; the site renders \"unpriced\" instead of "
"\"0 W\" (tooltip + panel, gate explanation one click in)\n"
"- era scaling re-anchored to cited population estimates; standing gate audit research/_audit_power.py "
"in the wave chain (proposals, roles, dead routes, inheritances, staleness). No wave ships an "
"office-holder at a silent 0 again. Rebuilt, browser-verified, pushed. Full site attached."
)

MSG2 = (
"**Tier-1 proposals awaiting your ruling** (pool x share x witness -> watts if ruled):\n"
"- faraday P_energy 0.01x0.5 -> 100 GW\n"
"- newton P_energy 0.002x0.5 -> 20 GW (P_metals via the Mint is the alternative)\n"
"- hamilton P_nation 0.02x0.5 -> 12 GW\n"
"- romulus P_authority 0.0005x1.0 -> 7.5 GW\n"
"- cincinnatus P_authority 0.0005x0.75 -> 5.6 GW\n"
"- sulla P_authority 0.0005x0.75 -> 5.6 GW\n"
"- numa P_authority 0.0003x1.0 -> 4.5 GW\n"
"- jefferson P_nation 0.005x0.5 -> 3 GW\n"
"- cato P_authority 0.0002x0.75 -> 2.25 GW\n"
"- wilson P_authority 0.0002x0.5 -> 1.5 GW\n"
"- publicola P_authority 0.0001x1.0 -> 1.5 GW\n"
"- jay P_nation 0.0005x0.5 -> 300 MW\n"
"- knox P_military 0.01x0.5 -> 250 MW (artillery branch + the War Department; Weems witness)\n"
"- burr P_nation 0.0002x0.5 -> 120 MW\n"
"- fabius P_military 0.001x1.0 -> 50 MW\n"
"- arnold P_military 0.0005x0.5 -> 12.5 MW\n"
"- marcellus 10 MW, aemilius-paullus 10 MW, coriolanus 7.5 MW, charles-lee 5 MW, braddock 5 MW (P_military)\n\n"
"Shares are order-of-magnitude anchors calibrated to your ruled table (Washington 0.15 P_nation, Mars 0.05 "
"P_military, Watt 0.01 P_energy). Name the lines you accept, rescale or reject; they go into "
"power_claims.json.direct and the next model run prices them.\n\n"
"**Doctrine call (Tier-2):** 13 role-attested figures sit unpriced with no proposal because their command "
"is epic or mythic, not flesh record: agamemnon (leader of the host), priam, aeneas, evander, latinus, odin, "
"math, maelgwn, nuada, balor, manannan, hel, nithuth's queen. Does epic command earn pool claims, or is "
"unpriced the honest label?\n\n"
"Also open: the 7 dead routes. Price their targets (apollo, mercury, odin, faraday, paris) or re-aim the "
"fractions."
)


def post(payload, filepath=None):
    boundary = uuid.uuid4().hex
    body = b''
    for k, v in payload.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    if filepath:
        fn = os.path.basename(filepath)
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="files[0]"; filename="{fn}"\r\n'
                 f'Content-Type: text/html\r\n\r\n').encode()
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


s1, id1 = post({'content': MSG1}, HTML)
print('msg1 (report + site html):', s1, id1)
s2, id2 = post({'content': MSG2})
print('msg2 (proposals):', s2, id2)
