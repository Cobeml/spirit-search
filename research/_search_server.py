#!/usr/bin/env python3
"""Search API for the spirit-search UI. GET /search?q=...&k=10&mode=hybrid
Serves on 127.0.0.1:8788 alongside the static site at :8787.
"""
import json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _search_lib import search

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        u = urlparse(self.path)
        if u.path != "/search":
            self.send_response(404); self.end_headers(); return
        p = parse_qs(u.query)
        q = p.get("q", [""])[0]
        if not q.strip():
            self._send({"results": []}); return
        k = min(int(p.get("k", [10])[0]), 50)
        mode = p.get("mode", ["hybrid"])[0]
        clusters = p.get("clusters", [None])[0]
        clusters = clusters.split(",") if clusters else None
        try:
            res = search(q, k=k, mode=mode, clusters=clusters)
        except Exception as e:  # noqa: BLE001
            self._send({"error": str(e)}); return
        self._send({"results": [{k2: v for k2, v in r.items() if k2 != "text"} | {"text": r["text"]} for r in res]})

    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    print("search server on http://127.0.0.1:8788/search?q=...")
    ThreadingHTTPServer(("127.0.0.1", 8788), H).serve_forever()
