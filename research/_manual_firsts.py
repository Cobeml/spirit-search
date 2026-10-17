#!/usr/bin/env python3
"""Manual first-highlight curation: hand-picked anchors for the stubborn nodes.

Each entry: node_id -> (file, [anchor regexes in priority order]). For each
anchor, the first non-TOC sentence-bounded slice containing the node's alias
wins. Nodes whose every pattern fails keep their current highlight (flagged).
"""
import json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nameinfra import FILES, SQMAP, positions, expand_span, junk_score, register_file_source, add_quote, GP, LP
from _audit_relevance import alias_patterns

TODAY = "2026-10-15"

TOCISH = re.compile(r"(?i)(\b[i]{1,3}\b\s*\.|\b[ivx]+\.\s).{0,60}?(\b[i]{1,3}\b\s*\.|\b[ivx]+\.\s)|\bcontents\b|comparison of .{0,40} with|digitized by the internet archive")

def sentence_pair(t, i):
    s = expand_span(t, max(0, i - 120), i + 400, max_back=400, max_fwd=450)
    if len(s) < 80:
        s = expand_span(t, max(0, i - 300), i + 500, max_back=1200, max_fwd=700)
    if len(s) < 80:
        s = expand_span(t, max(0, i - 200), i + 60, max_fwd=700)
    return s

def alias_ok(text, pats):
    tc = " " + re.sub(r"[^a-z0-9]+", " ", text.lower()).strip() + " "
    tsq = re.sub(r"\s+", "", text.lower())
    return any(p["na"] in tc or (p["long"] and p["sq"] in tsq) for p in pats)

# file keys -> relative paths (all already in FILES)
OVERRIDES = {
    # Hesiod
    "aphrodite": ("theog", [r"gods and men call aphrodite"]),
    "helios": ("theog", [r"and theia was subject in love to hyperion"]),
    "selene": ("theog", [r"and theia was subject in love to hyperion"]),
    "eos": ("theog", [r"and theia was subject in love to hyperion"]),
    "hera": ("theog", [r"queenly hera of argos"]),
    "athene": ("theog", [r"bright-eyed athene"]),
    "themis": ("theog", [r"reverend themis"]),
    "coeus": ("theog", [r"phoebe came to the desired embrace of coeus"]),
    "phoebe": ("theog", [r"phoebe came to the desired embrace of coeus"]),
    "pontus": ("theog", [r"the fruitless deep with his raging swell"]),
    "cronos": ("theog", [r"rhea was subject in love to cronos"]),
    "rhea": ("theog", [r"rhea was subject in love to cronos"]),
    "oceanus": ("theog", [r"bare deep-swirling oceanus"]),
    # Iliad
    "xanthus-balius": ("il", [r"the fleet horses xanthus and balius"]),
    "helen": ("il", [r"helen, daughter of aegis-bearing jove"]),
    "odysseus": ("il", [r"ulysses peer of gods in counsel"]),
    "patroclus": ("il", [r"patroclus who was close by him|son of menoetius"]),
    "menelaus": ("il", [r"menelaus son of atreus"]),
    "agamemnon": ("il", [r"agamemnon, king of men", r"agamemnon rose in anger"]),
    "idomeneus": ("il", [r"the famous spearsman idomeneus led the cretans"]),
    "diomedes": ("il", [r"diomed son of tydeus see mars"]),
    "priam": ("il", [r"hold priam back"]),
    # Ginzberg
    "adam": ("gz", [r"after adam was created", r"adam our father"]),
    "eve": ("gz", [r"eve was but as an ape compared with adam"]),
    "cain": ("gz", [r"cain slew his brother"]),
    "noah": ("gz", [r"call his name noah, for he will be left"]),
    "isaac": ("gz", [r"isaac was born unto his aged parents"]),
    "jacob": ("gz", [r"jacob busy preparing a dish of lentils"]),
    "joseph": ("gz", [r"they noticed that joseph was missing"]),
    "abraham": ("gz", [r"abraham our father came"]),
    # Mabinogion
    "pwyll": ("pwyll", [r"pwyll.{0,20}prince of dyved|lord over dyved"]),
    "gwawl": ("pwyll", [r"gwawl"]),
    "math": ("v3", [r"math the son of mathonwy was lord over gwynedd"]),
    "llew-llaw-gyffes": ("v3", [r"llaw gyffes be he called henceforth"]),
    "elphin": ("v3", [r"said elphin"]),
    "taliesin": ("v3", [r"taliesin .{0,80}(said|spake|was)"]),
    # Edda
    "nithuth": ("edda", [r"there was a king in sweden named nithuth"]),
    "bothvild": ("edda", [r"there was a king in sweden named nithuth"]),
    "volundr": ("edda", [r"volund .{0,120}(smith|nithuth|mighty)|the story of volund"]),
    "fafnir": ("edda", [r"rode to slay fafnir"]),
    "sigurd": ("edda", [r"birds to sigurth after the slaying of fafnir"]),
    "hel": ("edda", [r"now hel has the half"]),
    "guthrun": ("edda", [r"guthrun .{0,80}(spake|said|wept)", r"\bguthrun\b"]),
    "regin": ("edda", [r"regin .{0,90}(smith|foster|brother)", r"\bregin\b"]),
    "atli": ("edda", [r"atli .{0,80}(buthli|brother of brynhild|spake)", r"\batli\b"]),
    # Apuleius (Adlington spells her 'Psyches')
    "psyche": ("apul", [r"psyches .{0,250}(fair|beautiful|younger|daughter)", r"cupid and psyches\. there was sometimes", r"\bpsyche\b|\bpsyches\b"]),
    "cupid": ("apul", [r"cupid being more and more in love"]),
    # Weems
    "george-washington": ("weems", [r"great washington was born"]),
    "thomas-jefferson": ("weems", [r"secretary of foreign aifairs", r"berkley, jefferson"]),
    "henry-knox": ("weems", [r"gen\. knox, secretary of war"]),
    "james-wilson": ("weems", [r"joliii rtitledge, james wilson, john cushing", r"james wilson"]),
    "charles-lee": ("weems", [r"general lee.{0,40}said washington|for god.{0,20}sake, general lee"]),
    "alexander-hamilton": ("weems", [r"col\. hamilton, secretary of the treasury"]),
    # Livy
    "cincinnatus": ("livy", [r"by universal consent .{0,60}cincinnatus was called", r"cincinnatus .{0,120}(dictator|farm|four acres|plough)"]),
    # Plutarch (TOC excluded by TOCISH)
    "valerius-publicola": ("plu", [r"poplicola .{0,120}(was|died|when|banish)", r"valerius poplicola"]),
    "fabius-maximus": ("plu", [r"fabius .{0,120}(was|son of|delay)", r"fabius maximus"]),
    "marcius-coriolanus": ("plu", [r"coriolanus .{0,120}(was|son|when)", r"marcius coriolanus"]),
    "marcellus": ("plu", [r"marcellus .{0,120}(was|son of|when)", r"marcellus"]),
    "aemilius-paullus": ("plu", [r"aemilius .{0,120}(was|paulus)", r"aemilius paulus"]),
    # Aeschylus
    "erinyes": ("eum", [r"near the suppliant are the furies", r"the furies .{0,80}(sleep|dream)"]),
    # Freud summary of Hoffmann (translator spells him 'Nathaniel')
    "nathanael": ("sand", [r"nathaniel"]),
    # Horace commentary carries the Quinquatrus (Ovid Fasti file not on disk)
    "minerva": ("horace", [r"minerva .{0,200}(quinquatrus|festival|school)", r"\bminerva\b"]),
    "diana": ("theog", [r"artemis who delights in arrows"]),
    "pandora": ("theog", [r"pandora"]),
}

# map override file keys to real FILES keys
FILEALIAS = {
    "theog": "evidence/epimetheus/hesiod-evelynwhite-gutenberg348.txt",
    "il": "evidence/machaon/homer-iliad-butler-mb.txt",
    "gz": "evidence/lilith/ginzberg-legends1-gutenberg.txt",
    "v3": "evidence/rhiannon/guest-mabinogion-vol3-gutenberg.txt",
    "pwyll": "evidence/rhiannon/pwyll-branch.txt",
    "edda": "evidence/volundr/bellows-poetic-edda-1923-full.txt",
    "apul": "evidence/rhiannon/apuleius-golden-ass-adlington-gutenberg.txt",
    "weems": "evidence/washington/weems-life-of-washington-1800s-archive-full.txt",
    "livy": "evidence/cincinnatus/livy3-roberts-wikisource.txt",
    "plu": "evidence/_corpus/plutarch-lives-dryden-clough-gutenberg.txt",
    "eum": "evidence/athene/aeschylus-eumenides-smyth-theoi.html",
    "sand": "evidence/sandmann/freud-cp4-1925-full-djvu.txt",
    "horace": "evidence/genius/horace_epistles_smart_wikisource.txt",
}

g = json.load(open(GP))
ledger = json.load(open(LP))
byid = {n["id"]: n for n in g["nodes"]}
pats_of = {n["id"]: alias_patterns(n) for n in g["nodes"]}

def resolve_file(key):
    return FILEALIAS.get(key)

fixed = missed = 0
for nid, (fkey, patterns) in OVERRIDES.items():
    n = byid.get(nid)
    if not n:
        continue
    fp = resolve_file(fkey)
    if not fp or fp not in FILES:
        print(f"  !! {nid}: file not found ({fkey})")
        missed += 1
        continue
    t = FILES[fp]
    tl = t.lower()          # length-preserving: match indices valid on t
    chosen = None
    for pat in patterns:
        for m in re.finditer(pat, tl):
            s = sentence_pair(t, m.start())
            if len(s) < 60 or TOCISH.search(s) or junk_score(s) > 0.55:
                continue
            if not alias_ok(s, pats_of[nid]):
                continue
            chosen = (s, m)
            break
        if chosen:
            break
    if not chosen:
        print(f"  !! {nid}: no pattern hit")
        missed += 1
        continue
    s, m = chosen
    sid = register_file_source(ledger, fp, TODAY)
    src = next(x for x in ledger["sources"] if x["id"] == sid)
    add_quote(ledger, sid, s, TODAY)
    key = re.sub(r"\W+", "", s.lower())[:80]
    hls = n.get("highlights", [])
    kept = [h for h in hls if re.sub(r"\W+", "", h["text"].lower())[:80] != key]
    n["highlights"] = [{"text": s, "source_id": sid, "source_title": src["title"],
                        "source_url": src.get("url", ""), "direct": True,
                        "manual": True}] + kept[:4]
    fixed += 1
    print(f"  ok {nid}: {s[:90]!r}")

shutil.copy(GP, GP.with_suffix(".json.bak7"))
json.dump(g, open(GP, "w"), indent=1, ensure_ascii=False)
json.dump(ledger, open(LP, "w"), indent=1, ensure_ascii=False)
print(f"manual curation: {fixed} fixed, {missed} missed")
