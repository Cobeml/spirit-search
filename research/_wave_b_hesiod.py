#!/usr/bin/env python3
"""Wave B: Hesiod Titan genealogy (highest-power cluster: prometheus line)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wave import run

FILES = {"theog": "evidence/epimetheus/hesiod-evelynwhite-gutenberg348.txt"}
REF = "[26] Hesiod, Theogony"
E = -700
TR = "Greek myth (Hesiodic)"

NODES = [
    dict(id="cronos", label="Cronos", tradition=TR, era=E,
         note="Wily Cronos who swallowed his children; Zeus' father."),
    dict(id="rhea", label="Rhea", tradition=TR, era=E,
         note="Rhea who bare Zeus; gave Cronos the wrapped stone."),
    dict(id="oceanus", label="Oceanus", tradition=TR, era=E,
         note="Eldest Titan river; father of Styx and Metis in the catalogue."),
    dict(id="hyperion", label="Hyperion", tradition=TR, era=E,
         note="Father of Helios, Selene, Eos by Theia."),
    dict(id="iapetus", label="Iapetus", tradition=TR, era=E,
         note="Father of Atlas, Epimetheus, Prometheus; anchor of the Iapetid line."),
    dict(id="tethys", label="Tethys", tradition=TR, era=E, note="Oceanus' wife."),
    dict(id="theia", label="Theia", tradition=TR, era=E, note="Hyperion's wife."),
    dict(id="phoebe", label="Phoebe", tradition=TR, era=E,
         note="Mother of Leto and Asteria; a Titaness of the bright name."),
    dict(id="coeus", label="Coeus", tradition=TR, era=E, note="Titan; Leto's father with Phoebe."),
    dict(id="crius", label="Crius", tradition=TR, era=E, note="Titan; Astraeus and Pallas' father by Eurybia."),
    dict(id="helios", label="Helios", tradition=TR, era=E, note="The sun, Hyperion's son."),
    dict(id="selene", label="Selene", tradition=TR, era=E, note="The moon, Hyperion's daughter."),
    dict(id="eos", label="Eos", tradition=TR, era=E, note="Dawn, Hyperion's daughter."),
    dict(id="leto", label="Leto", tradition=TR, era=E,
         note="'Leto, being always unwearied'; mother of Apollo and Artemis."),
    dict(id="asteria", label="Asteria", tradition=TR, era=E, note="Starry one; Phoebe's daughter, mother of Hecate."),
    dict(id="pontus", label="Pontus", tradition=TR, era=E, note="Earth's sea-son, without union of love."),
    dict(id="nereus", label=None, tradition=TR, era=E, note=""),  # exists; skip guard
    dict(id="ceto", label="Ceto", tradition=TR, era=E, note="Pontus' daughter, wife of Phorcys."),
    dict(id="phorcys", label="Phorcys", tradition=TR, era=E, note="Sea-elder, Ceto's husband."),
    dict(id="tartarus", label="Tartarus", tradition=TR, era=E,
         note="The gulf where the Titans were bound; anvil of nine days' fall."),
]

EDGES = [
    dict(frm="cronos", to="zeus", type="kinship", title="The swallowed and the stone",
         file="theog", anchor=r"great Cronos who swallowed.{0,120}|Cronos the wily", source_id=26, source_ref=REF, era=E),
    dict(frm="rhea", to="zeus", type="kinship", title="Rhea bare him",
         file="theog", anchor=r"Rhea was subject in love to Cronos", source_id=26, source_ref=REF, era=E),
    dict(frm="iapetus", to="prometheus", type="kinship", title="The Iapetid line of wiles",
         file="theog", anchor=r"Iapetus", source_id=26, source_ref=REF, era=E),
    dict(frm="iapetus", to="atlas", type="kinship", title="Strong Atlas by Iapetus",
         file="theog", anchor=r"And she bare him a stout-hearted son, Atlas", source_id=26, source_ref=REF, era=E),
    dict(frm="hyperion", to="helios", type="kinship", title="The sun given to Theia",
         file="theog", anchor=r"(?:Theia|great Hyperion).{0,160}?(?:Helius|Helios)", source_id=26, source_ref=REF, era=E),
    dict(frm="hyperion", to="selene", type="kinship", title="The moon in the same litter",
         file="theog", anchor=r"Hyperion.{0,120}?(?:Selene|Moon)", source_id=26, source_ref=REF, era=E),
    dict(frm="hyperion", to="eos", type="kinship", title="Early-born Dawn",
         file="theog", anchor=r"Eos and great Helius and bright Selene", source_id=26, source_ref=REF, era=E),
    dict(frm="phoebe", to="leto", type="kinship", title="Phoebe bare Leto",
         file="theog", anchor=r"Phoebe came to the desired embrace of Coeus|Phoebe.{0,120}?Leto", source_id=26, source_ref=REF, era=E),
    dict(frm="coeus", to="leto", type="kinship", title="The desired embrace",
         file="theog", anchor=r"Coeus", source_id=26, source_ref=REF, era=E),
    dict(frm="leto", to="apollo", type="kinship", title="The unwearied mother",
         file="theog", anchor=r"Leto", source_id=26, source_ref=REF, era=E),
    dict(frm="asteria", to="hecate", type="kinship", title="Hecate of Asteria",
         file="theog", anchor=r"Asteria.{0,160}?Hecate|Hecate.{0,160}?Asteria", source_id=26, source_ref=REF, era=E),
    dict(frm="oceanus", to="styx", type="kinship", title="Chiefest of the Oceanids",
         file="theog", anchor=r"Styx who is the chiefest of them all", source_id=26, source_ref=REF, era=E),
    dict(frm="oceanus", to="metis", type="kinship", title="Metis among the eldest daughters",
         file="theog", anchor=r"Europa, Metis, and Eurynome", source_id=26, source_ref=REF, era=E),
    dict(frm="pontus", to="nereus", type="kinship", title="True and lies not",
         file="theog", anchor=r"Sea begat Nereus, the eldest of his children", source_id=26, source_ref=REF, era=E),
    dict(frm="phorcys", to="ceto", type="marriage", title="Sea-elder wed to sea's daughter",
         file="theog", anchor=r"Phorcys.{0,160}?Ceto|Ceto.{0,160}?Phorcys", source_id=26, source_ref=REF, era=E),
    dict(frm="zeus", to="tartarus", type="conflict", title="The nine-day anvil fall",
         file="theog", anchor=r"Tartarus", source_id=26, source_ref=REF, era=E),
]

if __name__ == "__main__":
    NODES = [n for n in NODES if n.get("label")]
    run(NODES, EDGES, FILES)
