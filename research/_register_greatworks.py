#!/usr/bin/env python3
"""Register great-works sources in the project ledger + attach one verbatim quote each."""
import json, re, subprocess, sys

S = "/home/cobe-liu/.hermes/skills/research/grounded-citations/scripts/sources.py"
LEDGER = "/home/cobe-liu/Developing/spirit-search/research/ledger.json"
D = "/home/cobe-liu/.hermes/cache/scratch/corpus"

SPECS = {
 "odyssey.txt": ("https://classics.mit.edu/Homer/odyssey.mb.txt",
   "Homer, Odyssey, trans. Butler 1900 (MIT Classics)", "Tell me, O muse, of that ingenious hero"),
 "herodotus.txt": ("https://classics.mit.edu/Herodotus/history.mb.txt",
   "Herodotus, Histories, trans. G.C. Macaulay 1890 (MIT Classics)", "The History of Herodotus"),
 "thucydides.txt": ("https://classics.mit.edu/Thucydides/pelopwar.mb.txt",
   "Thucydides, History of the Peloponnesian War, trans. Crawley 1874 (MIT Classics)", "The History of the Peloponnesian War"),
 "plato_republic.txt": ("https://classics.mit.edu/Plato/republic.mb.txt",
   "Plato, Republic, trans. Jowett 1871 (MIT Classics)", "The Republic"),
 "aristotle_poetics.txt": ("https://classics.mit.edu/Aristotle/poetics.mb.txt",
   "Aristotle, Poetics, trans. S.H. Butcher 1895 (MIT Classics)", "Poetics"),
 "aristotle_rhetoric.txt": ("https://classics.mit.edu/Aristotle/rhetoric.mb.txt",
   "Aristotle, Rhetoric, trans. W. Rhys Roberts 1924 (MIT Classics)", "Rhetoric"),
 "metamorphoses.txt": ("https://www.gutenberg.org/cache/epub/21765/pg21765.txt",
   "Ovid, Metamorphoses, trans. Brookes More 1922 (Gutenberg #21765)", "Metamorphoses"),
 "plutarch_lives.txt": ("https://www.gutenberg.org/cache/epub/14033/pg14033.txt",
   "Plutarch, Lives, trans. Dryden rev. Clough 1864 (Gutenberg #14033)", "Plutarch"),
 "cicero_nature_gods.txt": ("https://www.gutenberg.org/cache/epub/14988/pg14988.txt",
   "Cicero, De Natura Deorum, trans. Brooks 1896 (Gutenberg #14988)", "Nature of the Gods"),
 "paradise_lost.txt": ("https://www.gutenberg.org/cache/epub/20/pg20.txt",
   "Milton, Paradise Lost 1667 (Gutenberg #20)", "Paradise Lost"),
 "shakespeare.txt": ("https://www.gutenberg.org/cache/epub/100/pg100.txt",
   "Shakespeare, Complete Works (Gutenberg #100)", "Shakespeare"),
 "dante.txt": ("https://www.gutenberg.org/cache/epub/8800/pg8800.txt",
   "Dante, Divine Comedy, trans. Longfellow 1867 (Gutenberg #8800)", "Divine Comedy"),
 "mabinogion.txt": ("https://www.gutenberg.org/cache/epub/5160/pg5160.txt",
   "The Mabinogion, trans. Guest 1877 (Gutenberg #5160)", "Mabinogion"),
}

def run(*args):
    r = subprocess.run(["python3", S, "--ledger", LEDGER, *args], capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()

def slice_quote(path, anchor):
    t = open(path, encoding="utf-8", errors="replace").read()
    flat = re.sub(r"\s+", " ", t)
    i = flat.find(anchor)
    if i < 0:
        # regex anchor
        m = re.search(re.escape(anchor).replace(r"\ ", r"\s+"), flat)
        i = m.start() if m else -1
    if i < 0:
        return None
    return flat[max(0, i-60): i+240].strip()

for fn, (url, title, anchor) in SPECS.items():
    out = run("add", url, "--title", title)
    m = re.search(r"\[(\d+)\]", out)
    if not m:
        print("ADD FAIL", fn, out[:200]); continue
    sid = m.group(1)
    q = slice_quote(f"{D}/{fn}", anchor)
    if not q:
        print("NO QUOTE", fn, sid); continue
    r2 = run("quote", sid, "--text", q, "--from", f"{D}/{fn}")
    print(fn, "->", f"[{sid}]", "quote:", "OK" if "rror" not in r2 and "not found" not in r2.lower() else r2[:150])
