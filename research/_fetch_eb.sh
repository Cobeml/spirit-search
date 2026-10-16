#!/usr/bin/env bash
# Final EB1911 fetches: Watt, Adam Smith, Weems, Victoria (attempt)
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
cd /home/cobe-liu/Developing/spirit-search/evidence/_corpus || exit 1
fetch_eb() {  # fetch_eb <outfile> <page-title-encoded>
  curl -sL -A "$UA" "https://en.wikisource.org/w/api.php?action=parse&page=$1&prop=text&format=json" -o /tmp/eb.json
  python3 - "$2" <<'PY'
import json, re, html, sys
try:
    t = json.load(open("/tmp/eb.json"))["parse"]["text"]["*"]
    t = re.sub(r"<[^>]+>", " ", html.unescape(t))
    open(sys.argv[1], "w").write(re.sub(r"\s+", " ", t))
    print(sys.argv[1], len(t))
except Exception:
    print(sys.argv[1], "FAIL")
PY
  sleep 2
}
fetch_eb "1911_Encyclop%C3%A6dia_Britannica%2FWatt%2C_James" eb1911-watt.txt
fetch_eb "1911_Encyclop%C3%A6dia_Britannica%2FSmith%2C_Adam" eb1911-adam-smith.txt
fetch_eb "1911_Encyclop%C3%A6dia_Britannica%2FWeems%2C_Mason_Locke" eb1911-weems.txt
fetch_eb "1911_Encyclop%C3%A6dia_Britannica%2FVictoria" eb1911-victoria.txt
