#!/usr/bin/env bash
# Retry the failed Wikisource fetches serially with delays
cd /home/cobe-liu/Developing/spirit-search/evidence/_corpus || exit 1
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

curl -sL -A "$UA" -o eb1911-joule.txt "https://en.wikisource.org/w/index.php?title=1911_Encyclop%C3%A6dia_Britannica/Joule,_James_Prescott&action=raw"
sleep 3
curl -sL -A "$UA" -o eb1911-faraday.txt "https://en.wikisource.org/w/index.php?title=1911_Encyclop%C3%A6dia_Britannica/Faraday,_Michael&action=raw"
sleep 3
curl -sL -A "$UA" -o eb1911-ampere.txt "https://en.wikisource.org/w/index.php?title=1911_Encyclop%C3%A6dia_Britannica/Amp%C3%A8re,_Andr%C3%A9-Marie&action=raw"
sleep 3
curl -sL -A "$UA" -o eb1911-newton.txt "https://en.wikisource.org/w/index.php?title=1911_Encyclop%C3%A6dia_Britannica/Newton,_Isaac&action=raw"
sleep 3
curl -sL -A "$UA" -o livy1-roberts.txt "https://en.wikisource.org/w/index.php?title=History_of_Rome,_Book_I&action=raw"
for f in eb1911-joule.txt eb1911-faraday.txt eb1911-ampere.txt eb1911-newton.txt livy1-roberts.txt; do echo "== $f: $(wc -c < $f)"; head -c 120 "$f"; echo; done
