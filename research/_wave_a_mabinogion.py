#!/usr/bin/env python3
"""Wave A: Mabinogion Fourth-Branch/Taliesin figures + MacCulloch Tuatha."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wave import run

FILES = {
    "mab3": "evidence/rhiannon/guest-mabinogion-vol3-gutenberg.txt",
    "macc": "evidence/rhiannon/macculloch-religion-ancient-celts-1911.txt",
}

ERA_MAB = 1350   # Red Book of Hergest
ERA_MACC = 1911  # MacCulloch secondary attestation (flagged in notes)

NODES = [
    dict(id="math", label="Math fab Mathonwy", tradition="Welsh myth (Mabinogion)",
         era=ERA_MAB, note="Lord of Gwynedd in the Fourth Branch; the name-making and flower-making uncle."),
    dict(id="gwydion", label="Gwydion", tradition="Welsh myth (Mabinogion)",
         era=ERA_MAB, note="Math's sister's son; magician of the Fourth Branch, maker of Blodeuwedd, trickster of Pryderi."),
    dict(id="llew-llaw-gyffes", label="Llew Llaw Gyffes", tradition="Welsh myth (Mabinogion)",
         era=ERA_MAB, note="Aranrod's baptized son 'of the skilful hand'; Lleu. Blodeuwedd's husband, Gronw's victim."),
    dict(id="blodeuwedd", label="Blodeuwedd", tradition="Welsh myth (Mabinogion)",
         era=ERA_MAB, note="The woman made of flowers for Llew; her betrayal turns her into the owl."),
    dict(id="dylan", label="Dylan ail Ton", tradition="Welsh myth (Mabinogion)",
         era=ERA_MAB, note="Aranrod's sea-child, baptized into the sea at birth."),
    dict(id="aranrod", label="Aranrod", tradition="Welsh myth (Mabinogion)",
         era=ERA_MAB, note="Aranrod in the Edwards text (=Arianrhod); Math's footholder, mother of Dylan and Llew."),
    dict(id="taliesin", label="Taliesin", tradition="Welsh myth (Mabinogion / Hanes)",
         era=ERA_MAB, note="The reborn poet found in Elffin's weir; vol 3's closing tale."),
    dict(id="elphin", label="Elffin", tradition="Welsh myth (Hanes Taliesin)",
         era=ERA_MAB, note="He of the unlucky weir, finder of Taliesin; prisoner of Maelgwn."),
    dict(id="maelgwn", label="Maelgwn Gwynedd", tradition="Welsh myth/history (Hanes Taliesin)",
         era=ERA_MAB, note="Historical king of Gwynedd cast in the Taliesin tale as captor and judge."),
    # Tuatha (MacCulloch is a modern secondary witness: flagged)
    dict(id="nuada", label="Nuada of the Silver Hand", tradition="Irish myth (Tuatha De Danann)",
         era=ERA_MACC, note="Hand-lost king re-armed by Diancecht and Creidne in silver; witness here is MacCulloch 1911, secondary."),
    dict(id="diancecht", label="Diancecht", tradition="Irish myth (Tuatha De Danann)",
         era=ERA_MACC, note="Tuatha god of medicine: 'his name may mean swift in power'; silver-hand smith with Creidne."),
    dict(id="miach", label="Miach", tradition="Irish myth (Tuatha De Danann)",
         era=ERA_MACC, note="Diancecht's son who grew flesh where the father could only forge silver."),
    dict(id="goibniu", label="Goibniu", tradition="Irish myth (Tuatha De Danann)",
         era=ERA_MACC, note="Smith of the Tuatha; his weapons fail not."),
    dict(id="dagda", label="The Dagda", tradition="Irish myth (Tuatha De Danann)",
         era=ERA_MACC, note="'Good god' of the Tuatha, cauldron and club."),
    dict(id="manannan", label="Manannan mac Lir", tradition="Irish myth (Tuatha De Danann)",
         era=ERA_MACC, note="Sea-lord named in the euhemerist lists; witness MacCulloch 1911."),
    dict(id="brigit", label="Brigit", tradition="Irish myth (Tuatha De Danann)",
         era=ERA_MACC, note="Daughter of the Dagda; fire and poetry; saint's shadow over the goddess."),
    dict(id="morrigan", label="The Morrigan", tradition="Irish myth (Tuatha De Danann)",
         era=ERA_MACC, note="Battle-crow of the Tuatha; prophecy before the second battle of Moytura."),
    dict(id="balor", label="Balor", tradition="Irish myth (Fomorians)",
         era=ERA_MACC, note="Death-eyed Fomorian king, slain by his grandson at Moytura."),
    dict(id="lugh", label="Lugh", tradition="Irish myth (Tuatha De Danann)",
         era=ERA_MACC, note="Samildanach ('many-skilled'); Balor's grandson and slayer."),
]

MAB = "[21] Mabinogion vol 3, trans. Guest"
MAC = "[23] MacCulloch, Religion of the Ancient Celts"

EDGES = [
    dict(frm="math", to="gwydion", type="kinship", title="The sister's son at court",
         file="mab3", anchor=r"Gwydion (?:the|\w{0,30})? ?son of", source_id=21, source_ref=MAB, era=1350),
    dict(frm="gwydion", to="llew-llaw-gyffes", type="interaction", title="The name given at the fish-weir",
         file="mab3", anchor=r"Llew Llaw Gyffes be he called henceforth", source_id=21, source_ref=MAB, era=1350),
    dict(frm="gwydion", to="blodeuwedd", type="creation", title="The woman conjured from flowers",
         file="mab3", anchor=r"flowers of the oak.{0,200}?Blodeuwedd|Blodeuwedd.{0,200}?flowers of the oak", source_id=21, source_ref=MAB, era=1350),
    dict(frm="llew-llaw-gyffes", to="blodeuwedd", type="marriage", title="Flower-bride taken home",
         file="mab3", anchor=r"Blodeuwedd.{0,120}?(?:wife|wed)", source_id=21, source_ref=MAB, era=1350),
    dict(frm="aranrod", to="dylan", type="kinship", title="Baptized into the sea",
         file="mab3", anchor=r"Dylan is the name I will give him", source_id=21, source_ref=MAB, era=1350),
    dict(frm="aranrod", to="llew-llaw-gyffes", type="kinship", title="The unconceived son",
         file="mab3", anchor=r"Aranrod.{0,200}?Llew|Llew.{0,200}?Aranrod", source_id=21, source_ref=MAB, era=1350),
    dict(frm="taliesin", to="elphin", type="interaction", title="Found in the weir",
         file="mab3", anchor=r"Taliesin.{0,200}?(?:weir|Elffin)|(?:weir|Elffin).{0,200}?Taliesin", source_id=21, source_ref=MAB, era=1350),
    dict(frm="maelgwn", to="elphin", type="conflict", title="The captor of the unlucky weir",
         file="mab3", anchor=r"Maelgwn.{0,200}?Elffin|Elffin.{0,200}?Maelgwn", source_id=21, source_ref=MAB, era=1350),
    dict(frm="gwydion", to="pryderi", type="conflict", title="Pigs tricked out of Dyfed",
         file="mab3", anchor=r"Gwydion.{0,300}?Pryderi|Pryderi.{0,300}?Gwydion", source_id=21, source_ref=MAB, era=1350),
    # Tuatha cluster (witness: MacCulloch)
    dict(frm="nuada", to="diancecht", type="interaction", title="The silver hand",
         file="macc", anchor=r"fashioned a silver hand for Nuada", source_id=23, source_ref=MAC, era=1911),
    dict(frm="miach", to="diancecht", type="kinship", title="Flesh outgrows silver",
         file="macc", anchor=r"Diancecht.{0,200}?Miach|Miach.{0,200}?Diancecht", source_id=23, source_ref=MAC, era=1911),
    dict(frm="goibniu", to="nuada", type="interaction", title="The smith's unfailing weapons",
         file="macc", anchor=r"Goibniu", source_id=23, source_ref=MAC, era=1911),
    dict(frm="dagda", to="brigit", type="kinship", title="Daughter of the good god",
         file="macc", anchor=r"Brigit.{0,150}?Dagda|Dagda.{0,150}?Brigit", source_id=23, source_ref=MAC, era=1911),
    dict(frm="manannan", to="dagda", type="interaction", title="The sea-lord among the Tuatha",
         file="macc", anchor=r"Manannan.{0,200}?Tuatha|Tuatha.{0,200}?Manannan", source_id=23, source_ref=MAC, era=1911),
    dict(frm="balor", to="lugh", type="conflict", title="The death-eye meets the sling",
         file="macc", anchor=r"Balor.{0,250}?Lugh|Lugh.{0,250}?Balor", source_id=23, source_ref=MAC, era=1911),
    dict(frm="morrigan", to="dagda", type="interaction", title="Prophecy before Moytura",
         file="macc", anchor=r"Morrigan.{0,250}?Dagda|Dagda.{0,250}?Morrigan", source_id=23, source_ref=MAC, era=1911),
    dict(frm="nuada", to="lugh", type="interaction", title="The maimed king yields the host",
         file="macc", anchor=r"Nuada.{0,600}?Lugh|Lugh.{0,600}?Nuada", source_id=23, source_ref=MAC, era=1911),
         # cross-tradition: Brigit's double
         dict(frm="epona", to="brigit", type="analogy", title="Goddess into saint, twice",
         file="macc", anchor=r"Brigit.{0,800}?(?:saint|St\.)", source_id=23, source_ref=MAC, era=1911),
]

if __name__ == "__main__":
    run(NODES, EDGES, FILES)
