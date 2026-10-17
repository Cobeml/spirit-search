#!/usr/bin/env python3
"""Build research/search.db: chunk evidence/ texts, FTS5 + sqlite-vec hybrid index.

Corpus layout:
  evidence/<cluster_slug>/<file>.txt  -> chunks keyed to the cluster (usually a node id)
Chunks: ~1800 chars at blank-line boundaries, 240 char overlap. Offsets stored, not re-sliced.
Embeddings: fastembed (ONNX, bge-small-en-v1.5, 384d) by default.
"""
import json, os, re, sqlite3, struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _textclean as TC

REPO = Path(__file__).resolve().parent.parent
EVID = REPO / "evidence"
DB = REPO / "research" / "search.db"
CHUNK = 1800
OVERLAP = 240

def load_for_chunks(path):
    """Scrubbed (boilerplate/mojibake/invisible-free), case-preserving text
    with paragraph structure intact (blank lines kept for chunking)."""
    raw = path.read_text(errors="replace")
    return TC._tags(TC.scrub_raw(raw))

def chunk_text(text):
    """Paragraph-first chunking; oversized paragraphs split at sentence
    boundaries so context modal edges read as whole sentences."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    pieces = []
    for p in paras:
        if len(p) <= CHUNK * 2:
            pieces.append(p)
            continue
        i = 0
        while i < len(p):
            j = TC._next_boundary(p, min(i + int(CHUNK * 0.75), len(p) - 1),
                                  max_fwd=CHUNK)
            if j is None or j <= i + 100:
                j = min(len(p), i + CHUNK)
            piece = p[i:j].strip()
            if piece:
                pieces.append(piece)
            i = j
    chunks, cur = [], ""
    for p in pieces:
        if len(cur) + len(p) + 2 > CHUNK and cur:
            chunks.append(cur)
            cur = cur[-OVERLAP:] + "\n\n" + p if OVERLAP else p
        else:
            cur = (cur + "\n\n" + p) if cur else p
    if cur.strip():
        chunks.append(cur)
    return chunks

def main(dim_model="BAAI/bge-small-en-v1.5"):
    import sqlite_vec
    from fastembed import TextEmbedding

    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    cur = con.cursor()
    cur.executescript(f"""
    CREATE TABLE sources(
      id INTEGER PRIMARY KEY,
      cluster TEXT, path TEXT, title TEXT, url TEXT
    );
    CREATE TABLE chunks(
      id INTEGER PRIMARY KEY,
      source_id INTEGER REFERENCES sources(id),
      seq INTEGER, start_off INTEGER, text TEXT
    );
    CREATE VIRTUAL TABLE chunks_fts USING fts5(text, content='chunks', content_rowid='id');
    CREATE VIRTUAL TABLE chunk_vec USING vec0(embedding float[384]);
    """)
    # reuse ledger source metadata when a file matches by filename
    ledger = json.load(open(REPO / "research" / "ledger.json"))
    meta_by_name = {}
    for s in ledger["sources"]:
        fn = s.get("url", "").split("/")[-1]
        meta_by_name[fn] = s

    files = sorted(p for p in EVID.rglob("*.txt") if p.stat().st_size > 200)
    print(f"indexing {len(files)} files")
    all_chunks = []
    sid = 0
    for f in files:
        sid += 1
        text = load_for_chunks(f)
        meta = meta_by_name.get(f.name, {})
        cur.execute("INSERT INTO sources VALUES(?,?,?,?,?)",
                    (sid, f.parent.name, str(f.relative_to(REPO)),
                     meta.get("title", f.name), meta.get("url", "")))
        for i, c in enumerate(chunk_text(text)):
            cur.execute("INSERT INTO chunks VALUES(NULL,?,?,?,?)",
                        (sid, i, -1, c))
            cid = cur.lastrowid
            cur.execute("INSERT INTO chunks_fts(rowid, text) VALUES(?,?)", (cid, c))
            all_chunks.append((cid, c))
    print(f"{len(all_chunks)} chunks; embedding with {dim_model} ...")
    emb = TextEmbedding(model_name=dim_model)
    vecs = emb.embed((c for _, c in all_chunks))
    for (cid, _), v in zip(all_chunks, vecs):
        cur.execute("INSERT INTO chunk_vec(rowid, embedding) VALUES(?,?)",
                    (cid, struct.pack("f" * len(v), *[float(x) for x in v])))
    con.commit()
    print(f"done -> {DB} ({DB.stat().st_size/1e6:.1f} MB)")

if __name__ == "__main__":
    main()
