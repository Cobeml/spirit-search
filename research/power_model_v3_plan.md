# power model v3 — plan and recommendations (for Cobe's ruling, 2026-10-27)

Cobe's diagnosis: fixed pools + shares is a zero-sum pie; authority is not a fixed
quantity of energy, it matters WHAT one has authority over and then dividing that
down into the energy it commands. Split power into VIRTUAL (greatest attested feat
in myth/fiction, energy it would take) and PHYSICAL (actually commanded: army,
money, capital, office). Edge transfers must carry the type with them (Zeus's
virtual power to his children is virtual; Constantine's real power routed to God is
real). Deliverable requested: plan before execution. This document is the plan; the
graph and power_claims.json are untouched.

## 1. Why the current numbers are not comparable (diagnosis, with evidence)

`direct = pool x share x witness` answers the question "what fraction of a modern
pool's activity descends from this figure". It never asks what the figure commanded.
Consequences measured in the live claims file:

- Zeus P_authority share 0.5 -> 7.50 TW; God P_authority share 0.0001 -> 1.50 GW.
  Same pool, same estimator, 5,000x apart, both numbers arbitrary. Neither is a
  measurement of authority; both are share-of-pie claims set in different pricing
  regimes (early industrial-descent batches vs the 2026-10-21 Tier-2 anchor).
- Nine nodes read 1.5 TW with NO claim of their own, purely the unreviewed 0.2
  kinship/transmission default routing out of Zeus (cronos, rhea, themis, mnemosyne,
  hecate, styx, dionysus, sarpedon) and Prometheus (iapetus); hera reads 60 GW as
  0.2 x hephaestus. `_audit_power.py` section D lists exactly these.
- Pool choice is a 40,000x lever (P_energy 20 TW to P_amulet 0.5 MW), so a share
  number is meaningless without its pool, and shares were set across two regimes
  three orders of magnitude apart.

## 2. Model v3: two ledgers, no pools as multiplicands

Every node carries two independent, evidence-cited quantities:

    PHYSICAL  = the energy throughput of what the witness documents them commanding
                (troops, treasury, land, plant, office, institution), bottom-up,
                measured in their own era
    VIRTUAL   = the energy scale of the domain the witness assigns them to command,
                plus the greatest attested single feat as a reported bound

Pools are demoted to reporting denominators only ("X MW is Y% of modern P_authority
activity"), never multiplicands. Shares cease to exist. Witness strength becomes a
confidence grade displayed on the panel, not a multiplier (multiplying a physics
estimate by documentation quality mixes units).

### 2a. PHYSICAL recipe

1. Inventory commanded capital from the fetched witnesses, verbatim, per claim:
   troops, fleets, annona/grain, estates, workshops/engines, treasuries, offices.
2. Convert with cited coefficients (new data file `research/power_coefficients.json`,
   every coefficient carrying its source):
   - deployed soldier 15 kW (0.2 kW metabolism + fuel, transport, ammunition,
     supply-chain overhead; US DoD ~13 kW/deployed soldier is the calibration
     point)
   - premodern agriculture 0.3 kW/ha; installed engine 745.7 W/hp; annona grain
     15 MJ/kg; era treasury via state-share-of-GDP anchors
3. Record both lenses where they differ:
   - `phys_watts_era` — what they commanded in their time (this is the primary
     number; no population scaling is applied, because the number already is
     era-local)
   - `phys_watts_descendant` — modern activity that descends from the figure
     (Watt -> electrification), reported separately, never summed into the axis
4. Each value cites evidence file + locator + coefficient id. Uncited value = audit
   failure.

Worked examples (computed):

| figure | command documented | phys watts |
|---|---|---|
| Washington, peak army ~17,000 | Weems/Boswell | 255 MW |
| Washington, Mount Vernon 3,237 ha | Weems | 1.0 MW |
| Sulla, ~6 legions + auxiliaries (40,000) | Plutarch | 600 MW |
| Constantine, imperial army ~400,000 | (to fetch, Ammianus/Eusebius) | 6.0 GW |
| Constantine, Rome annona (~200k t/yr) | (to fetch) | 95 MW |
| Henry Knox, artillery corps ~1,000 | Weems | 15 MW |
| Boulton & Watt installed engines by 1800 (7,500 hp) | (EB1911/Boswell) | 5.6 MW |

### 2b. VIRTUAL recipe — and the honest problem with it

Literal "energy the feat would take" was computed across traditions. It does not
rank figures; it exposes three failure classes:

| feat (witness) | energy | sustained watts |
|---|---|---|
| Zeus/Thor single bolt (1 GJ, 30 us) | 1 GJ | 33 TW peak |
| Zeus/Thor storm system (1e17 J, 6 h) | 100 PJ | 4.6 TW |
| Poseidon earthquake M8 / M9 | 63 PJ / 2.0 EJ | 1.05 PW / 33 PW |
| Atlas holds the sky | static | 0 W sustained (50.5 EJ to raise 1 m) |
| God, flood to cover mountains (Gen 7-8) | 7.1e24 J | 2.04 EW |
| God parts the sea (Exod 14) | 490 GJ | 11.4 MW |
| Joshua/God, sun stands still (Josh 10:13, on disk) | 2.1e29 J | 2.1e29 W |
| Jesus calms the storm (Mark 4) | 1.0 PJ | 1.67 TW |
| Jesus feeds 5,000 (John 6) | 52 GJ | 2.4 MW |
| Jesus water to wine (John 2) | 60 MJ | 60 MW |
| Prometheus brings fire (torch) | 10 MJ | 10 MW |

Classes: (i) peak-vs-sustained swings 7 orders of magnitude on the same feat;
(ii) static holds have no sustained power at all; (iii) cosmological feats
(flood 2 EW, sun-stop 2.1e29 W) out-watt everything ever measured by 5+ orders and
make the axis a theology contest. So literal feat energy alone is a REPORTED BOUND,
not a ranking metric.

Recommended virtual metric — report a pair, never one blended number:

    virt_feat      {energy, class, duration, formula, excerpt}  -- greatest attested
                   single act; uncapped; flagged above planetary class
    virt_domain    {domain, era_budget_watts, coverage_frac, basis}  -- the physical
                   budget of the domain the witness assigns (Zeus: lightning over
                   his attributed territory, global lightning ~44 GW x the Greek
                   world's share; Poseidon: Aegean seismic/tidal budget; Yahweh:
                   the created order's own budgets, planetary class -> flagged),
                   times a RULED coverage fraction

`virt_domain` is the comparable, rankable number; `virt_feat` is the literal
achievement Cobe asked for and the audit trail for the domain claim. Coverage
fractions are rulings, per figure, recorded like the old shares but with an explicit
domain instead of a pie.

Cap policy: any feat at or above planetary class (Earth insolation 1.74e17 W,
internal heat flow 47 TW) gets `scale_class: cosmological`, displays symbolically
("unbounded"), and is excluded from size/rank encodings. The log states the feat and
its formula; no fabricated comparable number.

### 2c. Edge transfers keep their type

Each edge carries explicit `virt_frac` and `phys_frac` (both default ABSENT = 0, no
implicit 0.2 anywhere; the current default is the single biggest distortion in the
live numbers). Direction convention unchanged: `from` collects from `to`.

- Zeus -> Heracles: virt_frac only. Zeus -> Athene: virt_frac only.
- Constantine -> God: phys_frac only (endowments, basilicas, state enforcement of
  doctrine). At an initial ruled 3% of Constantine's 6 GW that is 180 MW of REAL
  power reaching God; the fraction is his to set.
- Sulla -> the treasury state: phys. Prometheus -> humanity: virtual to the arts
  (the old 12 TW reading was the pie; the feat is a torch, the descendant
  attribution is a separate reported line).

### 2d. What happens to the site

- Node panel: two readouts (PHYSICAL W / VIRTUAL W) with the feat line, the formula,
  the domain budget, coefficient citations, and the confidence grade. No single
  blended "total".
- Size toggle becomes physical / virtual / legacy-v2-pool-share (kept for
  comparison until the migration completes).
- Time axis: era-local absolute values; optional "share of their era's economy"
  lens using GDP anchors (to be added beside pop_anchors).
- Review queue: nodes whose virtual domain needs a coverage ruling.

## 3. Migration plan (staged, nothing destructive)

1. Rulings on section 4 (one line each).
2. `research/power_coefficients.json` + `research/virt_feats.json` (data, cited).
3. `research/power_model_v3.py` writing NEW fields (`phys_watts_era`,
   `phys_watts_descendant`, `virt_feat_*`, `virt_domain_watts`, `power_v3_status`)
   while leaving v2 fields frozen for comparison. Claims v3 file:
   `power_claims_v3.json` (per-node physical inventories, domain coverage rulings,
   typed edge fractions).
4. PILOT, 12 nodes, old-vs-new calibration table posted before anything else moves:
   zeus, thor, poseidon, atlas, prometheus, inana, apollo, heracles, god, jesus,
   washington, sulla + two transfer demos (constantine -> god phys; croesus ->
   delphi as a classic real-to-temple transfer).
5. Waves of ~20 nodes; each wave re-runs `_audit_power.py` extended with v3 gates:
   uncited phys value, uncited virt formula, edge fraction without transfer type,
   cosmological feat priced numerically, node with neither ledger populated.
6. Only after the pilot table is accepted: flip the site default lens to v3 and
   freeze v2.

## 4. Open rulings needed (before execution)

1. Virtual: literal feat only (V1) / domain-command only (V2) / pair, feat reported
   + domain ranked (V3) — recommendation: V3.
2. Cosmological feats: symbolic "unbounded" flag (recommendation) or a hard cap at
   Earth's insolation scale?
3. Physical coefficients: endorse the 15 kW/deployed-soldier default and the
   coefficient file as the machine-readable source of truth?
4. Static holds (Atlas): 0 W sustained + work figure reported (recommendation), or a
   "support power" convention?
5. Pools: delete from pricing, keep as report denominators (recommendation), or
   delete entirely?
6. Sizing: three-way lens toggle (physical / virtual / legacy) — recommendation — or
   force one?
7. Add constantine and croesus as nodes for the transfer demos (recommendation: yes)?
8. Witness strength: confidence grade, not a multiplier (recommendation)?
9. Domain coverage fractions: ruled per figure into power_claims_v3.json, or derived
   mechanically from the witness's territorial claims (recommendation: ruled, with a
   mechanical default proposal filed per node)?

## 5. Effort

Pilot 12 nodes: one session (evidence is on disk for all but Constantine/Croesus,
which need one fetch each). Full 208 nodes: 10-12 waves, physical ledger first for
flesh record (already documented), virtual second per tradition. No graph.json
writes until the rulings in section 4 arrive.

# RULINGS APPLIED (Cobe, 2026-10-27, second reply) — spec v2

1. VIRTUAL = the single highest attested feat, physics computed, PEAK AND SUSTAINED
   both reported. Domain-budget attribution dropped (Cobe: too abstract and static;
   accepted — the feat number is a literal statement, which is what the log needs).
2. NO CAP. Cosmological-scale feats are priced numerically where physics is defined
   (deluge 2.07 EW, sun-stop 2.1e29 W). Only feats with no defined energy class
   (creation ex nihilo, resurrection, plague) are reported `undefined` with the
   reason; that is an absence of physics, not a cap. Site size encoding must be
   log10 of watts (30 orders of span).
3. PHYSICAL is componentized and must be COMPLETE: every significant source of power
   accounted for, class by class — human (per-head, equipment-tiered), weapons,
   tools, natural resources, capital stock, finance. Each node's inventory either
   values a class or records it as "none documented". 15 kW/deployed-soldier is the
   default *human+supply* coefficient ONLY; weapon rows are added wherever the
   witness documents them (batteries, fleets, engines), resource rows where lands,
   mines or oil are documented.
4. Static holds = 0 W sustained; the work figure is reported separately (Atlas:
   5.05e19 J to raise the atmosphere 1 m).
5. Constantine and Croesus added as demo nodes (executed as pilot data; graph write
   pending acceptance).
6. TRANSFERS are typed per pool and may be multi-hop WITH CONSERVATION: an edge
   carries `virt_frac` and/or `phys_frac`; a node transmits only from the matching
   pool; physical power received by transfer may be re-transmitted from the physical
   pool (God receiving the Constantinian endowment then passing a share on), with
   sum(outbound fractions) <= 1 per pool per node; cycles cut at the weakest link by
   era order and flagged. No implicit defaults anywhere (the 0.2 kinship default is
   deleted).

## Pilot results (research/_power_v3_pilot.py -> power_v3_pilot.json)

14 nodes, all excerpts anchor-verified, transfers routed and conservation-checked.

| node | v2 | v3 physical | v3 virtual |
|---|---|---|---|
| zeus | 7.52 TW | - | 1.02 EW (theomachy sea-boil, thermal) |
| god | 1.50 GW | 272.9 MW (received: Constantinian endowment) | 2.07 EW (deluge) |
| inana | 300 GW | - | 30.1 TW (Mount Ebih fractured) |
| thor | 0 W (unpriced) | - | 26.7 TW serpent-lift / 23 kW blow total |
| poseidon | 0 W (unpriced) | - | 1.67 TW (storm laid flat) |
| jesus | 5 MW | 81.9 MW (received, multi-hop) | 1.67 TW (storm calmed) |
| prometheus | 14.25 TW | - | 10 MW (torch) |
| heracles | 3.75 GW | - | 59 MW (Augean diversion) |
| apollo | 7.50 GW | - | 10 kW (Python); plague undefined |
| atlas | 376.5 GW | - | 0 W sustained (5.05e19 J to raise 1 m) |
| washington | 180 GW | 46 MW (Weems's in-witness low) | none attested |
| sulla | 6.08 GW | 600 MW | none attested |
| constantine (new) | - | 9.10 GW | none attested |
| croesus (new) | - | 300 MW | none attested |

Transfer demos: constantine->god phys 3% = 272.9 MW; god->jesus phys 30% of received
= 81.9 MW (the clarification's case); croesus->apollo phys 10% = 30 MW (Herodotus
1.50-51 dedications); zeus->heracles virt 20% = 203.7 PW.

## Residual questions for the wave pass

- Feat-reading spread (Thor 23 kW vs 26.7 TW): report the pair with the largest act
  as the headline, keep the literal total in the row.
- Undefined-class feats: symbolic row or unlisted.
- Weapon/resource rows: confirm they enter as separate components.
- Transfer shares: ruled per edge (current values are proposals).
- Witness gaps: Washington's peak command, Croesus's host/mint, Constantine's
  establishment range (Gibbon 583,000-645,000).
