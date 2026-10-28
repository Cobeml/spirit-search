"""Post the round-2 report (pricing applied + neighborhood expansion) to the commissioning thread."""
import json, os, urllib.request, urllib.error, uuid

TOKEN = None
for line in open(os.path.expanduser('~/.hermes/.env')):
    if line.strip().startswith('DISCORD_BOT_TOKEN='):
        TOKEN = line.strip().split('=', 1)[1].strip().strip('"').strip("'")
assert TOKEN, 'no DISCORD_BOT_TOKEN'
CHANNEL = '1564437497793085442'   # thread: Add Jesus and God...
UA = 'DiscordBot (https://github.com/discord/discord-api-docs, 10)'
HTML = '/home/cobe-liu/Developing/spirit-search/docs/index.html'

MSG1 = (
"**Round 2: priced and expanded. 208 nodes, 256 edges. Site attached.**\n\n"
"Watt pricing applied per your ruling, one entry in power_claims.json.rulings:\n"
"- god P_authority 0.0001 x w 1.0 = **1.5 GW direct**\n"
"- jesus P_health 0.00005 x w 1.0 = **5.0 MW direct**\n"
"- 62 direct / 36 routed / 110 unpriced; claims_sha fresh; 0 dead routes. "
"Name a node and a share and either line rescales.\n\n"
"Edge expansion: six neighbor nodes from the on-disk witnesses, all "
"review-tagged (clear any by naming it):\n"
"- **Pontius Pilate** (era 93): the Matt 27 delivery, the Josephus "
"condemnation, the Tacitus procurator title, the hand-washing\n"
"- **Tiberius** (93): the Tacitus reign sentence, Luke 3:1, Josephus routing "
"the Aretas war orders\n"
"- **Herod Antipas** (93): the Luke 23 audience with the silent prisoner, "
"the Matt 14 risen-John rumor, Josephus 18.5.2's security killing\n"
"- **John the Baptist** (93): Matt 3:1, the Jordan baptism, Josephus's "
"prisoner 'called the Baptist'\n"
"- **Moses** (93): the bush, the commission and the refusal, Josephus's "
"lawgiver, the transfiguration\n"
"- **Mary** (1611): the annunciation, Matt 1:18, the Magnificat, Luke 2:19; "
"Josephus prints no 'Mary', so the KJV document year stands\n\n"
"12 new edges, first-hit distances 16-532, all inside the 600-char window:\n"
"- jesus gains pilate, tiberius, herod, john, moses (the transfiguration, "
"typed transmission) and mary (kinship)\n"
"- god gains moses ('Moses, Moses' at the bush) and mary ('found favour "
"with God')\n"
"- Rome: tiberius->pilate and tiberius->herod agency (Luke 3:1 names all "
"three), pilate->herod jurisdiction transfer\n"
"- herod->john conflict: 'out of Herod's suspicious temper... put to death' "
"(Josephus)\n"
"- mary->jesus and moses->jesus carry explicit 0.0 influence; nothing "
"silently routes 20% when the office-holders get priced.\n\n"
"Gates: relevance 0 first-card failures / 0 seg / 0 junk; thin audit 208/208 "
"tier-3; wiki table audited: Pilate, Moses, Mary mother of Jesus, "
"Tiberius, Herod Antipas, John the Baptist, all with lead images.")

MSG2 = (
"Four office-holder proposals sit in Tier-1 awaiting your next ruling:\n"
"- tiberius P_authority 0.0002 -> 3.00 GW (the emperor)\n"
"- moses P_authority 0.00005 -> 750 MW (the Exodus host command)\n"
"- herod-antipas P_authority 0.00001 -> 150 MW (tetrarch of Galilee)\n"
"- pontius-pilate P_authority 0.000005 -> 75 MW (prefect of Judaea)\n"
"Mary and John the Baptist hold no office in the witnesses; no proposal "
"filed, they stay unpriced.\n\n"
"Corpus search: the round-1 witnesses are indexed and queryable ('pilate' "
"hits the NT trial chunks, 'Moses deemed' hits Josephus). The Pliny letter "
"was saved as .html, which the builder skips; extracted it to .txt and a "
"rebuild is running (~35-60 min) so the 'hymn to Christ' passage becomes "
"searchable.\n\n"
"Next candidates the fetched corpus already names: Elias (the "
"transfiguration window carries him), Caiaphas (the chief priests of "
"Matt 27), Peter (the denial closing Matt 26), the centurion at the cross. "
"Deeper ones (Paul, the Acts material) need new fetches.")

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

print('msg1 len', len(MSG1), '| msg2 len', len(MSG2))
s, mid = post({'content': MSG1}, HTML)
print('round-2 report part 1 posted:', s, mid)
s, mid = post({'content': MSG2})
print('round-2 report part 2 posted:', s, mid)
