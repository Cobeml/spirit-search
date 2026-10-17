#!/bin/bash
# Repair chain: audit -> rebuild firsts -> toc fixup -> manual firsts -> reslice edges -> re-audit -> probe
set -e
cd /home/cobe-liu/Developing/spirit-search
echo "=== chain start $(date +%H:%M:%S) ==="
for s in _audit_relevance _rebuild_highlights _toc_fixup _manual_firsts _reslice_edges _audit_relevance _probe_fixability; do
  echo "=== $s $(date +%H:%M:%S) ==="
  /usr/bin/python3 "research/$s.py" 2>&1 | tail -15
done
echo "=== chain done $(date +%H:%M:%S) ==="
