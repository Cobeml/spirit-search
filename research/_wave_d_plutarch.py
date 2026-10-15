#!/usr/bin/env python3
"""Wave D: Plutarch Roman/Greek lives; link into cincinnatus/sulla/pericles.
First registers the full-text corpus file as a ledger source (idempotent by URL).
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wave import run, load, LP

FILES = {"plu": "evidence/_corpus/plutarch-lives-dryden-clough-gutenberg.txt"}
URL = "https://archive.org/download/plutarchlivesoft00674gut/plivs10.txt"
TITLE = "Plutarch, Lives, trans. Dryden rev. Clough 1864 (Gutenberg ed. archive.org plivs10)"

def ensure_source():
    g, led = load()
    hit = next((s for s in led["sources"] if s.get("url") == URL), None)
    if hit is None:
        new_id = max(s["id"] for s in led["sources"]) + 1
        led["sources"].append({"id": new_id, "url": URL, "title": TITLE,
                               "accessed": "2026-10-15", "quotes": []})
        json.dump(led, open(LP, "w"), indent=1, ensure_ascii=False)
        return new_id
    return hit["id"]

SID = ensure_source()
REF = f"[{SID}] Plutarch, Lives (Dryden/Clough)"
TR = "Plutarchan flesh record"
E = 100

NODES = [
    dict(id="valerius-publicola", label="Publicola", tradition=TR, era=E,
         note="Poplicola; the Brutus colleague who yielded the fasces and died poor."),
    dict(id="fabius-maximus", label="Fabius Maximus", tradition=TR, era=E,
         note="The Delayer; command without battle, the savior by patience."),
    dict(id="marcius-coriolanus", label="Coriolanus", tradition=TR, era=E,
         note="The exiled shield turning on its own city."),
    dict(id="numa-pompilius", label="Numa Pompilius", tradition=TR, era=E,
         note="The piety-founder: Rome's second king and its cult author."),
    dict(id="romulus", label="Romulus", tradition=TR, era=E,
         note="Founder; disappearer in the cloud; the Quirinus claim."),
    dict(id="marcellus", label="Marcellus", tradition=TR, era=E,
         note="Spolia opima winner; five-time consul; Syracuse's conqueror."),
    dict(id="cato-elder", label="Cato the Elder", tradition=TR, era=E,
         note="Censor and delenda-est; the anti-luxury ploughman."),
    dict(id="aemilius-paullus", label="Aemilius Paullus", tradition=TR, era=E,
         note="Pydna's victor who refused the spoils and walked in Perseus' train reversed."),
]
EDGES = [
    dict(frm="romulus", to="numa-pompilius", type="succession", title="War hands the city to piety",
         file="plu", anchor=r"Romulus.{0,300}?Numa|Numa.{0,300}?Romulus", source_id=SID, source_ref=REF, era=E),
    dict(frm="romulus", to="quirinus", type="transmission", title="The disappearance named",
         file="plu", anchor=r"Quirinus", source_id=SID, source_ref=REF, era=E),
    dict(frm="cincinnatus", to="valerius-publicola", type="analogy", title="Two consulships of renunciation",
         file="plu", anchor=r"Poplicola.{0,300}?consul", source_id=SID, source_ref=REF, era=E),
    dict(frm="fabius-maximus", to="cincinnatus", type="analogy", title="The slow answer to invasion",
         file="plu", anchor=r"Fabius", source_id=SID, source_ref=REF, era=E),
    dict(frm="marcellus", to="fabius-maximus", type="comparison", title="Sword against the shield of Rome",
         file="plu", anchor=r"Marcellus.{0,400}?Fabius", source_id=SID, source_ref=REF, era=E),
    dict(frm="marcius-coriolanus", to="fabius-maximus", type="contrast", title="Pride against patience",
         file="plu", anchor=r"Coriolanus", source_id=SID, source_ref=REF, era=E),
    dict(frm="cato-elder", to="aemilius-paullus", type="conflict", title="The censor snubbed by the victor",
         file="plu", anchor=r"Aemilius.{0,400}?Cato\b", source_id=SID, source_ref=REF, era=E),
    dict(frm="aemilius-paullus", to="pericles", type="analogy", title="Moderation at the top of fortunes",
         file="plu", anchor=r"Perseus.{0,400}?Aemilius|Aemilius.{0,400}?Perseus", source_id=SID, source_ref=REF, era=E),
]

if __name__ == "__main__":
    run(NODES, EDGES, FILES)
