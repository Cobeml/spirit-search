#!/usr/bin/env bash
# Fetch the approved (b)-list witnesses into evidence/_corpus/
set -x
cd /home/cobe-liu/Developing/spirit-search/evidence/_corpus || exit 1
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

fetch() {  # fetch <output> <url>
  curl -sL --retry 2 -A "$UA" -o "$1" "$2" && echo "== $1: $(wc -c < "$1") bytes" || echo "== $1 FAILED"
}

fetch virgil-aeneid-dryden.txt "https://classics.mit.edu/Virgil/aeneid.mb.txt" &
fetch hippocratic-oath.txt "https://classics.mit.edu/Hippocrates/hippooath.mb.txt" &
fetch guest-mabinogion-1877-full.txt "https://www.gutenberg.org/cache/epub/5160/pg5160.txt" &
fetch boswell-life-of-johnson-vol2.txt "https://www.gutenberg.org/cache/epub/9072/pg9072.txt" &
fetch fdr-first-inaugural.txt "https://en.wikisource.org/wiki/Franklin_D._Roosevelt%27s_First_Inaugural_Address?action=raw" &
fetch eb1911-joule.txt "https://en.wikisource.org/wiki/1911_Encyclop%C3%A6dia_Britannica/Joule,_James_Prescott?action=raw" &
fetch eb1911-faraday.txt "https://en.wikisource.org/wiki/1911_Encyclop%C3%A6dia_Britannica/Faraday,_Michael?action=raw" &
fetch eb1911-ampere.txt "https://en.wikisource.org/wiki/1911_Encyclop%C3%A6dia_Britannica/Amp%C3%A8re,_Andr%C3%A9-Marie?action=raw" &
fetch eb1911-newton.txt "https://en.wikisource.org/wiki/1911_Encyclop%C3%A6dia_Britannica/Newton,_Isaac?action=raw" &
wait
fetch ovid-fasti-3-frazer.html "https://www.theoi.com/Text/OvidFasti3.html"
fetch livy1-roberts.txt "https://en.wikisource.org/wiki/The_History_of_Rome,_Book_01?action=raw"
# Sandmann: find an English edition on archive.org
curl -s "https://archive.org/advancedsearch.php?q=title%3A%28sandmann+hoffmann%29+AND+mediatype%3Atexts&fl%5B%5D=identifier&rows=5&output=json" -o /tmp/sand.json
python3 -c "import json; [print(d['identifier']) for d in json.load(open('/tmp/sand.json'))['response']['docs']]"
