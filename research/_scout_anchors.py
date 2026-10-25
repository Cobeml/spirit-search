"""Queue-work anchor scouting: print mention contexts for the thin-queue names.
Read-only; each match line capped. Used to pick slice anchors before writing the
batch scripts."""
import re, os

EV = '/home/cobe-liu/Developing/spirit-search/evidence/'

JOBS = [
    ('alexander-hamilton', ['weems_life_of_washington_archive_org_1800_djvu.txt',
                            'weems-life-of-washington-1800s-archive-full.txt'], 'Hamilton', 6),
    ('benedict-arnold', ['weems_life_of_washington_archive_org_1800_djvu.txt'], 'Arnold', 5),
    ('numa-pompilius', ['plutarch-lives-dryden-clough-gutenberg.txt'], 'Numa', 4),
    ('romulus', ['plutarch-lives-dryden-clough-gutenberg.txt'], 'Romulus', 4),
    ('cato-elder', ['plutarch-lives-dryden-clough-gutenberg.txt'], 'Cato', 4),
    ('diancecht', ['macculloch-religion-ancient-celts-1911.txt'], r'Dian[c ]?[Cc]echt', 4),
    ('goibniu', ['macculloch-religion-ancient-celts-1911.txt'], r'Goibniu|Gobniu', 4),
    ('dagda', ['macculloch-religion-ancient-celts-1911.txt'], 'Dagda', 4),
    ('brigit', ['macculloch-religion-ancient-celts-1911.txt'], 'Brigit', 4),
    ('miach', ['macculloch-religion-ancient-celts-1911.txt'], 'Miach', 3),
    ('manannan', ['macculloch-religion-ancient-celts-1911.txt'], r'Manann[aá]n', 4),
    ('morrigan', ['macculloch-religion-ancient-celts-1911.txt'], r'Morrigan|Morrigu', 4),
    ('balor', ['macculloch-religion-ancient-celts-1911.txt'], 'Balor', 4),
    ('math', ['macculloch-religion-ancient-celts-1911.txt',
              'guest-mabinogion-1877-full.txt',
              'guest-mabinogion-vol3-gutenberg.txt'], r'Mathonwy|Math vab|Math son|Math ', 4),
    ('dylan', ['macculloch-religion-ancient-celts-1911.txt', 'guest-mabinogion-1877-full.txt'], 'Dylan', 3),
    ('aranrod', ['guest-mabinogion-1877-full.txt'], 'Aranrod', 3),
    ('maelgwn', ['guest-mabinogion-1877-full.txt'], 'Maelgwn', 3),
    ('tethys', ['hesiod-evelynwhite-gutenberg348.txt'], 'Tethys', 3),
    ('theia', ['hesiod-evelynwhite-gutenberg348.txt'], 'Theia', 3),
    ('crius', ['hesiod-evelynwhite-gutenberg348.txt'], r'Crius|Crios', 3),
]


def find_file(fn):
    for root, _, fns in os.walk(EV):
        if fn in fns:
            return os.path.join(root, fn)
    return None


for node, files, pat, cap in JOBS:
    print('=' * 76)
    print(node)
    rx = re.compile(pat)
    for fn in files:
        fp = find_file(fn)
        if not fp:
            print(f'  !! file not found: {fn}')
            continue
        raw = open(fp, encoding='utf-8', errors='ignore').read()
        sq = re.sub(r'\s+', ' ', raw)
        shown = 0
        for m in rx.finditer(sq):
            s = max(0, m.start() - 130)
            e = min(len(sq), m.end() + 260)
            print(f'  [{fn[:22]}] ...{sq[s:e]}...')
            shown += 1
            if shown >= cap:
                break
