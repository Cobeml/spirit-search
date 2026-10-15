#!/usr/bin/env python3
"""Wave C: Weems' American roster — war villains and cabinet-era flesh record."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wave import run

FILES = {"weems": "evidence/washington/weems_life_of_washington_archive_org_1800_djvu.txt"}
REF = "[15] Weems, Life of Washington, 1800"

NODES = [
    dict(id="benedict-arnold", label="Benedict Arnold", tradition="American flesh record", era=1800,
         note="Weems' castaway: valour without religion, 'cast out from the Eden of our republic'."),
    dict(id="charles-lee", label="Charles Lee", tradition="American flesh record", era=1800,
         note="The general who chose Monmouth retreat over Washington's glory, in Weems' moral arithmetic."),
    dict(id="aaron-burr", label="Aaron Burr", tradition="American flesh record", era=1800,
         note="In Weems' roll of talent damned for want of religion."),
    dict(id="edward-braddock", label="Edward Braddock", tradition="American flesh record", era=1800,
         note="The British defeat on the Monongahela that framed young Washington's survival."),
]
EDGES = [
    dict(frm="benedict-arnold", to="george-washington", type="conflict", title="The traitor to the pilot's faith",
         file="weems", anchor=r"laid his hand to the forbidden fruit", source_id=15, source_ref=REF, era=1800),
    dict(frm="charles-lee", to="george-washington", type="conflict", title="Retreat before Monmouth's fame",
         file="weems", anchor=r"fell into the vile state of envy", source_id=15, source_ref=REF, era=1800),
    dict(frm="aaron-burr", to="alexander-hamilton", type="conflict", title="Coupled in the fatal roll",
         file="weems", anchor=r"the Hamiltons and Burrs of the earth", source_id=15, source_ref=REF, era=1800),
    dict(frm="edward-braddock", to="george-washington", type="interaction", title="The field the young colonel survived",
         file="weems", anchor=r"Braddock", source_id=15, source_ref=REF, era=1800),
]

if __name__ == "__main__":
    run(NODES, EDGES, FILES)
