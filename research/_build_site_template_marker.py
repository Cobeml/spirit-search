import json, html, re, datetime, shutil, os
ROOT='/home/cobe-liu/Developing/spirit-search'
SITE=ROOT+'/docs'
g=json.load(open(ROOT+'/research/graph.json'))
ledger=json.load(open(ROOT+'/research/ledger.json'))
wiki={}
try: wiki=json.load(open(ROOT+'/research/wikipedia.json'))
except Exception: pass
urls={s['id']:s['url'] for s in ledger['sources']}
titles={s['id']:s['title'] for s in ledger['sources']}

def linkify(text):
    if not text: return ''
    t=html.escape(text)
    def rep(m):
        n=int(m.group(1))
        if n in urls:
            return f'<a class="cite" href="{html.escape(urls[n])}" target="_blank" rel="noopener" title="{html.escape(titles[n])}">[{n}]</a>'
        return m.group(0)
    return re.sub(r'\[(\d+)\]', rep, t)

support_essay="Supporting figure. Registered because a primary narrative names them; no standalone essay yet. Their documented interactions are the edges below."

nodes=[]
for n in sorted(g['nodes'], key=lambda x:(x.get('date_added',''),x['label'])):
    d={
        'id':n['id'],'label':n['label'],'tradition':n.get('tradition',''),
        'batch':n.get('batch'),'date_added':n.get('date_added'),
        'era':n.get('era'),
        'pw_d':n.get('power_watts_direct',0),'pw_p':n.get('power_watts_proxy',0),
        'pw_t':n.get('power_watts_total',0),'pw_e':n.get('power_watts_at_era',0),
        'pw_status':n.get('power_status','unpriced'),
        'pw_pool':n.get('power_pool'),'pw_why':n.get('power_rationale'),
        'pw_ws':n.get('power_witness_strength'),
        'essay':n.get('essay') or support_essay,
        'highlights':n.get('highlights',[]),
        'proposals':n.get('proposals',[]),
        'review':n.get('review')}
    # Wikipedia context (Cobe 2026-10-21): name links to the page, lead blurb
    # renders before the highlights. CONTEXT ONLY — never a citation for a
    # highlight or edge; corpus witnesses substantiate everything else.
    w=wiki.get(n['id'])
    if w and w.get('status')=='ok' and w.get('blurb'):
        d['wiki']={'title':w.get('title'),'url':w.get('url'),'blurb':w['blurb'],'img':w.get('img')}
    nodes.append(d)

edges=[{'frm':e['from'],'to':e['to'],'type':e['type'],'title':e['title'],'essay':e['essay'],'source':e.get('source',''),'date_added':e.get('date_added'),'era':e.get('era'),'excerpts':e.get('excerpts',[]),'influence':e.get('influence'),'review':e.get('review'),'audit':e.get('audit'),'pairing_note':e.get('pairing_note')} for e in g['edges']]

data={'nodes':nodes,'edges':edges,
      'sources':[{'id':i,'url':urls[i],'title':titles[i]} for i in sorted(urls)],
      'version':g.get('version'),
      'generated':datetime.date.today().isoformat()}

TEMPLATE=open(SITE+'/template.html').read()
assert '/*__DATA__*/' in TEMPLATE
page=TEMPLATE.replace('/*__DATA__*/', json.dumps(data, ensure_ascii=False))
open(SITE+'/index.html','w').write(page)
# mirror template into legacy site/ for the posted-file workflow
os.makedirs(ROOT+'/site', exist_ok=True)
shutil.copy(SITE+'/template.html', ROOT+'/site/template.html')
print('docs/index.html written:', len(page), 'bytes;', len(nodes),'nodes;',len(edges),'edges')
