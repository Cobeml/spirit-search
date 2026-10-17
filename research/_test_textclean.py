#!/usr/bin/env python3
"""Unit tests for _textclean on synthetic samples + real corpus files."""
import sys, re
sys.path.insert(0, 'research')
import _textclean as TC

fails = []
def check(name, cond, detail=""):
    status = "OK " if cond else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not cond:
        fails.append(name)

def S(x):
    return x or ""
    status = "OK " if cond else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not cond:
        fails.append(name)

# --- synthetic: boundary detection on cased text
s1 = "Now Zeus, king of the gods, made Metis his wife first, and she was wisest among gods and mortal men. But when she was about to bring forth the bright goddess Athene, Zeus craftily deceived her."
i = s1.find("Metis")
sent = S(TC.sentence_at(s1, i))
check("plain sentence", sent.startswith("Now Zeus") and sent.endswith("mortal men."), repr(sent[-40:]))

# verse number between sentences (KJV style)
s2 = "And all the days of Methuselah were nine hundred sixty and nine years: and he died. 5:28 And Lamech lived an hundred eighty and two years and begat a son. 5:29 And he called his name Noah."
sent = S(TC.sentence_at(s2, s2.find("Methuselah")))
check("verse-number skip", sent.startswith("And all the days") and sent.endswith("and he died."), repr(sent[-40:]))

# page number after period (Loeb style)
s3 = "Now Apollo wedded the fair Coronis, and they had a son, and Apollo loved the child. 176 Besides them Leucippus begat Arsinoe: with her Apollo had intercourse."
sent = S(TC.sentence_at(s3, s3.find("Coronis")))
check("page-num skip", sent.endswith("loved the child."), repr(sent[-40:]))

# Loeb mid-sentence page number
s4 = "he snatched the babe from the pyre and brought it to Chiron, the centaur, 178 by whom he was brought up and taught the arts of healing."
lo, hi = s4.find("snatched"), s4.find("healing") + 8
sl = S(TC.slice_clean(s4, lo, hi))
check("mid page-num strip", "178" not in sl, repr(sl[:60]))

# real quantity must survive
s5 = "The fleet was lost with almost all its men, nearly 200 of them, and the survivors sailed home by night."
sl = S(TC.slice_clean(s5, s5.find("fleet"), s5.find("night") + 5))
check("quantity preserved", "200" in sl, repr(sl[:80]))

# abbreviation guard
s6 = "At St. Paul's church the votaries gathered and prayed to the spirit of the place. Now the genius was said to dwell there."
sent = S(TC.sentence_at(s6, s6.find("votaries")))
check("St. not a boundary", sent.startswith("At St."), repr(sent[:40]))

# initials
s7 = "This edition was prepared by A. H. Clough, who compared the Greek. The translation follows Dryden throughout."
sent = S(TC.sentence_at(s7, s7.find("Clough")))
check("initials not split", "A. H. Clough" in sent, repr(sent[:50]))

# heading boundary
s8 = "BOOK I. Now Zeus was king of the immortals and ruled from Olympus."
sent = S(TC.sentence_at(s8, s8.find("Zeus")))
check("heading stripped", sent.startswith("Now Zeus"), repr(sent[:30]))

# leading locator
s9 = "(ll. 507-543) Now Iapetus took to wife the neat-ankled Clymene, daughter of Ocean, and went up with her into one bed."
sent = S(TC.sentence_at(s9, s9.find("Iapetus")))
check("locator prefix stripped", not sent.startswith("(ll"), repr(sent[:40]))

# --- scrub_text on stored junk
j1 = "The appointed hour \u200b was approaching when man in his turn was to go forth into the light of day."
j2 = "unde et Dido \x93litora litoribus contraria, fluctusque urbem\u2019 recitat.\u201d"
check("zero-width stripped", "\u200b" not in TC.scrub_text(j1))
check("mojibake mapped", "\u201c" in TC.scrub_text(j2), repr(TC.scrub_text(j2)))

# --- real corpus files
t = TC.load_case("evidence/machaon/iliad-butler-gutenberg1727.txt") if __import__('pathlib').Path("evidence/machaon/iliad-butler-gutenberg1727.txt").exists() else None
import pathlib
cands = list(pathlib.Path('evidence').rglob('*iliad*')) + list(pathlib.Path('evidence').rglob('*butler*mb*'))
if cands:
    t = TC.load_case(cands[0])
    i = t.find("sons of Aesculapius")
    sent = S(TC.sentence_at(t, i)) if i >= 0 else "ANCHOR NOT FOUND"
    check("iliad cased sentence", "Aesculapius" in sent and sent[:1].isupper(), f"file={cands[0].name} {sent[:80]!r}")
    check("PG header trimmed", "Project Gutenberg" not in t[:2000], repr(t[:60]))

# apollodorus (the 'married. 176' source)
cands = list(pathlib.Path('evidence').rglob('apollod*'))
if cands:
    t = TC.load_case(cands[0])
    i = t.find("Coronis")
    sent = S(TC.sentence_at(t, i)) if i >= 0 else "ANCHOR NOT FOUND"
    check("apollodorus cased", sent[:1].isupper(), f"file={cands[0].name} {sent[:90]!r}")

# kjv isaiah
cands = list(pathlib.Path('evidence').rglob('kjv-isaiah*'))
if cands:
    t = TC.load_case(cands[0])
    i = t.find("screech owl")
    if i < 0: i = t.find("owl")
    sent = S(TC.sentence_at(t, i)) if i >= 0 else "ANCHOR NOT FOUND"
    check("kjv verse slice", bool(sent) and sent[:1].isupper(), f"{sent[:80]!r}")

print()
print("FAILS:", fails if fails else "none")
sys.exit(1 if fails else 0)
