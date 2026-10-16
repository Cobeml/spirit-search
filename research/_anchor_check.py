#!/usr/bin/env python3
"""Anchor check for the manual first-highlight override table."""
import re

def ch(f):
    t = open(f, errors="replace").read()
    t = re.sub(r"<[^>]+>", " ", t) if t.count("<") > 100 else re.sub(r"[<>]", " ", t)
    return re.sub(r"\s+", " ", t).lower()

F = {
    "v1": ch("evidence/rhiannon/guest-mabinogion-vol1-gutenberg.txt"),
    "v3": ch("evidence/rhiannon/guest-mabinogion-vol3-gutenberg.txt"),
    "edda": ch("evidence/volundr/bellows-poetic-edda-1923-full.txt"),
    "apul": ch("evidence/rhiannon/apuleius-golden-ass-adlington-gutenberg.txt"),
    "weems": ch("evidence/washington/weems-life-of-washington-1800s-archive-full.txt"),
    "livy": ch("evidence/cincinnatus/livy3-roberts-wikisource.txt"),
    "plu": ch("evidence/_corpus/plutarch-lives-dryden-clough-gutenberg.txt"),
    "il": ch("evidence/machaon/homer-iliad-butler-mb.txt"),
    "eum": ch("evidence/athene/aeschylus-eumenides-smyth-theoi.html"),
    "sand": ch("evidence/sandmann/freud-cp4-1925-full-djvu.txt"),
}

TESTS = [
    ("pwyll", "v1", r"pwyll, prince of dyved"),
    ("gwawl", "v1", r"gwawl .{0,30}son of clud"),
    ("math", "v3", r"math .{0,20}son of mathonwy .{0,40}lord|math the son of mathonwy"),
    ("llew", "v3", r"llaw gyffes be he called henceforth"),
    ("elphin", "v3", r"elphin .{0,40}son of gwyddno|said elphin"),
    ("nithuth", "edda", r"there was a king in sweden named nithuth"),
    ("queen", "edda", r"the queen .{0,40}(said|spake).{0,80}volund"),
    ("guthrun", "edda", r"guthrun .{0,40}(daughter of giuki|giuki)"),
    ("regin", "edda", r"regin .{0,40}hreidmar|son of hreidmar"),
    ("fafnir", "edda", r"fafnir .{0,60}(hoard|dragon|serpent|slay)"),
    ("sigurd", "edda", r"sigurth .{0,40}(fafnir|regin)"),
    ("atli", "edda", r"atli .{0,40}(son of budli|budli)"),
    ("hel", "edda", r"\bhel\b .{0,80}half|half .{0,40}\bhel\b"),
    ("psyche", "apul", r"psyche .{0,80}(beauty|maiden|daughter)"),
    ("cupid", "apul", r"cupid .{0,80}(winged|love|youth)"),
    ("washington", "weems", r"washington was .{0,60}(but|born|then|appointed)"),
    ("jefferson", "weems", r"mr\. jefferson, secretary of foreign affairs"),
    ("knox", "weems", r"gen\. knox, secretary of war"),
    ("wilson", "weems", r"james wilson, john|, james wilson,"),
    ("lee", "weems", r"general lee"),
    ("hamilton", "weems", r"col\. hamilton, secretary of the treasury"),
    ("cincinnatus", "livy", r"cincinnatus"),
    ("poplicola", "plu", r"poplicola .{0,50}(valerius|was|son)|valerius poplicola"),
    ("fabius", "plu", r"fabius .{0,50}(was|son of|maximus)"),
    ("coriolanus", "plu", r"coriolanus .{0,50}(was|son)"),
    ("marcellus", "plu", r"marcellus .{0,50}(was|son)"),
    ("cato", "plu", r"cato .{0,50}(was born|the censor|when)"),
    ("aemilius", "plu", r"aemilius .{0,50}(paulus|was)"),
    ("balius", "il", r"balius"),
    ("helen", "il", r"helen, daughter|helen of the fair"),
    ("ulysses", "il", r"ulysses .{0,40}(counsel|peer|sage)"),
    ("patroclus", "il", r"patroclus .{0,40}son of menoetius"),
    ("menelaus", "il", r"menelaus .{0,40}son of atreus|valiant menelaus"),
    ("agamemnon", "il", r"agamemnon .{0,30}king of men|son of atreus, king of men"),
    ("idomeneus", "il", r"idomeneus .{0,40}cretan"),
    ("diomed", "il", r"diomed .{0,40}son of tydeus|tydeides"),
    ("erinyes", "eum", r"the furies"),
    ("athene", "eum", r"grey-eyed athene|grey-eyed athena|pallas athene"),
    ("nathanael", "sand", r"nathanael.{0,60}(letters|love|clara|childhood)"),
]

for label, fkey, pat in TESTS:
    t = F[fkey]
    m = re.search(pat, t)
    if m:
        print(f"{label:12s} [{fkey}] HIT | {t[max(0, m.start()-30):m.start()+130]!r}")
    else:
        print(f"{label:12s} [{fkey}] MISS")
