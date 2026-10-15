#!/usr/bin/env python3
"""Waves E (Iliad heroes), F (Ginzberg Genesis), G (Edda heroes), H (Apuleius)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wave import run

FILES = {
    "iliad": "evidence/machaon/homer-iliad-butler-mb.txt",
    "ginz": "evidence/lilith/ginzberg-legends1-gutenberg.txt",
    "edda": "evidence/volundr/bellows-poetic-edda-1923-full.txt",
    "apul": "evidence/rhiannon/apuleius-golden-ass-adlington-gutenberg.txt",
}
IL = "[1] Homer, Iliad, trans. Butler"
GZ = "[19] Ginzberg, Legends of the Jews vol 1"
ED = "[46] Bellows, The Poetic Edda"
AP = "[22] Apuleius, Golden Ass"
EI = -750; EG = 1909; EE = 850; EA = 150  # era of cited source transmission window per edge conventions

def W(frm, to, ty, title, f, anchor, sid, ref, era):
    return dict(frm=frm, to=to, type=ty, title=title, file=f, anchor=anchor,
                source_id=sid, source_ref=ref, era=era)

NODES = [
    # E: Iliad flesh of the folders
    dict(id="agamemnon", label="Agamemnon", tradition="Greek epic", era=EI,
         note="Son of Atreus, leader of the host; 194 mentions in Butler's Iliad."),
    dict(id="menelaus", label="Menelaus", tradition="Greek epic", era=EI,
         note="Wronged husband; healed by Machaon in book 4."),
    dict(id="odysseus", label="Odysseus", tradition="Greek epic", era=EI,
         note="'Ulysses' in Butler; the resourceful under war's ceiling."),
    dict(id="ajax-telamonian", label="Ajax son of Telamon", tradition="Greek epic", era=EI,
         note="Bastion of the host; 206 mentions in Butler's Iliad."),
    dict(id="diomedes", label="Diomedes", tradition="Greek epic", era=EI,
         note="'Diomed' in Butler; wounded Ares and Aphrodite in day."),
    dict(id="patroclus", label="Patroclus", tradition="Greek epic", era=EI,
         note="Achilles' second soul; the hinge the wounded Machaon sets moving."),
    dict(id="sarpedon", label="Sarpedon", tradition="Greek epic", era=EI,
         note="Lycian prince, son of Zeus, slain by Patroclus."),
    dict(id="helen", label="Helen", tradition="Greek epic", era=EI,
         note="The cause and the regret, speaking from the walls."),
    dict(id="calchas", label="Calchas", tradition="Greek epic", era=EI,
         note="Seer of the host; reader of Apollo's plague."),
    dict(id="idomeneus", label="Idomeneus", tradition="Greek epic", era=EI,
         note="Cretan head who priced the physician over several men."),
    # F: Genesis flesh record via Ginzberg
    dict(id="enoch", label="Enoch", tradition="Genesis legends (Ginzberg)", era=EG,
         note="Walked with God and was not; Ginzberg assembles the ascent traditions."),
    dict(id="noah", label="Noah", tradition="Genesis legends (Ginzberg)", era=EG,
         note="Ark-builder; flood patient patriarch."),
    dict(id="abraham", label="Abraham", tradition="Genesis legends (Ginzberg)", era=EG,
         note="Covenant bearer; 696 mentions in Legends vol 1."),
    dict(id="isaac", label="Isaac", tradition="Genesis legends (Ginzberg)", era=EG,
         note="The bound son; laughter's namesake."),
    dict(id="jacob", label="Jacob", tradition="Genesis legends (Ginzberg)", era=EG,
         note="Israel; ladder and wrestling night."),
    dict(id="joseph", label="Joseph", tradition="Genesis legends (Ginzberg)", era=EG,
         note="Dream economist into Egypt."),
    # G: Edda
    dict(id="sigurd", label="Sigurd", tradition="Norse myth (Poetic Edda)", era=EE,
         note="Sigurth in Bellows; Fafnir's slayer, Regin's foster."),
    dict(id="fafnir", label="Fafnir", tradition="Norse myth (Poetic Edda)", era=EE,
         note="The dragon on the hoard."),
    dict(id="regin", label="Regin", tradition="Norse myth (Poetic Edda)", era=EE,
         note="Smith to kings; the fosterer who forged the slaying."),
    dict(id="brynhild", label="Brynhild", tradition="Norse myth (Poetic Edda)", era=EE,
         note="The wakeless shieldmaid."),
    dict(id="hel", label="Hel", tradition="Norse myth (Poetic Edda)", era=EE,
         note="Half-dead ruler of the ninth world's low house."),
    dict(id="fenrir", label="Fenrir", tradition="Norse myth (Poetic Edda)", era=EE,
         note="The wolf foredoomed to Odin's swallowing."),
    dict(id="tyr", label="Tyr", tradition="Norse myth (Poetic Edda)", era=EE,
         note="One-handed god; his hand in the wolf's mouth as pledge."),
    dict(id="atli", label="Atli", tradition="Norse myth (Poetic Edda)", era=EE,
         note="Attila folded into legend; 300 mentions in Bellows."),
    # H: Apuleius
    dict(id="psyche", label="Psyche", tradition="Apuleian tale", era=EA,
         note="The soul given trials for love; Adlington 1566."),
    dict(id="cupid", label="Cupid", tradition="Apuleian tale", era=EA,
         note="The unseen husband of Psyche."),
]

EDGES = [
    W("agamemnon", "menelaus", "kinship", "The sons of Atreus", "iliad",
      r"sons of Atreus", 1, IL, EI),
    W("menelaus", "machaon", "interaction", "Healed by the herb-lore",
      "iliad", r"Machaon.{0,250}?Menelaus", 1, IL, EI),
    W("odysseus", "agamemnon", "interaction", "Counsel to the host's head", "iliad",
      r"Ulysses.{0,250}?Agamemnon", 1, IL, EI),
    W("ajax-telamonian", "hector", "conflict", "The bastion stands the wave back", "iliad",
      r"Ajax.{0,250}?Hector", 1, IL, EI),
    W("diomedes", "ares", "conflict", "Wounds the war-god in daylight", "iliad",
      r"Diomed.{0,250}?Mars|Diomed.{0,250}?Ares", 1, IL, EI),
    W("patroclus", "achilles", "kinship", "Soul for soul", "iliad",
      r"Patroclus.{0,250}?Achilles", 1, IL, EI),
    W("sarpedon", "zeus", "kinship", "The father watches his son die", "iliad",
      r"Sarpedon.{0,250}?(?:Jove|Jupiter|Zeus)", 1, IL, EI),
    W("helen", "priam", "interaction", "Named from the wall", "iliad",
      r"Helen.{0,200}?Priam", 1, IL, EI),
    W("calchas", "apollo", "interaction", "Reading the archer's plague", "iliad",
      r"Calchas", 1, IL, EI),
    W("idomeneus", "machaon", "interaction", "The physician priced above fighters", "iliad",
      r"physician is worth more", 1, IL, EI),
    W("enoch", "noah", "kinship", "The ascended forebears the ark", "ginz",
      r"Enoch.{0,300}?Noah", 19, GZ, EG),
    W("noah", "abraham", "kinship", "Seed and covenant after the flood", "ginz",
      r"Noah.{0,300}?Abraham", 19, GZ, EG),
    W("abraham", "isaac", "kinship", "The bound son", "ginz",
      r"Isaac.{0,200}?Abraham", 19, GZ, EG),
    W("isaac", "jacob", "kinship", "Two blessings on one house", "ginz",
      r"Jacob.{0,150}?Isaac", 19, GZ, EG),
    W("jacob", "joseph", "kinship", "The dreamer sent ahead", "ginz",
      r"Joseph.{0,200}?Jacob", 19, GZ, EG),
    W("regin", "sigurd", "interaction", "The smith who forged the slayer", "edda",
      r"Regin.{0,250}?Sigurd|Sigurth.{0,250}?Regin", 46, ED, EE),
    W("sigurd", "fafnir", "conflict", "The hoard won from the serpent", "edda",
      r"Fafnir.{0,250}?Regin", 46, ED, EE),
    W("brynhild", "sigurd", "interaction", "Wakeful to betrayal", "edda",
      r"Brynhild.{0,250}?Sigurth", 46, ED, EE),
    W("hel", "odin", "interaction", "Half the dead to her hall", "edda",
      r"Hel.{0,200}?Odin|Othin.{0,200}?Hel", 46, ED, EE),
    W("fenrir", "odin", "conflict", "The wolf the All-Father feeds", "edda",
      r"Fenrir.{0,250}?(?:Othin|Odin)", 46, ED, EE),
    W("tyr", "fenrir", "conflict", "The hand left in the jaw", "edda",
      r"Tyr.{0,250}?Fenrir|Fenrir.{0,250}?Tyr", 46, ED, EE),
    W("atli", "brynhild", "kinship", "Brother to the oath-maid", "edda",
      r"Atli.{0,250}?Brynhild", 46, ED, EE),
    W("psyche", "cupid", "marriage", "The unseen husband", "apul",
      r"Psyche.{0,250}?Cupid", 22, AP, EA),
    W("psyche", "venus", "conflict", "The goddess' jealous service", "apul",
      r"Psyche.{0,300}?Venus", 22, AP, EA),
]

if __name__ == "__main__":
    run(NODES, EDGES, FILES)
