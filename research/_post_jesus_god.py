"""Post the jesus+god batch report + rebuilt site to the commissioning thread (2026-10-27)."""
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
"**Jesus and God added. 202 nodes, 244 edges. Site attached.**\n\n"
"Both nodes sit at era 93: Josephus's Antiquities (93/94 CE, Whiston text, "
"fetched to evidence/jesus/) is the earliest fetched witness naming each; "
"the KJV enters the year table at 1611 as a document (the convention settled "
"with [18] Isaiah). Dating the Old Testament content to the Torah's redaction "
"would move God to about -450: a one-line re-rule.\n\n"
"Witnesses: the full KJV (#10) was already on disk under the lilith cluster; "
"split into Genesis-Exodus [317] and New Testament [318] section files, "
"Gutenberg verse prefixes stripped per the [18] quote convention. New "
"fetches: Josephus [319], Tacitus Annals 15.44 (Church/Brodribb, MIT) [320], "
"Pliny 10.96 (Georgetown text) [321]. Franklin's Autobiography [40] was cited "
"but never on disk; restored from Gutenberg #20203, so his evidence chain now "
"verifies against a file.\n\n"
"15 edges, every excerpt naming both endpoints in-window (distances 13-277):\n"
"- Genesis cluster x10 via [317]: adam (creation), eve, cain, abel, noah, "
"abraham, isaac, jacob, joseph, enoch\n"
"- lilith via Ginzberg [19]: 'God sent forth three angels' (conflict)\n"
"- jesus via Mark 1:1 [318] (kinship)\n"
"- washington via Weems [15]: the 'Jehovah, the God of Hosts, was with him' "
"window\n"
"- franklin via [40]: the parents' epitaph, 'with God's blessing ... "
"distrust not Providence'\n"
"- fdr via [45], two_sided pairing, review-tagged: the close asks God's "
"blessing, the Avalon header names him\n\n"
"Gates: relevance 0 first-card failures, 0 seg, 0 junk; thin audit 202/202 "
"tier-3; power claims_sha fresh, 0 dead routes. Explicit 0.0 influence on "
"all 15 edges, so nothing silently routes 20% when you price God.")

MSG2 = (
"Power proposals sitting in the Tier-1 gate report for your ruling: god "
"P_authority share 0.0001 -> 1.5 GW (witness 1.0: KJV + Josephus + Ginzberg + "
"the invocations); jesus P_health 0.00005 -> 5 MW (the healing record; an "
"authority share on 'All power is given unto me' is the alternative). Both "
"render unpriced on the site until you rule. Name a node and a share and "
"I'll apply it.\n\n"
"Held for your salience gate:\n"
"- New-node candidates inside the witnesses: Pontius Pilate (named by "
"Tacitus, Josephus and the gospels), Tiberius, Trajan, Herod, Mary, Moses.\n"
"- jesus|baldr analogy: no on-disk witness names both within 600 chars. "
"Frazer's Balder the Beautiful names Christ 13x but never in a Balder "
"window; option is fetching a pairing witness (the 1911 Britannica Balder "
"article).\n"
"- god|methuselah: the only co-occurrence is the genealogy line (Enoch walks "
"with God after begetting him); no direct interaction, so not added.\n"
"- god|genius: City of God 7.13 pairs 'Genius' and 'God', but that God is "
"Varro's world-soul, Jupiter; adding it would misattribute.\n\n"
"Corpus search index is rebuilding in the background (~35-60 min); the "
"search bar covers the new witnesses once it lands. The long-form qmd still "
"carries no per-node sections for queue-era additions; profiles can be "
"written there whenever you gate them.")

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

print('msg1 len', len(MSG1), 'msg2 len', len(MSG2))
s, mid = post({'content': MSG1}, HTML)
print('report part 1 posted:', s, mid)
s, mid = post({'content': MSG2})
print('report part 2 posted:', s, mid)
