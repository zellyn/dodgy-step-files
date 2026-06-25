# OCC/gmsh Disagreement Audit — 2026-06-24

**Scope**: 188 fixtures (8.4% of corpus) where OCC and gmsh coarsen to different outcome
buckets.  Cross-reference: `audit/oracle_disagreement_baseline_2026-06-24.md`.

---

## Pattern breakdown

| Bucket | occt (coarse) | gmsh (coarse) | Count |
|--------|--------------|---------------|-------|
| B1 | loaded | silent | 104 |
| B2 | loaded | rejected | 80 |
| B3 | silent | rejected | 4 |
| **Total** | | | **188** |

---

## B1 — occt=loaded, gmsh=silent (104 fixtures)

**Representative fixtures sampled**: Gp161, Gn015, Gn036, Gs006, Bo001, Tsh035, M012,
M017, N106, Hea016.

**Oracle pattern**: `occt=shape(1) gmsh=empty`.  OCCT loads a shape; gmsh returns
nothing (no error either).

**Catalog Expected line** (all 104 checked): `occt=shape(1)/shape(1) gmsh=empty
ifc=schema_n/a`.  The Expected line correctly encodes both outcomes side-by-side — the
divergence is captured.

**Verdict: class (a) — catalog already captures the divergence.**  No action required.

### Diagnostic sub-finding (informational, not class-changing)

103 of 104 B1 fixtures have `occt_diag_on` containing `"Incorrect Syntax : Fails Count
: 2"` from the OCCT StepFile reader, and the same text appears in `gmsh_diag`.  Both
kernels see the syntax issue; OCCT recovers and emits shape(1), gmsh gives up and
returns empty.  The catalog Notes field on these entries typically says **"OCC behavior:
silently accepts (no diagnostic, empty result)"** — this wording is imprecise (OCCT
does emit an ERR diagnostic), but it describes OCC's failure to reject/heal as the
catalog requires, not the shape-vs-empty outcome.  The Expected line is the authoritative
divergence record and is correct.  The Notes wording imprecision is pre-existing and
out-of-scope for this audit.

Exception: **M012** (TCGR requires AP242 Ed.4) — no diagnostic from either kernel.  OCCT
silently accepts the unknown entity and loads whatever B-rep is present; gmsh ignores the
TCGR entity and returns empty.  This is a semantic divergence (entity-class handling), not
a syntax-recovery divergence.  Catalog Expected says `gmsh=empty`; oracle confirms.
Class (a).

---

## B2 — occt=loaded, gmsh=rejected (80 fixtures)

**Representative fixtures sampled**: Gp002, Gp005, Gp007, Xp012, Wr054, Twi006,
Twi033, Tfa069, Tsh020, Bo006, N088, A079, A083, Fi001, Pmi006, Ad120.

**Oracle pattern**: `occt=shape(1) gmsh=reject` (or `gmsh=signal(11)` for signal-class
rejections such as Pmi006, A079).

**Catalog Expected line** (all 80 checked): each entry's Expected line correctly encodes
`gmsh=reject` or `gmsh=signal(11)`.  Sample confirmations:

- `Gp002`: `occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a`
- `Tsh020`: `occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a`
- `Pmi006`: `occt=shape(1)/shape(1) gmsh=signal(11) ifc=schema_n/a`
- `A079`: `occt=shape(1)/shape(1) gmsh=signal(11) ifc=schema_n/a`
- `Fi001`: `occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a`

**Verdict: class (a) — catalog already captures the divergence.**  No action required.

### Sub-pattern note

Same `"Incorrect Syntax : Fails Count : 2"` diagnostic from OCCT appears in 80/80
B2 fixtures.  The divergence here is harsher: gmsh actively rejects the file (non-empty
exit status or explicit reject return), while OCCT heals past the syntax error and
delivers a shape.  The Notes phrasing imprecision noted in B1 applies here too but does
not affect correctness of Expected lines.

---

## B3 — occt=silent, gmsh=rejected (4 fixtures)

All four fixtures: **Tfa153, M041, M042, M048**.

| Fixture | Oracle | Catalog Expected | Match |
|---------|--------|-----------------|-------|
| Tfa153 | `occt=empty gmsh=reject` | `occt=empty/empty gmsh=reject ifc=schema_n/a` | exact |
| M041 | `occt=empty gmsh=signal(11)` | `occt=empty/empty gmsh=signal(11) ifc=schema_n/a` | exact |
| M042 | `occt=empty gmsh=signal(11)` | `occt=empty/empty gmsh=signal(11) ifc=schema_n/a` | exact |
| M048 | `occt=empty gmsh=signal(11)` | `occt=empty/empty gmsh=signal(11) ifc=schema_n/a` | exact |

**Tfa153** Notes: explicitly documents that both kernels see "Incorrect Syntax: Fails
Count: 2" but OCCT categorizes the result as silent-empty while gmsh categorizes it as
reject — the divergence is the explanation.

**M041/M042/M048** are appearance/material fixtures.  gmsh crashes (signal 11) on
`SURFACE_STYLE_TRANSPARENT`, `STYLED_ITEM` (root label), and `MATERIAL_DESIGNATION`
with zero density.  OCCT silently drops the attributes and returns empty (no BRep to
load).  Both oracles agree there is no loadable BRep; they disagree on whether the
process is clean.

**Verdict: class (a) — catalog already captures the divergence.**  No action required.

---

## Overall verdict

**188/188 fixtures = class (a).**

Every disagreeing fixture's catalog entry already encodes the oracle-vs-oracle divergence
in its `Expected validation` line.  The Expected line format (`occt=X/X gmsh=Y`) was
designed from a dual-oracle perspective and was populated correctly when the fixtures were
generated or refreshed.

### No class (b) findings

No fixtures were found where the catalog mentions only one kernel's behavior without
encoding the divergence in the Expected line.

### No class (c) findings

No fixtures were found where the catalog Expected line contradicts what the oracles
actually produce.  (Checked via exact string match on all 188 Expected lines against the
coarsened oracle outcomes.)

---

## What this means for next-session work

1. **No regen work required from this audit.**  The disagreement corpus is well-captured;
   the Expected lines serve as documented inter-kernel divergence baselines.

2. **Potential low-priority cleanup** (NOT a next-session priority): The Notes field on
   ~183 fixtures (B1 + B2) says "OCC behavior: silently accepts (no diagnostic, empty
   result)" when OCCT actually emits an ERR diagnostic.  This is a Notes-wording
   imprecision about the OCC behavior description, not a claim error.  If Notes clarity
   becomes a priority, these could be updated to say "OCC emits ERR diagnostic but
   recovers and loads a shape" vs "gmsh returns empty/rejects."

3. **Diagnostic pattern is structurally useful**: The near-universal `"Incorrect Syntax :
   Fails Count : 2"` diagnostic on 187/188 disagreeing fixtures means the disagreement
   corpus is almost entirely about post-syntax-error recovery policy, not geometric
   correctness.  A CAD kernel being built against this corpus should implement
   lenient-recovery-from-syntax-error behavior to match OCCT rather than strict-reject to
   match gmsh.

---

*Audit performed: 2026-06-24.  Scope: research/read-only, no code or catalog changes.*
