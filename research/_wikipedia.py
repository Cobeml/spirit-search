#!/usr/bin/env python3
"""Fetch per-node Wikipedia summaries -> research/wikipedia.json (Cobe 2026-10-21).

Wikipedia is a source for ALL nodes: the node panel name links to the
en.wikipedia page and the lead blurb renders before the corpus highlights.
Doctrine: the blurb is CONTEXT, not evidence. A highlight or edge is never
substantiated by Wikipedia; it still requires a verbatim quote from a
corpus-worthy witness. Wikipedia surfaces candidate connections in future
discovery rounds; every candidate still passes corpus substantiation.

Idempotent: resolved nodes are cached; unresolved ones retry each run.
Re-run after growth waves to cover new nodes. Never import this file (it is
a script); run it as a process. Output keyed by node id:
  {status:'ok', title, url, blurb, description, via, checked}
  {status:'unresolved', via, checked}
  {status:'none', reason, checked}   (explicit OVERRIDES[nid] = None)
"""
import json, os, re, time, unicodedata, urllib.error, urllib.parse, urllib.request

ROOT = '/home/cobe-liu/Developing/spirit-search'
OUT = ROOT + '/research/wikipedia.json'
UA = 'spirit-search/1.0 (https://github.com/Cobeml/spirit-search; research graph)'
PAUSE = 0.12

# tradition strings meaning historic person -> plain-title search first;
# everything else (deities, heroes, tale figures) gets the 'mythology' bias
FLESH_MARKERS = ('flesh record', 'biographer', 'artist 1865', 'manufactory',
                 'Royal Society', 'Royal Institution', 'French physics',
                 'brewing physics', 'physician of record',
                 'physician of the empire', 'statesman', 'Roman exemplar',
                 'Roman dictator', 'American national cult')

# node id -> exact en.wikipedia title (bypasses search + validation).
# Spelling mismatches: Guest's Mabinogion names, Bellows' Edda spellings,
# ambiguous plain names, and parent-work pages for tale-internal figures.
OVERRIDES = {
    # transliteration / spelling mismatches (Guest, Bellows, Evelyn-White-era sources)
    'manawyddan': 'Manawydan',
    'bran': 'Br\u00e2n the Blessed',
    'aranrod': 'Aranrhod',
    'llew-llaw-gyffes': 'Lleu Llaw Gyffes',
    'guthrun': 'Gu\u00f0r\u00fan Gj\u00fakad\u00f3ttir',
    'volundr': 'Wayland the Smith',
    'cronos': 'Cronus',
    'typhoeus': 'Typhon',
    'inana': 'Inanna',
    # ambiguous plain names / wrong primary topic
    'james-wilson': 'James Wilson (Founding Father)',
    'charles-lee': 'Charles Lee (general)',
    'marcellus': 'Marcus Claudius Marcellus',
    'marcius-coriolanus': 'Gaius Marcius Coriolanus',
    'helen': 'Helen of Troy',
    'odysseus': 'Odysseus',
    'dionysus': 'Dionysus',
    'loki': 'Loki',
    'pandora': 'Pandora',
    'pyrrha': 'Pyrrha',
    'asclepius': 'Asclepius',
    'ajax-telamonian': 'Ajax the Great',
    'cupid': 'Cupid',
    'abraham': 'Abraham',
    'isaac': 'Isaac',
    'jacob': 'Jacob',
    'joseph': 'Joseph (Genesis)',
    'enoch': 'Enoch',
    'eve': 'Eve',
    'llwyd': 'Llwyd ap Cil Coed',
    'maelgwn': 'Maelgwn Gwynedd',
    'math': 'Math fab Mathonwy',
    'atli': 'Attila',
    # search otherwise lands on a set-index or wrong-domain page
    'asteria': 'Asteria (Titaness)',
    'dione': 'Dione (Titaness)',
    'hyperion': 'Hyperion (Titan)',
    'phoebe': 'Phoebe (Titaness)',
    'ceto': 'Ceto',
    # tale-internal figures -> parent-work page (2026-10-21 audit)
    'nathanael': 'The Sandman (short story)',
    'olympia': 'The Sandman (short story)',
    'bothvild': 'B\u00f6\u00f0vildr',
    'nithuth': 'Ni\u00f0had',
    'anzud-bird': 'Anz\u00fb (mythology)',
    'eurypylus-telephid': 'Eurypylus (son of Telephus)',
}
OVERRIDES = {k: v for k, v in OVERRIDES.items() if v is not None}

# nodes with genuinely no standalone en.wikipedia article -> status 'none'
NONE = {
    'agrimus': "aggadic angel-prince named only in Ginzberg's Legends of the Jews",
    'nithuths-queen': "unnamed antagonist in Volundarkvitha; no standalone article",
}


def norm(s):
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', s.lower())


def core_label(label):
    t = label.split('(')[0]
    t = re.split(r'\s*/\s*', t)[0]
    t = t.split(' & ')[0]
    t = t.strip(' ,')
    if t.lower().startswith('the '):
        t = t[4:]
    return t.strip()


def json_get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def search_titles(q, n=6):
    d = json_get('https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode({
        'action': 'query', 'list': 'search', 'srsearch': q,
        'srlimit': n, 'srnamespace': 0, 'format': 'json'}))
    time.sleep(PAUSE)
    if not d or 'query' not in d:
        return []
    return [h['title'] for h in d['query'].get('search', [])]


def summary(title):
    url = ('https://en.wikipedia.org/api/rest_v1/page/summary/'
           + urllib.parse.quote(title.replace(' ', '_'), safe=''))
    s = json_get(url)
    time.sleep(PAUSE)
    return s


def trim_blurb(t, cap=760):
    if not t:
        return t
    if len(t) <= cap:
        return t
    cut = t.rfind('. ', 0, cap)
    return t[:cut + 1] if cut > 200 else t[:cap].rsplit(' ', 1)[0] + '\u2026'


def validates(node, s):
    if not s:
        return False
    if s.get('type') == 'disambiguation':
        return False
    first = core_label(node['label']).split()
    key = norm(first[0]) if first else ''
    if not key:
        return False
    hay = norm(' '.join([s.get('title') or '', s.get('description') or '',
                         s.get('extract') or '']))
    return key in hay


def ok_entry(s, via):
    return {'status': 'ok',
            'title': s.get('title'),
            'url': (s.get('content_urls') or {}).get('desktop', {}).get('page'),
            'blurb': trim_blurb(s.get('extract')),
            'description': s.get('description'),
            'thumb': ((s.get('thumbnail') or {}).get('source')),
            'via': via,
            'checked': time.strftime('%Y-%m-%d')}


def img_ext(url):
    low = (url or '').lower()
    if '.png' in low:
        return '.png'
    if '.webp' in low:
        return '.webp'
    if '.gif' in low:
        return '.gif'
    return '.jpg'


def looks_image(b):
    return (b[:2] == b'\xff\xd8' or b[:8] == b'\x89PNG\r\n\x1a\n'
            or (b[:4] == b'RIFF' and b[8:12] == b'WEBP')
            or b[:4] == b'GIF8')


def download_images(cache):
    """Save each node's Wikipedia lead thumbnail to docs/img/<id>.<ext>.

    Local files, not runtime CDN fetches: the site stays offline-first and
    the posted single HTML file degrades gracefully (missing images fall
    back to the plain sphere via onerror). Idempotent: existing files are
    kept. Every saved file is magic-byte checked (impostor-page doctrine).
    """
    d = ROOT + '/docs/img'
    os.makedirs(d, exist_ok=True)
    fetched = have = noimg = 0
    for nid, e in cache.items():
        if e.get('status') != 'ok':
            e['img'] = None
            continue
        url = e.get('thumb')
        if not url:
            e['img'] = None
            noimg += 1
            continue
        path = d + '/' + nid + img_ext(url)
        if os.path.exists(path) and os.path.getsize(path) > 200:
            e['img'] = 'img/' + nid + img_ext(url)
            have += 1
            continue
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                b = r.read()
            time.sleep(PAUSE)
            if not looks_image(b):
                e['img'] = None
                noimg += 1
                continue
            open(path, 'wb').write(b)
            e['img'] = 'img/' + nid + img_ext(url)
            fetched += 1
        except Exception:
            e['img'] = None
            noimg += 1
    return fetched, have, noimg


def resolve(node):
    nid, label = node['id'], node['label']
    core = core_label(label)
    first = core.split()[0] if core else ''
    flesh = any(m in (node.get('tradition') or '') for m in FLESH_MARKERS)

    if nid in OVERRIDES:
        s = summary(OVERRIDES[nid])
        if s and s.get('type') != 'disambiguation':
            return ok_entry(s, 'override'), None
        return None, 'override-failed:' + OVERRIDES[nid]

    steps = []
    if flesh:
        if core:
            steps.append(('rest', core))
        if first and first != core:
            steps.append(('rest', first))
        if core:
            steps.append(('search', core))
    else:
        if core:
            steps.append(('search', core + ' mythology'))
            steps.append(('search', core))
        if first and first != core:
            steps.append(('search', first + ' mythology'))

    for kind, q in steps:
        titles = [q] if kind == 'rest' else search_titles(q)
        for t in titles:
            s = summary(t)
            if validates(node, s):
                return ok_entry(s, kind + ':' + t), None
    return None, 'unresolved'


def main():
    g = json.load(open(ROOT + '/research/graph.json'))
    cache = {}
    try:
        cache = json.load(open(OUT))
    except Exception:
        pass
    today = time.strftime('%Y-%m-%d')
    for nid, reason in NONE.items():
        if cache.get(nid, {}).get('status') != 'none':
            cache[nid] = {'status': 'none', 'reason': reason, 'checked': today}
    unresolved, done = [], 0
    todo = [n for n in g['nodes']
            if cache.get(n['id'], {}).get('status') not in ('ok', 'none')]
    print('nodes:', len(g['nodes']), ' already cached ok:',
          len(g['nodes']) - len(todo), ' to fetch:', len(todo))
    for i, n in enumerate(todo, 1):
        nid = n['id']
        entry, fail = resolve(n)
        if entry:
            cache[nid] = entry
            done += 1
        else:
            cache[nid] = {'status': 'unresolved', 'via': fail, 'checked': today}
            unresolved.append((nid, n['label'], fail))
        if i % 25 == 0:
            json.dump(cache, open(OUT, 'w'), ensure_ascii=False, indent=1)
            print('  ...', i, 'of', len(todo))
    fetched, have, noimg = download_images(cache)
    json.dump(cache, open(OUT, 'w'), ensure_ascii=False, indent=1)
    ok = sum(1 for v in cache.values() if v['status'] == 'ok')
    print('resolved:', ok, 'of', len(g['nodes']), '; new this run:', done)
    print('images: fetched', fetched, '; cached', have, '; none', noimg)
    if unresolved:
        print('UNRESOLVED:')
        for nid, label, via in unresolved:
            print(' ', nid, '|', label, '|', via)


if __name__ == '__main__':
    main()
