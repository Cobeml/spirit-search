#!/usr/bin/env python3
"""Weems cabinet wave: flesh-record nodes from Weems' Life of Washington [15].
Adds nodes (Hamilton, Jefferson, Knox, Jay) + interaction edges to Washington,
excerpts sliced programmatically from the saved 1800s archive file. Auto-added
items are tagged review. Idempotent. Cobe gates power numbers separately.
"""
import json, re, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GP = REPO / "research" / "graph.json"
LP = REPO / "research" / "ledger.json"
WEEMS = REPO / "evidence" / "washington" / "weems_life_of_washington_archive_org_1800_djvu.txt"
SRC_ID = 15
TODAY = "2026-10-14"

text = WEEMS.read_text(errors="replace")
norm = re.sub(r"\s+", " ", text)

def slice_quote(anchor, before=60, after=260):
    i = norm.find(anchor)
    assert i >= 0, f"anchor missing: {anchor[:50]}"
    s = max(0, i - before)
    return norm[s : i + after].strip()

g = json.load(open(GP))
led = json.load(open(LP))
src = next(s for s in led["sources"] if s["id"] == SRC_ID)

QUOTES = {
    "hamilton_treasury": "no pilot can save without the aid of able sea",
    "hamilton_genius": "There was the gallant general Hamilton also",
    "franklin_agent": "Doctor Franklin, who was then in England as a colony agent",
    "franklin_rod": "the old man with his cap and iron rod, for Doctor Franklin",
}
existing_q = {q["text"][:60] for q in src.get("quotes", [])}
for label, anchor in QUOTES.items():
    q = slice_quote(anchor)
    if q[:60] not in existing_q:
        src.setdefault("quotes", []).append({"text": q, "added": TODAY})
        existing_q.add(q[:60])

def qtext(anchor):
    q = slice_quote(anchor)
    return q

def excerpt(anchor):
    return {"text": qtext(anchor), "source_id": SRC_ID,
            "source_title": src["title"], "source_url": src["url"]}

by_id = {n["id"] for n in g["nodes"]}
def has_edge(f, t, ty):
    return any(e["from"] == f and e["to"] == t and e["type"] == ty for e in g["edges"])

NEW = [
    dict(id="alexander-hamilton", label="Alexander Hamilton",
         tradition="American flesh record",
         note="First Secretary of the Treasury; Weems: 'a gigantic genius — a statesman fit to rule the mightiest monarchy' [15]."),
    dict(id="thomas-jefferson", label="Thomas Jefferson",
         tradition="American flesh record",
         note="Secretary of State (Weems: 'Secretary of Foreign Affairs') in Washington's first cabinet [15]."),
    dict(id="henry-knox", label="Henry Knox",
         tradition="American flesh record",
         note="Secretary of War in Washington's first cabinet [15]."),
    dict(id="john-jay", label="John Jay",
         tradition="American flesh record",
         note="Chief Justice named in Weems' roster of the wise rallied by Washington [15]."),
]
for spec in NEW:
    if spec["id"] not in by_id:
        g["nodes"].append({
            "id": spec["id"], "label": spec["label"], "tradition": spec["tradition"],
            "batch": None, "date_added": TODAY, "era": 1800,
            "notes": [{"date": TODAY, "text": spec["note"] + " Auto-added in Weems cabinet wave; power unpriced pending Cobe's gate."}],
            "review": {"status": "auto-added", "date": TODAY},
        })
        by_id.add(spec["id"])

EDGES = [
    dict(frm="george-washington", to="alexander-hamilton",
         title="The pilot hires able seamen",
         anchor=QUOTES["hamilton_treasury"], extra_anchor="hamilton_genius"),
    dict(frm="george-washington", to="thomas-jefferson",
         title="Foreign affairs handed down",
         anchor=QUOTES["hamilton_treasury"], extra_anchor=None),
    dict(frm="george-washington", to="henry-knox",
         title="War office in the seamen's roster",
         anchor=QUOTES["hamilton_treasury"], extra_anchor=None),
    dict(frm="george-washington", to="john-jay",
         title="The bench in the seamen's roster",
         anchor=QUOTES["hamilton_treasury"], extra_anchor=None),
    dict(frm="benjamin-franklin", to="george-washington",
         title="The colony agent in Britain",
         anchor=QUOTES["franklin_agent"], extra_anchor="franklin_rod"),
]
for spec in EDGES:
    if has_edge(spec["frm"], spec["to"], "interaction"):
        continue
    e = {
        "from": spec["frm"], "to": spec["to"], "type": "interaction",
        "source": f"[{SRC_ID}] Weems, Life of Washington, 1800",
        "title": spec["title"],
        "essay": None,
        "date_added": TODAY, "era": 1800, "influence": None,
        "excerpts": [excerpt(spec["anchor"])] + ([excerpt(QUOTES[spec["extra_anchor"]])] if spec["extra_anchor"] else []),
        "review": {"status": "auto-added", "date": TODAY},
    }
    g["edges"].append(e)

shutil.copy(GP, GP.with_suffix(".json.bak"))
json.dump(g, open(GP, "w"), indent=1, ensure_ascii=False)
json.dump(led, open(LP, "w"), indent=1, ensure_ascii=False)
print("nodes:", len(g["nodes"]), "edges:", len(g["edges"]),
      "| source 15 quotes:", len(src["quotes"]))
