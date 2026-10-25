"""Post the queue-work progress report + rebuilt site to the spirit-search thread (2026-10-21)."""
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
"**Queue worked, top to bottom. All 200 nodes now fully fleshed**: 0 stubs, 0 one-card-thin, 0 edge-debt.\n\n"
"Per node:\n"
"- 20 essays from the on-disk witnesses. Hamilton and Arnold (Weems: the roster, the 'gigantic genius' "
"passage, the Monmouth record); Numa, Romulus, Cato (Plutarch + NEW source Livy Book 1, sliced "
"programmatically); the eight Irish gods (MacCulloch: Diancecht's silver hand, "
"Goibniu's never-failing spears, Dagda's 'good hand', Brigit's poets, Miach's 365 herbs, Manannan's "
"immortality gift, the Morrigan's scald-crow triad, Balor's eye); the Welsh four (Guest: Math's "
"footholder law, Dylan baptized into the wave, Aranrod's wand test, Maelgwn's Dyganwy court); the Titans "
"(Evelyn-White: Tethys' rivers, Theia's sun-moon-dawn, Crius and Eurybia).\n"
"- fdr repaired: his witness never named him. Replaced with the full Avalon page, [45]'s quotes re-sliced "
"to it, two Wikipedia thumb-captions the wiki layer had misattached to the source dropped, and the "
"document header pinned as his naming first card; 'fear itself' stays second.\n\n"
"Pipeline repairs surfaced on the way (shipped, unit tests green):\n"
"- The 2026-10-16 boundary overhaul had a gap: 'me.\" — And' (period, quote, em dash) defeated sentence "
"detection, so every Weems cabinet pin walked back into Washington's speech. Fixed; Knox, Hamilton, "
"Jefferson, Wilson and Jay now pin the clean 'crazy ship at sea' roster window.\n"
"- expand_span returned an empty span when an anchor sat exactly at a sentence start; guarded.\n"
"- Two furniture cards dropped (a Jastrow scan-cover on Gilgamesh, an IA strip on Weems), Adam's "
"mid-sentence card re-sliced, cupid re-anchored to 'But Cupid being now healed of his wound'.\n\n"
"Gate: 0 first-cards failing the name rule, 0 segmentation, 0 junk. Miach carries a thin-witness note: "
"two MacCulloch passages are his whole record. Power untouched (60 direct / 36 routed / 104 unpriced). "
"Rebuilt, browser-verified, pushed. Site attached.\n\n"
"Thin queue empty; next growth is candidate enumeration off _queue.json."
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
print('queue-work report posted:', s, mid)
