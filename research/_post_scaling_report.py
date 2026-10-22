"""Post the applied power-scaling report + rebuilt site to the spirit-search thread (2026-10-21)."""
import json, os, urllib.request, urllib.error, uuid

TOKEN = None
for line in open(os.path.expanduser('~/.hermes/.env')):
    if line.strip().startswith('DISCORD_BOT_TOKEN='):
        TOKEN = line.strip().split('=', 1)[1].strip().strip('"').strip("'")
assert TOKEN, 'no DISCORD_BOT_TOKEN'
CHANNEL = '1562619411972759553'
UA = 'DiscordBot (https://github.com/discord/discord-api-docs, 10)'
HTML = '/home/cobe-liu/Developing/spirit-search/docs/index.html'

MSG = (
"**Power scaling applied per your ruling: every awaiting line is priced.** 96 nodes now carry watts "
"(60 direct / 36 routed; the 104 remaining unpriced have no command role and no pool claim).\n\n"
"Applied as proposed (pool x share x witness -> direct watts):\n"
"- faraday P_energy 0.01x0.5 -> 100 GW (total 120 GW with the Franklin route; Ampere now routes 30 GW)\n"
"- newton 20 GW\n"
"- hamilton 12 GW\n"
"- odin P_authority 0.0005x1.0 -> 7.5 GW (Heimdall now routes 750 MW)\n"
"- romulus 7.5 GW\n"
"- sulla 5.6 GW + 450 MW via the activated Apollo route\n"
"- cincinnatus 5.6 GW\n"
"- numa 4.5 GW\n"
"- jefferson 3 GW\n"
"- cato 2.2 GW\n"
"- paris-alexandrus 750 MW direct, 2.2 GW total (Hector now routes 225 MW)\n"
"- wilson 1.5 GW, publicola 1.5 GW, aeneas 1.5 GW, priam 1.5 GW, math 1.5 GW, nuada 1.5 GW\n"
"- apollo P_health 0.02x0.75 -> 1.5 GW direct, 7.5 GW total with the Asclepius kinship (Sibyl now routes 450 MW)\n"
"- mercury 1.5 GW direct, 19.5 GW total with the Capitol rent (Adam Smith now routes 450 MW)\n"
"- atlas P_energy 1.5 GW direct, 376.5 GW total (Iopas now routes 300 MW)\n"
"- latinus 1.1 GW\n"
"- nithuths-queen, evander, maelgwn, balor, hel 750 MW each; manannan 375 MW\n"
"- jay 300 MW\n"
"- knox P_military 0.01x0.5 -> 250 MW (artillery branch + War Department)\n"
"- burr 120 MW\n"
"- fabius 50 MW\n"
"- arnold 12.5 MW\n"
"- marcellus 10 MW, aemilius-paullus 10 MW, coriolanus 7.5 MW, agamemnon 5 MW, charles-lee 5 MW, braddock 5 MW\n\n"
"Epic and mythic command priced under your scaling directive at small shares: Agamemnon's host at 5 MW "
"against Fabius' staff-college doctrine at 50 MW, the Welsh and Tuatha thrones at 375-750 MW.\n\n"
"All 7 dead routes now flow; gate audit reads clean (0 awaiting, 0 dead routes, claims fresh). The 11 "
"default kinship inheritances (Sarpedon 1.5 TW and kin) stay flagged for per-line ruling. Any node: name "
"it and a share and I rescale. Ruling logged in power_claims.json; site rebuilt and attached."
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


s, mid = post({'content': MSG}, HTML)
print('scaling report posted:', s, mid)
