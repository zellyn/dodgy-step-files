# OCCT problem-coverage remediation — wave plan (2026-07-12)

Turns the ranked queue in `BACKLOG.md` §"OCCT problem-coverage remediation queue (2026-07-12)"
into an executable set of work packets for parallel fixture-synthesis agents. Inputs:
`occt-coverage/OCCT_PROBLEM_COVERAGE.md`, `occt-coverage/{tkshhealing,exchange}/problems.json`
(post-calibration, commit `292e2dfc`), `occt-coverage/{tkshhealing,exchange}/SUMMARY.md`.
Scope: the 25 STEP-exercisable GAP classes + 63 PARTIAL classes named in the BACKLOG queue
(88 classes total). IGES is out of scope throughout (structural carve-out, not re-litigated here).

**Bottom line:** 3 of the 25 GAP classes are carved out as STEP-inexpressible. 2 more GAP classes
are already being fixed by sibling agents (excluded from this plan). That leaves **20 fillable GAP
classes + 3 single-fixture-insurance items + 63 fillable PARTIAL classes = 86 problem classes**,
requiring an estimated **118 new fixtures**, bundled into **16 work packets** run across **8
two-packet waves**. If every packet lands as specified, the honest STEP-exercisable denominator
(171 classes, after the carve-out) goes from **86 COVERED / 63 PARTIAL / 22 GAP (50.3% / 87.1%
COVERED-or-PARTIAL)** to **169 COVERED / 0 PARTIAL / 2 GAP (98.8% / 98.8%)** — the residual 2 GAP
being the two in-flight items this plan deliberately does not touch.

All projections in §4 are **aspirational targets**, not guarantees: this project's own audit
history shows a ~30% COVERED-verdict overturn rate on first-pass claims (see
`VERDICT_AUDIT.md`/`COVERED_FULL_REVERIFY.md`). Treat "GAP/PARTIAL → COVERED" as "verdict eligible
for re-review once the fixture lands," not as self-certifying.

---

## 1. Carve-outs and the honest denominator

### 1a. STEP-INEXPRESSIBLE (3 classes, all `exchange/brepcheck`, all `detect_only`)

These three are excluded from the fillable denominator because their trigger requires an
in-memory OCCT B-Rep data structure that no combination of Part-21 STEP bytes can cause the
reader to construct — not merely "no fixture has tried hard enough," but "the reader's translator
functions have no code path that populates this representation from any STEP input." Bar applied:
if a creative encoding could *plausibly* reach the mechanism, it's classified FILLABLE instead
(see §1b for three GAP items that look similar on the surface but were reclassified FILLABLE
after re-deriving the mechanism).

- **`bc-invalid-point-on-surface`** — requires a `BRep_PointOnSurface` vertex representation (a
  vertex bound to a `(surface, U, V)` tuple with its own companion 3D point, distinct from the
  vertex's primary point). `StepToTopoDS_TranslateVertex::Init` only ever builds a bare
  `BRep_TVertex` from a `Geom_CartesianPoint` — there is no Part-21 entity or reader call site that
  attaches a second point-on-surface representation to a translated vertex. This representation
  type is populated only by OCCT-internal algorithms (e.g. certain fillet/offset constructions)
  operating on an already-built shape, never by `StepToTopoDS`.
- **`bc-invalid-polygon-on-triangulation`** — requires a `Poly_PolygonOnTriangulation` edge
  representation (indices into a `Poly_Triangulation`'s node array, attached to a `TopoDS_Edge`).
  STEP's `TRIANGULATED_FACE`/`COMPLEX_TRIANGULATED_FACE` entities carry only face-level triangle
  index tables; `StepToTopoDS_TranslateFace`'s tessellated-`Init` path assigns the resulting
  `Poly_Triangulation` to the **face**, never to an edge. No Part-21 construct maps to an
  edge-linked polygon-on-triangulation record — it is populated only by `BRepMesh` acting on an
  already-built shape.
- **`bc-multiple-3d-curve`** — requires one `TopoDS_Edge` (one `BRep_TEdge`) carrying two or more
  `BRep_Curve3D` representations. Part-21's `EDGE_CURVE` entity has exactly one `edge_geometry`
  attribute — the schema is 1:1 between an edge entity and its 3D curve, so no STEP file can
  declare two curves for the same edge. The only way OCCT ever attaches a second `Curve3D` to one
  `TopoDS_Edge` is direct `BRep_Builder` API misuse (calling `UpdateEdge` twice with different
  curves) — no `StepToTopoDS` call site does this; each edge-producing path sets the curve exactly
  once.

**Three GAP items that looked similar but were reclassified FILLABLE** (re-derived, not assumed):
`bc-no-curve-on-surface`, `bc-no-surface`, and `bc-self-intersecting-wire` were all downgraded
COVERED→GAP in the prior audit pass because their *existing* fixtures crash OCCT (signal 11),
contradict their own tier-3 assertions, or carry an explicit "does not fire" annotation — not
because the mechanism is structurally unreachable. In all three cases `StepToTopoDS`/`XSAlgo`
genuinely *can* produce the live TopoDS state BRepCheck needs to flag (an edge kept 3D-only with a
dropped pcurve; a tessellated-fallback face with no B-Rep surface at all, see
`stp-tess-dangling-brep-link`; a geometrically self-crossing wire, which is plain geometry with no
special encoding requirement) — the corpus just hasn't produced a fixture that reaches that state
without also tripping over an unrelated crash or dead-scaffold problem. These are counted as
FILLABLE GAPs below (items G5, G6, G7).

> **Back-flag (Wave-1 adversarial verifier, 2026-07-12):** the `bc-self-intersecting-wire`
> re-derivation above was over-optimistic. It reads as "the corpus just hasn't produced a fixture
> that reaches that state," implying a plain reader-observable GAP. In fact even a clean,
> confound-free fixture (Twi286) still gets silently healed by `STEPControl_Reader`'s mandatory
> default `ShapeFix_Wire::FixSelfIntersection` pass before any of this corpus's oracle
> configurations (`occt_heal_on/off`, `gmsh_autofix_on/off`) can observe the
> `BRepCheck_SelfIntersectingWire` status — none of them bypass the reader. The mechanism is real
> and was independently confirmed (direct `BRepBuilderAPI_MakePolygon`/`MakeFace` +
> `BRepCheck_Analyzer` on the raw unhealed shape), but only via a runtime scaffold, exactly the
> `tkshh-splitting-vertex-face`/Tfa249 precedent — not a plain reader-observable status. Annotated
> as runtime-scaffold-fillable; landed as such in `exchange/problems.json` (Twi286, COVERED). The
> other two reclassified-FILLABLE items in this section (`bc-no-curve-on-surface`, `bc-no-surface`)
> were not part of this wave's scope and should get the same scrutiny before being counted as
> straightforwardly closed.

### 1b. In-flight — excluded from this plan (2 classes)

Per BACKLOG.md, do not fixture these here; re-check their verdict once the sibling work lands:

- `tkshh-splitting-vertex-face` (TKShHealing) — sibling agent authoring a splitting-vertex fixture now.
- `seq-xsalgo-unit-mismatch` (exchange/heal-sequence) — sibling agent authoring a unit-mismatch fixture now.

### 1c. The honest denominator

| | classes |
|---|---:|
| STEP-exercisable denominator (audit convention, excl. IGES only) | 174 |
| − STEP-INEXPRESSIBLE carve-out (§1a) | −3 |
| **Honest fillable denominator** | **171** |
| COVERED (baseline) | 86 |
| PARTIAL (baseline, all 63 in scope here) | 63 |
| GAP (baseline, 25 − 3 carve-out) | 22 |
| … of which in-flight, excluded from this plan (§1b) | 2 |
| **GAP classes this plan targets** | **20** |
| + 3 single-fixture-insurance items (COVERED but resting on exactly one fixture) | 3 |
| **Total problem classes this plan fixtures** | **20 + 3 + 63 = 86** |
| **Estimated new fixtures** | **~118** |

---

## 2. Packet catalog

16 packets, grouped so every packet's fixtures land in a small, consistent set of
`step-examples/12-*` section directories (the packing unit for the disjointness constraint).
Naming: `Gn` = GAP-derived item, `Ins` = insurance item, `Pn` = PARTIAL-derived item, numbered
per packet. Directory prefix key: Bo/Ps/Sw/Tsh→`12-3a-shells`, Twi→`12-3b-wires`,
Hea/Tfa→`12-3c-faces`, N/Tb→`12-4-tolerance`, U→`12-5-units`, A/P→`12-6-assembly`,
Gp→`12-2a-pcurves`, Gn→`12-2b-nurbs`, Gb/Gs→`12-2c-surfaces`, Lh→`12-1b-header`,
Ad→`12-11-adversarial`, M/Os/Fi→`12-8-mixed`.

Value ordering: **GAP classes first** (packets A1/B1/C1/D1/JL/GHIK — whole problem classes, run in
Waves 1–3), **then the 3 insurance items** (bundled into A1/B1, since they land in the same
directories as GAP work already scheduled early), **then PARTIALs densest-first** (Waves 4–8;
packets with the most missing-subvariant fixtures were preferentially placed earlier within their
family where the wave-pairing constraint allowed).

Nearest-verified-fixture mirrors favor the fixtures verified today per the task brief (N152,
N146–N153, Gp022, Tsh013, Tfa020, Bo025, Twi048) wherever their structure fits; otherwise the
nearest fixture cited in the class's own `problems.json` record.

### Wave 1 — Packet A1 (GAP, shells) + Packet B1 (GAP, wires)

**A1 — GAP: shells/solids** · dirs: `12-3a-shells` · 8 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `tkshh-sliver-solid` (GAP) | Compound of 2 solids: one normal box solid + one sliver solid at 0.5% of its volume (below `ShapeFix_FixSmallSolid` volume threshold); second fixture: same but width-factor (vol/half-area) below threshold, adjacent to a neighbor solid to exercise the Merge disposition | 2 | Tfa015 (structure to avoid: must be a genuine `TopoDS_SOLID`, not a bare face) |
| `tkshh-solid-unstructured-multishell` (GAP) | Two fixtures: (a) 2 shells, no BREP_WITH_VOIDS wrapper, one geometrically nested inside the other — forces `ShapeFix_Solid::CreateSolids` point-containment classification into one solid-with-void; (b) 2 shells, genuinely disjoint bounding boxes — forces classification into a compound of 2 separate solids | 2 | Bo003 (avoid its BREP_WITH_VOIDS wrapper — that's a different, already-covered path) |
| `seq-drop-small-solids` (GAP) | Mirror the two `tkshh-sliver-solid` fixtures above but reached via the STEP.exec.op `dropsmallsolids` operator context (opt-in operator, same geometry works) | 2 | (shares geometry with the tkshh-sliver-solid pair above) |
| `bc-enclosed-region` (insurance) | Second independent fixture: a face with a wholly-enclosed inner wire (not touching the outer boundary), distinct geometry from Tsh015 | 1 | Tsh015 (sole existing fixture — do not touch it, add a new one) |
| `stp-degenerate-edge-multiface` (GAP) | Cone apex degenerate edge referenced from 2 different ADVANCED_FACEs' bounds (not within one wire) — forces `StepToTopoDS_TranslateEdge::Init`'s cached-degenerated-edge retranslate-per-face path | 1 | Tsh035 (single-face — extend to multi-face) |

**B1 — GAP: wires** · dirs: `12-3b-wires` · 8 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `tkshh-wire-duplicate-coincident-vertex-instances` (GAP) | (a) Two consecutive wire edges sharing a location but using distinct VERTEX_POINT entities (not reused) on a live face; (b) two arbitrary, non-adjacent edges registered as touching via coincident-but-distinct vertices in a broader connectivity graph | 2 | Twi009/Twi050 (SplitCommonVertex — opposite direction, use as negative-space guide) |
| `bc-self-intersecting-wire` (GAP, reclassified from §1a) | Clean figure-eight/bow-tie wire on a real ADVANCED_FACE, minimal — no extra defects layered on top that could crash OCCT or trigger a "checker does not fire" annotation | 1 | Twi049 (fix: strip the confounding factors that made Twi049/Twi076 non-firing) |
| `seq-split-closed-edges` (insurance) | Second independent fixture: full-period closed edge (start==end vertex) on a different surface kind than Twi019 (e.g. torus belt, not circle) | 1 | Twi019 (sole existing fixture — add a new one, don't touch it) |
| `seq-split-common-vertex` (insurance) | Second independent fixture: two adjacent edges sharing a common vertex requiring split, distinct geometry from Twi009 | 1 | Twi009 (sole existing fixture — add a new one, don't touch it) |
| `tkshh-edge-missing-3d-curve` (PARTIAL, missing 1 of 2) | Edge with neither a 3D curve nor a usable pcurve (zero-length pcurve range) inside an otherwise-healthy wire — exercises the removal path (`ShapeFix_Wire.cxx:744-759`), not the reconstruct-from-pcurve path Twi047 already covers | 1 | Twi047 |
| `stp-null-arc-edge-fallback` (PARTIAL, missing 1 of 2) | Non-closed 3D curve, two distinct vertices, malformed/near-zero-length arc trim that fails `BRepLib_MakeEdge`'s validity check → forces the "substitute a straight Geom_Line between the vertex points" fallback | 1 | Twi018 (covers the *other* subvariant — identical vertices) |
| `stp-loop-vertex-merge` (PARTIAL, missing 1 of 2) | Two ADJACENT edges in one wire whose shared corner vertex is encoded as two distinct-but-coincident-within-tolerance VERTEX_POINT entities (not the single-edge start/end case Twi017 covers) | 1 | Twi017 |

### Wave 2 — Packet C1 (GAP, faces) + Packet D1 (GAP, pcurves)

**C1 — GAP: faces** · dirs: `12-3c-faces` · 8 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `tkshh-indirect-elementary-surface-axes` (GAP) | (a) A planar/cylindrical ADVANCED_FACE whose AXIS2_PLACEMENT_3D has a negative-determinant (mirrored) location, right-handed frame otherwise; (b) a CONICAL_SURFACE with negative semi-angle, combined with an indirect frame to also satisfy the "both defects" subvariant | 2 | none in corpus — new territory; base geometry off any single-face `Tfa0*` fixture |
| `sew-merged-edge-continuity-encoding` (GAP) | Two faces sharing exactly one merged edge with genuinely tangent (G1, not sharp) geometry, sewn via the default face-merge path, so `BRepLib::EncodeRegularity` is invoked and its result is assertable | 1 | Bo025 (G1 edge mis-tagged — invert the framing: this fixture's edge should end up correctly classified, testing the *encode* path itself, not the mis-tag detection) |
| `stp-missing-geometry-definition` (GAP) | An EDGE_CURVE with `edge_geometry=$` (null), wired into a live, reachable wire/face (not inside a GEOMETRIC_CURVE_SET, not a dead trailing entity) — must be referenced by a real CLOSED_SHELL/OPEN_SHELL so `StepToTopoDS_TranslateEdge::Init`'s clean-fail path actually executes on the default import path | 1 | Xp008 (face variant — reuse its face-hosted pattern, just for an EDGE_CURVE instead) |
| `tkshh-face-intersecting-wires` (PARTIAL, missing 2 of 4) | (a) Large (>50%) collinear segment overlap between the outer and an inner wire of one face, forcing the 3-edge reconstruction path; (b) clean endpoint-endpoint contact between two wires (not a transverse crossing) forcing `UnionVertexes` | 2 | Tfa039 |
| `tkshh-face-natural-bound-missing` (PARTIAL, missing 1 of 3) | Sphere face whose only hole wire touches the pole via a degenerated edge — the hole must be merged into the natural (whole-surface) boundary rather than kept as a separate FACE_BOUND | 1 | Tfa002 |
| `bc-intersecting-wires` (PARTIAL, firing unconfirmed on sole survivor) | Second independent outer/inner-wire UV-crossing fixture, distinct geometry from Tfa039, built to avoid whatever kept firing "unconfirmed" on the existing one | 1 | Tfa039 |

**D1 — GAP: pcurves** · dirs: `12-2a-pcurves` · 8 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `bc-no-curve-on-surface` (GAP, reclassified from §1a) | Single planar or cylindrical face, one boundary edge with a real 3D curve but no pcurve entity and no other edges/faces malformed enough to crash OCCT before BRepCheck runs (unlike Gp001/Gp042's signal 11) | 1 | Gp001 (fix: isolate the defect from whatever triggers the crash) |
| `stp-compcurve-reorder` (GAP) | A COMPOSITE_CURVE whose segment list is out of connected geometric order (segment 2 given before segment 1, endpoints still connect once reordered) — must exercise `StepToTopoDS_TranslateCompositeCurve::Init`'s `FixReorder`, not an EDGE_LOOP-level scramble | 1 | Twi007 (covers the *wrong* path — EDGE_LOOP scrambling; rebuild via COMPOSITE_CURVE) |
| `tkshh-edge-crossing-surface-singularity` (PARTIAL, missing 2 of 2) | (a) An edge whose interior 3D curve passes directly over a cone apex/sphere pole — must trigger a SPLIT into two sub-edges, not just an apex-adjacent pcurve; (b) a contour wrapping both a degenerated pole and the seam, needing pcurve rebuild with `AdjustOverDegenMode=false` | 2 | Xp013, Gp048 |
| `tkshh-edge-curve-inconsistent-with-vertex-removed` (PARTIAL, missing 1 of 5) | An edge whose 3D curve endpoint disagrees with its vertex position beyond tolerance while its pcurve is trustworthy — the mirror-image of the well-covered pcurve-side case, exercising `FixRemoveCurve3d` | 1 | Gp064 (covers the pcurve-side removal — build the 3D-curve-side analog) |
| `tkshh-near-zero-knot-span-thin-patch-filter` (PARTIAL, missing 1 of 2) | A 2D pcurve (not surface) whose knot vector has a near-duplicate/clustered knot pair producing a near-zero-length Bezier arc after `ShapeUpgrade_ConvertCurve2dToBezier` decomposition | 1 | Gn042 (surface-side sibling — mirror its structure onto a 2D curve) |
| `tkshh-nonperiodic-bspline-seamlike-edge` (PARTIAL, missing 2 of 3) | (a) Same CATIA-style near-closed non-periodic B-spline seam-like-edge pattern as Gp013 but in the V direction instead of U; (b) same defect on a non-B-spline base surface, forcing `GeomConvert_ApproxSurface` before periodicity can be set | 2 | Gp013 |

### Wave 3 — Packet JL (GAP, mixed+adversarial) + Packet GHIK (GAP, units/tolerance/assembly/header)

**JL — GAP: tessellation/geomset + robustness** · dirs: `12-8-mixed`, `12-11-adversarial` · 8 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `bc-no-surface` (GAP, reclassified from §1a) + `stp-tess-dangling-brep-link` face subvariant (GAP) — **one fixture covers both** | A TESSELLATED_FACE whose `geometric_link` points at an unresolvable/unbound BRep face entity — the reader falls back to a fresh empty face with `theHasGeom` cleared, which genuinely has no B-Rep surface, so `BRepCheck_Face::Blind`'s `NoSurface` check has a live target to fire on | 1 | M022 (has `geometric_link=$`; needs an actual unresolvable ref instead of absent) |
| `stp-tess-dangling-brep-link` shell subvariant (GAP) | TESSELLATED_SHELL with an unresolvable topological link — falls back to a fresh shell | 1 | Pmi164 |
| `stp-tess-dangling-brep-link` solid subvariant (GAP) | TESSELLATED_SOLID with an unresolvable geometric link — falls back to a fresh shell+solid | 1 | Tsh065 |
| `stp-geomset-gri-fallback` (GAP) | GEOMETRIC_SET mixing a supported item (LINE) with a generic GeometricRepresentationItem (AXIS2_PLACEMENT_3D) — same pattern as M051 but built to avoid the signal-11 crash M051 hits | 1 | M051 (fix the crash trigger, keep the mixed-item pattern) |
| `stp-polyloop-dup-point` (GAP) | FACETED_BREP POLY_LOOP listing the same CARTESIAN_POINT twice in immediate succession — exercises `StepToTopoDS_TranslatePolyLoop::Init`'s degenerate-segment skip | 1 | M055 (only existing POLY_LOOP fixture — has distinct points; duplicate one) |
| `stp-tess-degenerate-triangles` (GAP) | TRIANGULATED_FACE using **strip or fan** encoding (not plain triangle list, which M005's fixture used and which the skip-guard never reaches) with a repeated-vertex-index triple | 1 | M005 (wrong encoding mode — rebuild as strip/fan) |
| `stp-tess-malformed-normals` (GAP) | Tessellated normals table with a row that has 2 or 4 components instead of 3 — triggers the row-arity guard's silent-ignore | 1 | Bo027 (well-formed rows — malform one row's arity instead) |
| `bc-check-fail` (PARTIAL, missing live-shape confirmation) | Extreme-but-non-crashing degenerate geometry on a **built shape** (not just at read/heal time) that makes a BRepCheck-equivalent sub-check throw — e.g. a near-zero-radius circle used as a face boundary that survives translation but chokes a projection call during validity checking | 1 | Ad132 (throw is at heal time — move the throw to check time) |

**GHIK — GAP: units/tolerance/assembly/header** · dirs: `12-5-units`, `12-4-tolerance`, `12-6-assembly`, `12-1b-header` · 10 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `stp-missing-unit-context-default` (GAP) | (a) A standalone FaceSurface entity requested for isolated transfer with no reachable SHAPE_REPRESENTATION (no unit context at all) — must be a live GRI, not GEOMETRIC_CURVE_SET-hosted like M063; (b) a REPRESENTATION_CONTEXT of the wrong kind (missing unit mixins) directly governing a live shell | 2 | M063 (fix: escape the GEOMETRIC_CURVE_SET type-skip that made it type-skipped, not translated) |
| `stp-srr-nauo-reversed` (GAP) | NEXT_ASSEMBLY_USAGE_OCCURRENCE + SHAPE_REPRESENTATION_RELATIONSHIP wired through a real CONTEXT_DEPENDENT_SHAPE_REPRESENTATION (not stuffed in a GEOMETRIC_CURVE_SET like M062), with the SRR relating the two representations in the direction opposite the NAUO | 1 | M062 (fix: wire through CDSR properly, keep the reversal) |
| `bc-invalid-tolerance-value` (PARTIAL) | A live translated face whose tolerance ends up smaller than one of its child edges'/vertices' tolerances after reader tolerance-inflation on a pcurve-disagreement fixture — not a GEOMETRIC_CURVE_SET single free edge like N001 | 1 | N001 (fix: needs a face context) |
| `seq-set-tolerance` (PARTIAL, missing 1 of 3) | Live shell whose vertex/edge tolerance is out of the acceptable `[val/ratio, val*ratio]` band relative to a target — reached via `settol` operator on a real face, not N001's dead GEOMETRIC_CURVE_SET | 1 | Bo025, Twi048 (structure/framing) |
| `stp-tolerance-ceiling-clamp` (PARTIAL) | A shell whose per-entity repairs (vertex-tolerance bumps) accumulate across several edges to exceed a configurable ceiling, demonstrating the global `ReadMaxPrecisionMode` post-pass clamp — not just one bloated UNCERTAINTY_MEASURE like Tb020 | 1 | Tb020, N152 (tolerance-band structure) |
| `stp-vertex-tol-gap` (PARTIAL, missing 1 of 2) | A LINE-type curve displaced from its true position but with the correct direction (FPX/PCB-style export quirk) — both edge endpoints show the same projection error so OCCT rigidly shifts the curve along its own direction, rather than merely enlarging vertex tolerance | 1 | N007 (ordinary-gap case — build the correct-direction-but-displaced variant) |
| `stp-mapped-item-no-transform` (PARTIAL) | A MAPPED_ITEM with a resolvable REPRESENTATION_MAP and a real target shape, but a placement/transform reference of a type OCCT's dispatch doesn't recognize (not Tfa248's malformed empty-string source slot, which risks aborting before the fallback runs) | 1 | Tfa248 (fix: keep the map+shape valid, only the placement should be unrecognized) |
| `stp-srrwt-axis-swap` (PARTIAL, missing 1 of 2) | SRRWT where only ONE of Origin/Target resolves to its expected representation's item list (not fully swapped like A007) — exercises the unrepairable "does not belong" branch | 1 | A007 |
| `stp-ideas-shell-closing` (PARTIAL) | FILE_NAME.preprocessor_version containing "I-DEAS", **plus** an actual open shell with 1+ adjacent purely-non-manifold closing shells for `computeIDEASClosings`/`closeIDEASShell` to merge and prune — not Lh031's header-only probe with no real shell topology | 1 | Lh031 (fix: add real shell topology behind the header trigger) |

### Wave 4 — Packet A2 (PARTIAL, sewing core, shells) + Packet B2 (PARTIAL, tkshh wires)

**A2 — sewing core mechanisms** · dirs: `12-3a-shells` · 8 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `sew-degenerate-free-wire-collapse` (GAP, last one) | A sewn shell's leftover free-boundary wire loop (2+ full-length free edges forming a closed loop after the main merge) whose overall size is geometrically negligible — post-merge, not Sw003's pre-merge zero-area-but-full-length pattern | 1 | Sw003 (rejected structure — needs true sub-tolerance extent, post-merge) |
| `sew-cutting-hanging-vertex-split` (PARTIAL, missing 3 of 3) | Purpose-built T-junction: one free edge's endpoint vertex projects onto the interior of an unrelated free edge, three variants combined into 2 fixtures: (a) snap-to-existing-cut-vertex vs new-cut-vertex threshold + non-manifold-vertex preservation across the cut; (b) seam-edge dual-pcurve propagation across a cut on a periodic surface | 2 | M045 (incidental hit — purpose-build it) |
| `sew-free-edge-gap-merge` (PARTIAL, missing 2 of 2) | (a) Within-tolerance gap but candidate edge shorter than the min-length floor (rejected as spurious sliver); (b) within-tolerance gap but sampled-point coverage below ~50% (rejected as insufficient overlap evidence) | 2 | Tsh203, Tfa020 |
| `sew-candidate-tiebreak-reciprocity` (PARTIAL) | Purpose-built (not incidental): 3 coplanar free edges where 2 are genuinely equidistant candidates for a reference edge, requiring the `arrMinDist` tie-break, plus a reciprocity-asymmetric configuration (A's best match is B, B's best match is C) | 1 | M045, Tsh013 |
| `sew-longest-edge-reference-selection` (PARTIAL) | Two face-hosted (not GEOMETRIC_CURVE_SET) candidate edges of unequal length within merge tolerance — the longer must become the parametrization reference | 1 | N148 (structure — rebuild face-hosted) |

**B2 — tkshh wire mechanics** · dirs: `12-3b-wires` · 8 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `tkshh-closed-edge-full-period-unsplit` (PARTIAL, missing 2 of 3, pick 2) | (a) A closed/periodic edge whose projected endpoint parameter order is swapped after projection (w1>w2), requiring epsilon-safe range reconstruction; (b) a closed-curve split nested inside an Offset/Trimmed-curve wrapper, falling back to the nearest true-basis-curve knot | 2 | Twi019 |
| `tkshh-same-curve-fragmented-edges` (PARTIAL, missing 2 of 5) | (a) An open chain of 2+ arcs of the same circle (not yet closing to a full circle) fused into one arc; (b) a chain of B-spline/Bezier edges concatenated under `ConcatBSplines` mode | 2 | Twi089 (line case — mirror structure for arcs/B-splines) |
| `tkshh-wire-missing-or-bad-degenerated-edge` (PARTIAL, missing 2 of 10) | (a) Degenerated-torus (major radius < minor radius) missing its apex edge at `aPhi = acos(-R/r)`; (b) a B-spline surface pinched to a point at a U- or V-boundary, missing its degenerated edge at the pinch (bug 24055 path) | 2 | Twi021 |
| `tkshh-wire-nonadjacent-edges-intersect` (PARTIAL, missing 1 of 8) | Two non-adjacent edges of one wire with a large (>50%) collinear overlap, forcing the 3-edge reconstruction path (not the small-overlap 2-edge split Twi063 covers) | 1 | Twi063 |
| `sew-malformed-subshape-tolerance` (PARTIAL, needs live confirmation) | An edge with a null vertex reference wired into a real face boundary context (not Twi253's dead `shape_null==True` scaffold) so `FindFreeBoundaries`'s `vFirst/vLast.IsNull()` guard actually executes | 1 | Twi253 (fix: make it reachable) |

### Wave 5 — Packet C2 (PARTIAL, faces) + Packet D2 (PARTIAL, pcurves)

**C2 — face mechanics (small)** · dirs: `12-3c-faces` · 3 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `tkshh-face-wire-of-two-coincident-edges` (PARTIAL) | A multi-wire face (2+ wires) where one wire is exactly the 2-edge slit reusing the same EDGE_CURVE twice — same defect as Tfa074 but with a second real wire on the same face so `FixWiresTwoCoincEdges`'s `nbWires>=2` gate is actually satisfied | 1 | Tfa074 (fix: add the missing second wire) |
| `sew-edge-endpoint-tolerance-reconciliation` (PARTIAL, missing 1 of 2) | Two coincident but topologically unshared closed edges (start==end vertex on each, e.g. two independent full-circle boundaries at the same location) whose merge must use the 3-point-averaging `ComputeToleranceVertex` overload | 1 | Tfa020 |
| `sew-per-edge-fault-isolation` (PARTIAL) | A self-inconsistent 3D/2D curve pairing on one edge (3D LINE +X vs pcurve +Y, like Twi247) wired into a real face-boundary sewing context (not a floating GEOMETRIC_CURVE_SET loop) so `SameParameterEdge`'s per-edge `catch(Standard_Failure)` actually fires mid-sewing | 1 | Twi247 (fix: face-host it) |

**D2 — pcurve mechanics** · dirs: `12-2a-pcurves` · 8 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `bc-invalid-same-range-flag` (PARTIAL) | An edge whose 3D-curve range and pcurve range genuinely differ, wired into a real ADVANCED_FACE (not Twi082's GEOMETRIC_CURVE_SET) so translation binds the pcurve to a face and the SameRange flag lie is live | 1 | Twi082 (fix: face-host it) |
| `seq-split-continuity` (PARTIAL, missing 1 of 3) | A curve with a genuine C0 interior knot (multiplicity = degree+1, non-collinear poles either side) referenced by a live EDGE_CURVE/PCURVE reachable from a translated shape (not Gp033's `shape_null` or Gn172's orphan pattern) | 1 | Gp033 (fix: make it reachable) |
| `seq-xsalgo-pcurve-consistency` (PARTIAL, missing 1 of 3) | A pcurve winding MULTIPLE full periods of a closed surface (degree-vs-radian confusion producing dozens of wraps), not just a single-period shift | 1 | Gp022 |
| `sew-pcurve-domain-reconciliation` (PARTIAL) | Two pcurve-bearing edges actually merged by sewing (not single-edge `ShapeFix_Edge` probes) where one contributor is reversed-orientation, exercising `Reverse()`+`ReversedParameter` before the `SameRange` rescale | 1 | Gp050 |
| `sew-pcurve-parameter-desync-repair` (PARTIAL, missing 3 of 4, pick 2) | (a) A pcurve needing the relaxed second smoothing attempt after the first C0→C1 upgrade doesn't fully resolve, with a deliberate regression so the revert-on-regression path fires; (b) ill-conditioned (highly non-uniform) knot spacing forcing arc-length reparametrization | 2 | Gp040 |
| `stp-compcurve-disconnected` (PARTIAL, single-fixture-thin) | Second independent COMPOSITE_CURVE fixture with a genuine post-reorder connectivity gap, distinct geometry from Gp034 | 1 | Gp034 |
| `stp-missing-pcurve-projection` (PARTIAL, missing 1 of 2) | An EDGE_CURVE whose `associated_geometry` lists a pcurve entity that itself fails to translate (a malformed PCURVE, not a null `$` slot like Gp012) — exercises the "listed pcurve fails to translate" mode | 1 | Gp035 (no-pcurve mode — build the malformed-pcurve-in-list mode) |

### Wave 6 — Packet A3 (PARTIAL, sewing nonmanifold/seam, shells) + Packet F1 (PARTIAL, surfaces)

**A3 — sewing nonmanifold/seam/tolerance-budget** · dirs: `12-3a-shells` · 8 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `sew-nonmanifold-candidate-disambiguation` (PARTIAL) | 3+ shells meeting along a cylindrical seam (not M045's planar-only overlap) so the closed-surface `IsUClosedSurface`/`IsVClosedSurface`+`IsMergedClosed` disqualification arm actually engages | 1 | M045, Tsh013 |
| `sew-nonmanifold-multi-edge-merge-chain` (PARTIAL, unproven) | 3 distinct edge sections (not Sw001's accidental 2) genuinely requiring the transitive `myCuttingNode` adjacency walk to fold into one non-manifold edge | 1 | Sw001, M045 |
| `sew-seam-dual-pcurve-preservation` (PARTIAL, needs reachable fixture) | A seam edge with only one explicit PCURVE (missing the dual forward+reversed pair) participating in an actual, reachable sewing merge — not Gp139's dead scaffold or Tsh209's unproven reachability | 1 | Tsh209 |
| `sew-tolerance-budget-acceptance-and-cap` (PARTIAL, missing 3 of 3, pick 2) | (a) A merge whose first attempt fails the quality bar, triggering the swapped-reference retry with a strictly-better second result; (b) a gap large enough to force the 23-point discretized-sampling fallback AND exceed a caller-set `MaxTolerance`, nullifying the resulting edge | 2 | Tsh187, N152/N153 |
| `sew-vertex-endpoint-pairing-orientation` (PARTIAL, single-fixture-thin) | Second clean cross-pairing (reversed relative orientation) fixture distinct from Tsh176, avoiding both Tsh086's different mechanism and M045's earlier-rejected-before-this-gate issue | 1 | Tsh176 |
| `bc-invalid-imbrication-of-shells` (PARTIAL, sole survivor crash-adjacent) | Two nested void shells (like Bo003) built to survive translation (avoid the signal-11 crash Bo003 hits) so `BRepCheck_Solid::Blind`'s imbrication check actually runs | 1 | Bo003 (fix the crash) |
| `bc-subshape-not-in-shape` (PARTIAL, only incidental hit) | Purpose-built duplicate-face-dedup scenario mirroring what accidentally triggered `SubshapeNotInShape` in Bo007 | 1 | Bo007 |

**F1 — surface splitting/continuity** · dirs: `12-2c-surfaces` · 5 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `tkshh-face-closed-surface-unsplit-at-seam` (PARTIAL, missing 3 of 9, pick 3) | (a) A torus face closed in both U and V, forcing the recursive second split after the first; (b) a V-closed-only face (sphere/cone pole direction) exercising the V fallback; (c) a face trimmed to within tolerance of a full period (thin near-closed face) forcing the `RectangularTrimmedSurface` half-surface closure test | 3 | Gs193 |
| `tkshh-surface-curve-continuity-below-required` (PARTIAL, missing 2 of 8, pick 2) | (a) A surface-of-revolution or linear-extrusion face whose C0 BASIS CURVE (not the surface itself) forces the split; (b) a geometrically-smooth over-multiplied knot repaired by knot REMOVAL instead of splitting | 2 | Gs049 |

### Wave 7 — Packet A4 (PARTIAL, step-reader shells) + Packet F2 (PARTIAL, nurbs+surfaces)

**A4 — step-reader shell/solid mechanics** · dirs: `12-3a-shells` · 7 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `stp-nm-shared-entity-reuse` (PARTIAL, missing 2) | (a) A cross-shell fixture where the SAME EDGE_CURVE entity is genuinely shared (not independently duplicated per shell like M045) across 2+ OPEN_SHELLs; (b) an I-DEAS-header fixture where the same logical entity appears under 2 distinct STEP ids sharing one Name string, requiring name-matched reuse | 2 | Tsh019 |
| `stp-partial-assembly-continuation` (PARTIAL, missing 3 of 5, pick 3) | (a) A BREP_WITH_VOIDS with a genuinely FAILING void shell (untranslatable) alongside a good outer shell; (b) an EDGE_BASED_WIREFRAME_MODEL or FACE_BASED_SURFACE_MODEL with one failing member; (c) a RECTANGULAR_COMPOSITE_SURFACE with one failing patch | 3 | Bo002 |
| `stp-shell-to-solid-promotion` (PARTIAL, unconfirmed) | Same closed-tetrahedron-in-OPEN_SHELL/SBSM pattern as Tsh003 but with tier-3 metadata that explicitly asserts the promoted output is a `TopoDS_SOLID` (not just `shape(1)`) | 1 | Tsh003 |
| `tkshh-face-small-area-wire` (PARTIAL, missing cross-face cascade) | A face whose entire outer boundary is composed of edges shared only with a removed internal-wire's small hole, on a neighboring face, so removing the small wire cascades into removing the whole neighbor face | 1 | Tsh124 (unexpanded placeholder — write it out properly) |

**F2 — heal-sequence representation-normalization + sewing/step-reader surfaces** · dirs: `12-2b-nurbs`, `12-2c-surfaces` · 10 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `seq-bspline-restriction` (PARTIAL, missing 1 of 4) | Rational B-spline surface/curve where the target requires polynomial (non-rational) form — exercises the rational-to-polynomial re-approximation | 1 | Gn011 |
| `seq-elementary-to-revolution` (PARTIAL, weak) | An analytic CYLINDRICAL_SURFACE/CONICAL_SURFACE in a context requiring SURFACE_OF_REVOLUTION representation (the direction N030/Gn015 don't cover) | 1 | Gn013 |
| `seq-swept-to-elementary` (PARTIAL, missing swept-source direction) | A cylinder authored as a SURFACE_OF_REVOLUTION sweeping a straight generatrix line (not a B-spline already resembling a cylinder) — exercises canonical-form recovery from a genuinely swept source | 1 | N030, Gn015 |
| `sew-degenerate-edge-passthrough` (PARTIAL, weak negative-control framing) | Same cone-apex/sphere-pole degenerate-edge-present shell as Gs189, reframed in catalog metadata as a "must NOT be altered" negative control rather than a defect fixture | 1 | Gs189 |
| `sew-seam-closed-surface-merge` (PARTIAL, missing 2 of 3) | (a) V-periodic seam-merge validation (torus/sphere V-direction, not Tsh209's U-closed cylinder); (b) closure detected via the isoline-distance fallback (a trimmed/offset surface that doesn't self-report `IsUClosed`/`IsVClosed`) | 2 | Tsh209 |
| `stp-edge-curve-param-range` (PARTIAL, missing 3 of 6) | (a) Trim parameter outside a bounded non-periodic curve's own definition range, forcing a clamp; (b) a B-spline curve closed only within 3D tolerance (not formally flagged `Closed`); (c) trim parameters in reverse order on an ordinary (non-periodic, non-closed) curve, forcing a curve-reverse + parameter swap | 3 | Gs029 |
| `stp-vertexloop-bound-mismatch` (PARTIAL, missing 1 of 3) | VERTEX_LOOP used as a face bound on a TOROIDAL_SURFACE — the silent-skip branch, distinct from the sphere/plane subvariants already covered | 1 | Gs039 |

### Wave 8 — Packet B3 (PARTIAL, wires — small) + Packet D3 (PARTIAL, pcurves — small)

**B3 — wire mechanics tail** · dirs: `12-3b-wires` · 6 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `bc-invalid-degenerated-flag` (PARTIAL) | A positive-length LINE wrapped in a SEAM_CURVE with zero-length pcurve (Twi083's exact defect pattern), wired into a real ADVANCED_FACE/CONICAL_SURFACE (not GEOMETRIC_CURVE_SET) so the flag genuinely lies on translated geometry | 1 | Twi083 (fix: face-host it) |
| `tkshh-wire-small-edge` (PARTIAL, missing 3 of 9, pick 3) | (a) A small SEAM edge on a periodic face, requiring seam-with-seam merge specifically; (b) a drop-mode-only case where the small edge cannot be merged into any neighbor and must be dropped with connectivity re-check; (c) a multi-face configuration where a circle-like closed curve must NOT be collapsed (protection case) | 3 | Twi013 |
| `stp-makeedge-validity-fallback` (PARTIAL, missing 2 of 5) | (a) A vertex point that cannot be projected onto the 3D curve at all (e.g. off the curve's plane for a planar curve type); (b) a projected point with an infinite curve parameter (e.g. projecting onto an unbounded line far from the defined segment) | 2 | Twi086 |

**D3 — pcurve mechanics tail** · dirs: `12-2a-pcurves` · 5 fixtures

| item | spec | count | mirror |
|---|---|---:|---|
| `stp-pcurve-trim-range-repair` (PARTIAL, missing 2 of 3) | (a) A pcurve whose 2D trim parameters literally collapse to a point (w1==w2) on an otherwise real, non-degenerate 3D edge — pcurve dropped, edge kept 3D-only; (b) a pcurve range that straddles a U-periodic surface's seam in the wrong order (w1>w2), forcing `ElCLib::AdjustPeriodic` re-basing | 2 | Gp007 |
| `stp-seam-pcurve-selection` (PARTIAL, missing 2 of 3) | (a) A CATIA-style pseudo-seam where two DIFFERENT faces (not one face, two wires) are built on the same not-formally-closed surface, sharing edge geometry across two wires — exercises `IsLikeSeam`; (b) a genuinely ambiguous forward-pcurve case that hard-fails edge translation | 2 | Gp013 (formal-seam case — build the cross-face pseudo-seam and the hard-fail case) |
| `stp-transfer-exception-to-fail` (PARTIAL, narrow breadth) | A COMPOSITE_CURVE segment whose per-segment 3D-curve or pcurve conversion throws mid-translation (numerically degenerate segment geometry), demonstrating the segment-dropped-not-whole-curve-aborted catch site (distinct call site from Ad043/Xp008's already-covered root-entity and per-edge catches) | 1 | Ad043 |

---

## 3. Wave summary

| wave | packets | dirs touched (disjoint within wave) | fixtures |
|---:|---|---|---:|
| 1 | A1 + B1 | `12-3a-shells` / `12-3b-wires` | 8 + 8 = 16 |
| 2 | C1 + D1 | `12-3c-faces` / `12-2a-pcurves` | 8 + 8 = 16 |
| 3 | JL + GHIK | `12-8-mixed`+`12-11-adversarial` / `12-5-units`+`12-4-tolerance`+`12-6-assembly`+`12-1b-header` | 8 + 10 = 18 |
| 4 | A2 + B2 | `12-3a-shells` / `12-3b-wires` | 8 + 8 = 16 |
| 5 | C2 + D2 | `12-3c-faces` / `12-2a-pcurves` | 3 + 8 = 11 |
| 6 | A3 + F1 | `12-3a-shells` / `12-2c-surfaces` | 8 + 5 = 13 |
| 7 | A4 + F2 | `12-3a-shells` / `12-2b-nurbs`+`12-2c-surfaces` | 7 + 10 = 17 |
| 8 | B3 + D3 | `12-3b-wires` / `12-2a-pcurves` | 6 + 5 = 11 |
| **total** | **16 packets** | | **118** |

Note on disjointness: within every wave, the two packets' directory sets are disjoint by
construction — the four biggest families (shells/wires/faces/pcurves) never share a directory
with each other, and the smaller families (surfaces, nurbs, units/tolerance/assembly/header,
mixed/adversarial) are disjoint from all four and from each other except where explicitly grouped
into the same packet (F1+F2 both touch `12-2c-surfaces`, so they are never paired against each
other — see Wave 6/7 assignments). Across waves (sequential, not parallel), directory reuse is
expected and fine (e.g. `12-3a-shells` is touched by A1, A2, A3, A4 in four different waves).

---

## 4. Projected coverage after each wave

Baseline (before any wave): honest denominator 171 → **86 COVERED (50.3%) / 63 PARTIAL (36.8%) /
22 GAP (12.9%)** · COVERED-or-PARTIAL = 149/171 = **87.1%**.

Assumption for this table: every problem class targeted by a wave's packets is assumed to reach
COVERED once its fixtures land and pass verification (i.e. the fixture spec above is assumed to
fully satisfy the class's remaining named subvariants). This is the same aspirational framing
used elsewhere in this project's planning docs — actual post-verification numbers historically
run a `~30%` overturn rate lower on first pass (see `VERDICT_AUDIT.md`); re-run
`merge_coverage.py` after each wave lands to get the real number.

| after wave | GAP→COVERED (cum.) | PARTIAL→COVERED (cum.) | COVERED | PARTIAL | GAP | %COVERED | %COVERED-or-PARTIAL |
|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 0 | 0 | 86 | 63 | 22 | 50.3% | 87.1% |
| 1 (A1+B1) | 6 | 3 | 95 | 60 | 16 | 55.6% | 90.6% |
| 2 (C1+D1) | 11 | 10 | 107 | 53 | 11 | 62.6% | 93.6% |
| 3 (JL+GHIK) | 19 | 18 | 123 | 45 | 3 | 71.9% | 98.2% |
| 4 (A2+B2) | 20 | 27 | 133 | 36 | 2* | 77.8% | 98.8% |
| 5 (C2+D2) | 20 | 37 | 143 | 26 | 2* | 83.6% | 98.8% |
| 6 (A3+F1) | 20 | 46 | 152 | 17 | 2* | 88.9% | 98.8% |
| 7 (A4+F2) | 20 | 57 | 163 | 6 | 2* | 95.3% | 98.8% |
| 8 (B3+D3) | 20 | 63 | 169 | 0 | 2* | **98.8%** | **98.8%** |

\* The residual 2 GAP after Wave 4 are the two in-flight items excluded from this plan (§1b), not
addressable by any packet here. If/when those land COVERED via the sibling agents' work, the
denominator reaches **171/171 = 100%** COVERED-or-PARTIAL and ~100% COVERED on the honest
STEP-exercisable (post-carve-out) denominator.

---

## 5. Execution notes

- Packets run 2-at-a-time in parallel worktrees per wave, in the order given in §3. Waves
  themselves are sequential (Wave 2 should not start until Wave 1's packets have merged, since
  later PARTIAL packets sometimes assume earlier GAP-derived fixtures exist as mirrors — though no
  packet has a hard dependency on another packet's *output*, only on its *spec* as a reference).
- Every fixture spec above should go through this project's standard verification bar before its
  class's verdict is actually flipped in `problems.json`: read the catalog entry, read the `.stp`
  bytes, confirm reachability (not orphaned in a `GEOMETRIC_CURVE_SET`/dead scaffold per
  `feedback_orphaned_defect_carrier`), and confirm the fixture doesn't crash OCCT before the
  mechanism it's meant to demonstrate gets to run (the single most common failure mode surfaced by
  `COVERED_FULL_REVERIFY.md`/`VERDICT_AUDIT.md` across this whole queue).
- After each wave, re-run `occt-coverage/merge_coverage.py` and diff against §4's projection;
  large deviations likely mean a fixture didn't survive verification and should be triaged before
  the next wave starts (same "structural-grep-verify before quarantine" discipline as prior audit
  passes — see `feedback_audit_pattern.md`).
- `bc-no-surface` and the `stp-tess-dangling-brep-link` face subvariant are specified as **one
  shared fixture** in packet JL — author it once, cite it for both classes.
