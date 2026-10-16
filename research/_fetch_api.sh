#!/usr/bin/env bash
# EB1911 via API parse + Livy + Sandmann search
cd /home/cobe-liu/Developing/spirit-search/evidence/_corpus || exit 1
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

api() { curl -sL -A "$UA" "$1"; }

api "https://en.wikisource.org/w/api.php?action=parse&page=1911_Encyclop%C3%A6dia_Britannica%2FJoule%2C_James_Prescott&prop=text&format=json" | python3 -c "
import json,sys,re,html
t=json.load(sys.stdin)['parse']['text']['*']
t=re.sub(r'<[^>]+>',' ',html.unescape(t))
open('eb1911-joule.txt','w').write(re.sub(r'\s+',' ',t))
print('joule',len(t))"
sleep 2
api "https://en.wikisource.org/w/api.php?action=parse&page=1911_Encyclop%C3%A6dia_Britannica%2FFaraday%2C_Michael&prop=text&format=json" | python3 -c "
import json,sys,re,html
t=json.load(sys.stdin)['parse']['text']['*']
t=re.sub(r'<[^>]+>',' ',html.unescape(t))
open('eb1911-faraday.txt','w').write(re.sub(r'\s+',' ',t))
print('faraday',len(t))"
sleep 2
api "https://en.wikisource.org/w/api.php?action=parse&page=1911_Encyclop%C3%A6dia_Britannica%2FNewton%2C_Isaac&prop=text&format=json" | python3 -c "
import json,sys,re,html
t=json.load(sys.stdin)['parse']['text']['*']
t=re.sub(r'<[^>]+>',' ',html.unescape(t))
open('eb1911-newton.txt','w').write(re.sub(r'\s+',' ',t))
print('newton',len(t))"
sleep 2
# Ampere title search
api "https://en.wikisource.org/w/api.php?action=query&list=search&srsearch=incategory%3A%221911%20Encyclop%C3%A6dia%20Britannica%22%20Ampere&format=json&srlimit=5" | python3 -c "import json,sys; [print(r['title']) for r in json.load(sys.stdin)['query']['search']]"
sleep 2
# Livy book 1 title search
api "https://en.wikisource.org/w/api.php?action=query&list=search&srsearch=Livy%20Book%201%20Roberts&format=json&srlimit=5" | python3 -c "import json,sys; [print(r['title']) for r in json.load(sys.stdin)['query']['search']]"
# Sandmann English search
curl -s "https://archive.org/advancedsearch.php?q=title%3A%28the+sandman+hoffmann%29+AND+mediatype%3Atexts&fl%5B%5D=identifier,title&rows=5&output=json" | python3 -c "import json,sys; [print(d['identifier'],'|',d.get('title','')[:50]) for d in json.load(sys.stdin)['response']['docs']]"
