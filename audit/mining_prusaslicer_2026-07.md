# Mining PrusaSlicer for NEW file-level STEP defect classes (2026-07)

**Source.** `prusa3d/PrusaSlicer` (AGPL-3.0) — a 3D-printing slicer with a native STEP
import path built on **OCCT** (`OCCTWrapper.so`) that tessellates the loaded B-rep to a
mesh and runs an open-edge / manifold check. Because it wraps OCCT, most of its STEP bugs
**correlate with the already-mined OCCT classes**; the mining job here is to isolate the
handful that are genuinely NEW file-level classes (or a distinct sub-case) and honestly
flag the rest as corroborating.

**Method.** `gh issue list --repo prusa3d/PrusaSlicer --state all --search "…" --limit 100`
across STEP-import, crash, hang, empty, units, and color queries; read the strongest tickets
(starting with the survey-flagged #11305 and #8998); for each candidate decided (a) is it
FILE-LEVEL (a static `.stp` reproduces it, not a runtime/UI/version-only bug?) and (b) is it
NOVEL vs `STEP_PROBLEM_CATALOG.md` (grepped ORIENTED_EDGE cyclic/recursion, sphere/cone pole,
zero-bbox, open-edge/non-watertight). **License:** PrusaSlicer is AGPL-3.0 and OCCT is
LGPL-2.1-w-exception, but we cite the **pattern only**. Every attached reproducer is a
user-uploaded proprietary CAD export (FreeCAD, Fusion 360, SolidWorks, Solid Edge, Onshape) —
**DESCRIBE-ONLY, never ingest bytes**; we synthesize an equivalent minimal fixture from the
described mechanism.

---

## Candidate table

| # | Title / defect class | Source (pattern only) | Reproducer recipe (minimal Part-21) | Expected behavior | Target section | Novelty | License |
|---|---|---|---|---|---|---|---|
| 1 | **Cyclic / self-referential `ORIENTED_EDGE.edge_element` → unbounded `EdgeStart`/`EdgeEnd` recursion → stack overflow (DoS)** | PrusaSlicer #11305 (ASAN `stack-overflow`, frames alternate `StepShape_OrientedEdge::EdgeEnd()` ⇄ `EdgeStart()` in `OCCTWrapper.so`) | `#1=ORIENTED_EDGE('',*,*,#1,.F.);` (self-ref, reversed orientation) — or a 2-cycle `#1=ORIENTED_EDGE('',*,*,#2,.T.); #2=ORIENTED_EDGE('',*,*,#1,.F.);` — placed in an `EDGE_LOOP`/`FACE_OUTER_BOUND` so the transfer pass dereferences it. The derived-attribute accessor `EdgeStart()` delegates to `edge_element->EdgeStart()` (swapping to `EdgeEnd()` when `orientation=.F.`); a cycle never reaches an `EDGE_CURVE`, so it recurses forever. | Reject with a bound: chase `ORIENTED_EDGE` wrapper chains under a depth/visited-set guard; emit `E_EDGE_CYCLE` / drop the edge; **must not** stack-overflow. Fuzz-grade DoS — a receiver must give up gracefully. | **Twi** (§12.3b wire/loop), sub-class *cyclic-oriented-edge / fuzz*; cross-list **Ad** (§12.11) | **NEW** — Twi004 is a *finite* wrapper chain that terminates at an `EDGE_CURVE` and is healed by traversal (silent-empty, no crash). This is the *unbounded-cycle* variant that overflows the stack in the `EdgeStart`/`EdgeEnd` derived accessors. Distinct entity path from Gs054 (COMPOSITE_CURVE_SEGMENT self-cycle), Pf010/A012 (external-ref / generic entity-graph cycle). No existing entry covers an `ORIENTED_EDGE.edge_element` cycle. | pattern-only (attached `stack-overflow.step` = DESCRIBE-ONLY) |
| 2 | **Receiver drops a validly-loaded STEP as "Object size … appears to be zero"** (cross-oracle: opens in FreeCAD / Autodesk viewer / OrcaSlicer, zero-extent in PrusaSlicer's mesh path) | #8685 (FreeCAD 0.20 export), #10326 (FreeCAD 0.19, AP214 & AP242 both), #11599 (Solid Edge export; "works in OrcaSlicer") | A STEP whose transferred shape yields an empty / zero-extent tessellation in one OCCT-mesh consumer but not others — e.g. a surface/sheet body with no `MANIFOLD_SOLID_BREP` (only `OPEN_SHELL`/`SHELL_BASED_SURFACE_MODEL`), or a body that OCCT sews to nothing at the receiver's default tolerance. Bbox of the resulting mesh = 0 → object removed. | Do not silently discard; if the transfer produced a valid shape, mesh it (surface bodies included) or surface a specific diagnostic rather than a generic "size is zero". Cross-oracle divergence should be reproducible/attributable. | **In** (§12.1c interface/transfer diagnostics) | **SUB-CASE / borderline** — the *receiver-divergence* framing ("valid in 3 tools, zero-size-dropped in the 4th") is under-covered, but the precise Part-21 construct can't be pinned from the tickets (no bytes); mechanism overlaps existing silent-empty / transfer-fail entries. Honestly closer to CORROBORATES unless a concrete surface-body-only fixture is built. | pattern-only (3 proprietary exports = DESCRIBE-ONLY) |
| 3 | **Header parse abort `unexpected QUID, expecting STEP` at line 2** | #12109 (`** ERR StepFile : Undefined Parsing: Line 2: Incorrect syntax: unexpected QUID, expecting STEP **`; surfaced to user as `basic_string` throw) | A header whose 2nd token stream puts a quoted string (`QUID` = quoted-id lexer token) where OCCT's `step.yacc` grammar expects the `STEP`/keyword production — e.g. mangled/garbage or mis-encoded bytes before/inside `HEADER;`, or a stray leading quoted token. | Reject with a precise header-syntax diagnostic; do not leak the raw `basic_string` C++ exception to the UI. | **Lh** (§12.1b header) | **CORROBORATES-existing** header-framing/parse entries — too vague to pin a distinct novel construct without the file; noted for completeness. | pattern-only |

---

## Corroborating (NOT novel — confirm existing classes)

- **#8998 — "STEP model has 127 open edges; STL of the same part has none"** (the survey's flagship PrusaSlicer example). Sub-tolerance sewing gaps survive as free/naked edges in the tessellated STEP while the STL is already welded. → **CORROBORATES** the free-naked-edge / non-watertight vein (Twi037, Tsh019/Tsh040, M004) plus the STEP-vs-mesh cross-oracle framing already present. Strong *illustration*, not a new class.
- **#12391 — revolved sphere: the cap where the profile circle meets the rotation axis perpendicularly is dropped** (SolidWorks export; also wrong in 3ds Max). This is the singular **pole of a `SPHERICAL_SURFACE`/`SURFACE_OF_REVOLUTION`**. → **CORROBORATES Gp005** (single-pole apex on sphere/cone; wire touches the singular point without an explicit degenerate edge).
- **#13506 — surface "damaged", a hole appears after import** (Fusion 360; "some triangles got removed" during tessellation). → **CORROBORATES** the tessellation/faceting-dropout mesh defects.
- **#13892 — curved surface imported as a single flat faceted triangle** instead of a smooth face. → **CORROBORATES** the curved-surface-faceting / faceting-resolution entries.
- **#14395 — same file imports wrong only when PrusaSlicer is built against OCCT 7.8.x** (correct in FreeCAD-on-OCCT-7.8). Kernel-**version**-sensitive, not a static-file property. → **SKIP** (runtime/version divergence; the survey already notes it).

## Dropped (runtime / UI / not file-level)
- #11503 (freeze/crash on open, no ASAN detail — perf/hang), #9712 (crash on *re-orientation before slicing*, not import), #14144 (import "too slow" — perf), #12416 (vague "error rendering", no mechanism), #13138 (particular file "doesn't slice" — slicing, not import). None encode a distinct static-file class.

---

## Honest yield note

PrusaSlicer behaves exactly as the source survey predicted: a **high-volume, attachment-rich,
but heavily OCCT-correlated** stream. Of the tickets reviewed, **one is genuinely NEW**
(candidate 1 — the cyclic-`ORIENTED_EDGE` stack overflow, a clean fuzz-grade file-level DoS
distinct from the existing finite-chain Twi004 and from the composite-curve/external cycles),
**one is a borderline sub-case** (candidate 2 — the cross-oracle "object size is zero"
receiver-divergence, only worth an entry if a concrete surface-body fixture is synthesized),
and everything else **corroborates** classes the corpus already covers (open-edges/non-watertight,
sphere-pole singularity, tessellation dropout, curved-face faceting). Candidate 1 is the only
one I'd recommend cataloguing now.
