#!/usr/bin/env python3
"""Hybrid BM25+vector search over research/search.db with RRF(k=60) fusion.

CLI:  python3 _search_lib.py "query" [--clusters a,b] [--k 10] [--mode hybrid|bm25|vec]
Lib:  from _search_lib import search; search("healer wounded", k=5)
"""
import argparse, json, sqlite3, struct
from pathlib import Path

DB = Path(__file__).resolve().parent / "search.db"
_EMB = None

def _emb():
    global _EMB
    if _EMB is None:
        from fastembed import TextEmbedding
        _EMB = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return _EMB

def _conn():
    import sqlite_vec
    con = sqlite3.connect(DB)
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    return con

def _bm25(con, q, k, clusters=None):
    sql = """SELECT c.id, bm25(chunks_fts) AS score, c.text, s.cluster, s.title, s.url, s.path
             FROM chunks_fts f JOIN chunks c ON c.id=f.rowid
             JOIN sources s ON s.id=c.source_id
             WHERE chunks_fts MATCH ?"""
    if clusters:
        sql += f" AND s.cluster IN ({','.join('?'*len(clusters))})"
    sql += " ORDER BY score LIMIT ?"
    params = [q] + (list(clusters) if clusters else []) + [k * 3]
    try:
        return con.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        return []  # bad FTS query syntax (punctuation) -> no lexical hits

def _vec(con, q, k, clusters=None):
    v = list(_emb().embed([q]))[0]
    blob = struct.pack("f" * len(v), *[float(x) for x in v])
    rows = con.execute(
        """SELECT rowid, distance FROM chunk_vec
           WHERE embedding MATCH ? AND k = ? ORDER BY distance""",
        (blob, k * 6)).fetchall()
    if not rows:
        return []
    sql = """SELECT c.id, c.text, s.cluster, s.title, s.url, s.path
             FROM chunks c JOIN sources s ON s.id=c.source_id
             WHERE c.id IN (%s)""" % ",".join(str(r[0]) for r in rows)
    if clusters:
        sql += f" AND s.cluster IN ({','.join(repr(c) for c in clusters)})"
    info = {r[0]: r[1:] for r in con.execute(sql).fetchall()}
    return [(rid, dist, *info.get(rid, ("", "", "", "", ""))) for rid, dist in rows if rid in info]

def search(q, k=8, mode="hybrid", clusters=None, rrf_k=60):
    con = _conn()
    bm, vc = _bm25(con, q, k * 4, clusters), _vec(con, q, k * 4, clusters)
    scores, data = {}, {}
    for rank, row in enumerate(bm):
        cid = row[0]
        scores[cid] = scores.get(cid, 0) + 1 / (rrf_k + rank + 1)
        data[cid] = row
    for rank, row in enumerate(vc):
        cid = row[0]
        # normalize vec row to bm row shape: (id, score, text, cluster, title, url, path)
        data.setdefault(cid, (row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        scores[cid] = scores.get(cid, 0) + (1 / (rrf_k + rank + 1) if mode != "vec" else 1 / (rank + 1))
    if mode == "bm25":
        order = [row[0] for row in bm][:k]
        out = [(cid, data.get(cid)) for cid in order if cid in data]
    else:
        top = sorted(scores, key=scores.get, reverse=True)[:k]
        out = [(cid, data[cid]) for cid in top]
    return [{"chunk_id": cid,
             "snippet": " ".join(row[2].split())[:600],
             "text": row[2],
             "cluster": row[3], "title": row[4], "url": row[5], "path": row[6]}
            for cid, row in out]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--mode", default="hybrid", choices=["hybrid", "bm25", "vec"])
    ap.add_argument("--clusters", default=None)
    a = ap.parse_args()
    res = search(a.query, k=a.k, mode=a.mode,
                 clusters=a.clusters.split(",") if a.clusters else None)
    print(json.dumps(res, indent=1))
