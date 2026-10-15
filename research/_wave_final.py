#!/usr/bin/env python3
"""Wave E-final: reach 200 nodes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wave import run

FILES = {
    "ila": "evidence/machaon/homer-iliad-butler-mb.txt",
    "ginz": "evidence/lilith/ginzberg-legends1-gutenberg.txt",
    "edda": "evidence/volundr/bellows-poetic-edda-1923-full.txt",
    "weems": "evidence/washington/weems_life_of_washington_archive_org_1800_djvu.txt",
}
IL = "[1] Homer, Iliad, trans. Butler"
GZ = "[19] Ginzberg, Legends of the Jews vol 1"
ED = "[46] Bellows, The Poetic Edda"
WE = "[15] Weems, Life of Washington, 1800"

NODES = [
    dict(id="cain", label="Cain", tradition="Genesis legends (Ginzberg)", era=1909,
         note="First shedder of brother's blood."),
    dict(id="abel", label="Abel", tradition="Genesis legends (Ginzberg)", era=1909,
         note="The keeper of flocks whose sacrifice was accepted."),
    dict(id="guthrun", label="Guthrun", tradition="Norse myth (Poetic Edda)", era=850,
         note="Gudrun in later spelling; Sigurth's widow, Atli's wife, the cycle's survivor."),
    dict(id="mimir", label="Mimir", tradition="Norse myth (Poetic Edda)", era=850,
         note="The water-spirit of wisdom; Othin's pledge-eyed well."),
    dict(id="dione", label="Dione", tradition="Greek myth (Hesiodic)", era=-750,
         note="Oceanid namesake of Aphrodite's mother in the Iliad."),
    dict(id="james-wilson", label="James Wilson", tradition="American flesh record", era=1800,
         note="Justice named in Weems' roster of the wise rallied around Washington."),
]
EDGES = [
    dict(frm="cain", to="abel", type="conflict", title="The first fratricide",
         file="ginz", anchor=r"Cain.{0,250}?Abel", source_id=19, source_ref=GZ, era=1909),
    dict(frm="abel", to="adam", type="kinship", title="Second son of the first house",
         file="ginz", anchor=r"Abel.{0,200}?Adam|Adam.{0,200}?Abel", source_id=19, source_ref=GZ, era=1909),
    dict(frm="guthrun", to="sigurd", type="marriage", title="The widow of the slayer", file="edda",
         anchor=r"Guthrun.{0,400}?Sigurth", source_id=46, source_ref=ED, era=850),
    dict(frm="mimir", to="odin", type="interaction", title="The eye pledged for wisdom",
         file="edda", anchor=r"Othin's eye.{0,250}?Mimir", source_id=46, source_ref=ED, era=850),
    dict(frm="dione", to="aphrodite", type="kinship", title="The Oceanid mother", file="ila",
         anchor=r"Dione", source_id=1, source_ref=IL, era=-750),
    dict(frm="george-washington", to="james-wilson", type="interaction", title="A justice in the seamen's roster",
         file="weems", anchor=r"James Wilson", source_id=15, source_ref=WE, era=1800),
]

if __name__ == "__main__":
    run(NODES, EDGES, FILES)
