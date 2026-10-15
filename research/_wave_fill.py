#!/usr/bin/env python3
"""Wave fill: edges for orphaned wave nodes + loose anchors."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wave import run

FILES = {
    "mab3": "evidence/rhiannon/guest-mabinogion-vol3-gutenberg.txt",
    "macc": "evidence/rhiannon/macculloch-religion-ancient-celts-1911.txt",
    "theog": "evidence/epimetheus/hesiod-evelynwhite-gutenberg348.txt",
    "weems": "evidence/washington/weems_life_of_washington_archive_org_1800_djvu.txt",
}
MAB = "[21] Mabinogion vol 3, trans. Guest"
MAC = "[23] MacCulloch, Religion of the Ancient Celts"
REF = "[26] Hesiod, Theogony"
WE = "[15] Weems, Life of Washington, 1800"

NODES = []
EDGES = [
    dict(frm="maelgwn", to="taliesin", type="interaction", title="The judgment of the chairs",
         file="mab3", anchor=r"Maelgwn", source_id=21, source_ref=MAB, era=1350),
    dict(frm="balor", to="lugh", type="kinship", title="Grandfather to the sling", 
         file="macc", anchor=r"Balor", source_id=23, source_ref=MAC, era=1911),
    dict(frm="lugh", to="nuada", type="succession", title="The host passes to the many-skilled",
         file="macc", anchor=r"Tuatha De Danann.{0,400}?(?:Lugh|Lug)\b|(?:Lugh|Lug)\b.{0,300}?Nuada", source_id=23, source_ref=MAC, era=1911),
    dict(frm="oceanus", to="tethys", type="marriage", title="Three thousand daughters",
         file="theog", anchor=r"Oceanus.{0,300}?Tethys|Tethys.{0,300}?Oceanus", source_id=26, source_ref=REF, era=-700),
    dict(frm="hyperion", to="theia", type="marriage", title="Sun and moon given to Theia",
         file="theog", anchor=r"Hyperion.{0,400}?Helius|great Hyperion", source_id=26, source_ref=REF, era=-700),
    dict(frm="crius", to="astr", type="kinship", title="Crius by Eurybia",
         file="theog", anchor=r"Crius", source_id=26, source_ref=REF, era=-700),
    dict(frm="benedict-arnold", to="aaron-burr", type="comparison", title="Coupled in the fatal roll",
         file="weems", anchor=r"why should I summon the Arnolds", source_id=15, source_ref=WE, era=1800),
]
if __name__ == "__main__":
    EDGES = [e for e in EDGES if e["to"] != "astr"]  # astr not a node; drop if anchor weak
    EDGES.append(dict(frm="crius", to="phoebe", type="kinship", title="Brother of the bright name",
        file="theog", anchor=r"Coeus and Crius", source_id=26, source_ref=REF, era=-700))
    run(NODES, EDGES, FILES)

# second pass: last two orphans
