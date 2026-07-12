# Full re-verification of the 43 unaudited COVERED verdicts

Completion of the stratified audit in `VERDICT_AUDIT.md`: that audit sampled 26 of the 69
COVERED verdicts in `problems.json` and overturned 10 (8 → PARTIAL, 2 → GAP). This pass
re-verifies the **43 COVERED verdicts the audit did not sample** (69 minus the 26 sampled),
using the same method: for each class, every cited fixture's **raw `.stp` bytes** and its
`STEP_PROBLEM_CATALOG.md` entry (including the structured `Expected validation` / tier-3
block) were re-read and the verdict re-derived — mechanism present in the bytes, on the
defect path, reachable from a live translated shape, every named subvariant demonstrated.
The three known failure modes (orphaned/dead defect carrier, adjacent-mechanism credit,
crash-as-coverage) were checked for every fixture; verification ran as three independent
byte-reading passes (stp-reader, BRepCheck part 1, BRepCheck part 2 + heal-sequence) with
Expected-block spot-checks on every overturn.

## Headline

| | classes | UPHOLD | → PARTIAL | → GAP | downgrade rate |
|---|---:|---:|---:|---:|---:|
| **This pass (unaudited 43)** | **43** | **31** | **5** | **7** | **28%** |
| stp-reader (14) + bc-no-3d-curve | 15 | 9 | 2 | 4 | 40% |
| BRepCheck detect-only | 19 | 14 | 2 | 3 | 26% |
| heal-sequence operators | 9 | 8 | 1 | 0 | 11% |

The sampled audit's 38% overturn rate extrapolated well for stp-reader classes and
over-predicted for heal-sequence classes. Notably, the downgrade *mix* shifted: this
unaudited slice contains proportionally more full collapses (7 GAP vs 5 PARTIAL) than the
sample (2 GAP vs 8 PARTIAL), because four stp classes and three bc classes rested entirely
on orphaned/crashing/never-fired fixtures.

## Verdicts (43)

| problem_id | verdict | evidence one-liner |
|---|---|---|
| `stp-closed-curve-two-vertices` | UPHOLD | Twi017 byte-verified: full CIRCLE EDGE_CURVE with two distinct VERTEX_POINTs both at (1,0,0), wired into real ADVANCED_FACE/OPEN_SHELL, occt=shape(1); Gp171 same pattern at 1e-8 offset. |
| `stp-loop-degenerate-edge-drop` | UPHOLD | Twi018: same-vertex EDGE_CURVE(#11,#11,#17) is one of 5 ORIENTED_EDGEs in a real EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE, occt=shape(1) — wire genuinely completes after the bad edge drops. |
| `stp-surface-force-periodic` | UPHOLD | Gs005 real ADVANCED_FACE #75 on B_SPLINE_SURFACE #11, tier-3 `is_u_periodic==True`, occt=shape(1); Gp013/Tfa197 same tier-3 signal. (Gs005's stale header comment "shape_null=True" contradicted by Expected block.) |
| `stp-edgeloop-empty` | UPHOLD | Twi001 (bare `EDGE_LOOP('',())` wired to sole ADVANCED_FACE, occt=shape(1)) and Xp008 (#129 empty loop is one of 6 faces in a real CLOSED_SHELL/MANIFOLD_SOLID_BREP, occt=shape(1)). |
| `stp-seam-pcurve-selection` | DOWNGRADE→PARTIAL | "Formal seam, edge twice in one wire" survives strongly (Gs193/Gp011/Twi022/Gp013/Gs028/Gp119, all byte-verified single-face double-references); "pseudo-seam across two different faces/wires" undemonstrated (every fixture is single-face); "forward-pcurve-indeterminate hard-fail" undemonstrated (all 6 succeed with shape(1), none hard-fails). |
| `stp-pcurve-basis-surface-match` | UPHOLD | Gp172 byte-verified: PCURVE #30 has basis_surface=#11 (cylinder) instead of #6 (plane) on a real 2-face shell, tier-3 n_faces==2; Gp012 (null `$` slot) and Gp010 (3D LINE in pcurve slot) also genuine and reachable. |
| `stp-compcurve-cyclic-ref` | UPHOLD | Gs054: COMPOSITE_CURVE_SEGMENT #29's parent_curve is #30, the very COMPOSITE_CURVE containing it, wired into real EDGE_CURVE → ADVANCED_FACE, occt=shape(1). |
| `stp-compcurve-infinite-segment` | UPHOLD | Gs055: segment #14's parent_curve is TRIMMED_CURVE(-1e40,+1e40), genuinely unbounded, wired into real EDGE_CURVE → ADVANCED_FACE, occt=shape(1). |
| `stp-polyloop-nonplanar-surface` | UPHOLD | M055: POLY_LOOP #10 with 4 non-coplanar points on a CYLINDRICAL_SURFACE, wired through CLOSED_SHELL → FACETED_BREP → ABSR, occt=shape(1). |
| `stp-missing-geometry-definition` | DOWNGRADE→GAP | Xp008's null-geometry face #138 is never referenced by CLOSED_SHELL #139 (dead trailing entity); Tfa003's topological items sit inside a GEOMETRIC_CURVE_SET whose builder dispatch only accepts GeometricRepresentationItems (type-skipped, never reaches TranslateEdge::Init); Ad005/Bo002/Ad123 demonstrate dangling-refs-to-undeclared-IDs (different mechanism) and are structurally disconnected. No fixture reaches any of the 4 cited OCCT functions on live topology. |
| `stp-shell-to-solid-promotion` | DOWNGRADE→PARTIAL | Tsh003 (genuinely closed all-vertices-shared 4-face tetrahedron in OPEN_SHELL/SBSM, occt=shape(1)) plausibly supports promotion, though no tier-3 field confirms a TopoDS_Solid was produced; A102 (deliberately open 7/8-face) and P015 ("re-import yields zero solids") demonstrate *failure* to promote; M052 is a broken one-triangle `'placeholder'` stub. |
| `stp-missing-unit-context-default` | DOWNGRADE→GAP | M063's no-unit SHAPE_REPRESENTATION #8 is a member of GEOMETRIC_CURVE_SET #9 — not a GeometricRepresentationItem, silently type-skipped, never independently transferred (its shape(1) comes from the outer, properly-unitted rep); N028/N018 record occt=empty/empty; Xp002 records occt=signal(11). No graceful default-and-continue is ever exercised. |
| `stp-srr-nauo-reversed` | DOWNGRADE→GAP | M062 stuffs NAUO/SRR/PRODUCT_DEFINITION entities into a GEOMETRIC_CURVE_SET (type-skipped, occt=empty); A034 demonstrates an unrelated SHAPE_ASPECT-vs-PROPERTY_DEFINITION null-deref crash, not SRR/NAUO direction reversal. |
| `stp-geomset-gri-fallback` | DOWNGRADE→GAP | Sole fixture M051 records occt=signal(11)/signal(11) — a crash directly contradicts the claim that the fallback transfer succeeds and "a shape is still produced". |
| `bc-no-3d-curve` | UPHOLD | Twi047 byte-verified: four EDGE_CURVEs whose SURFACE_CURVE carries only a PCURVE (no Geom_Curve) bounding a live square ADVANCED_FACE, occt=shape(1), consistent with detect-only; Twi088 is an orphaned GEOMETRIC_CURVE_SET (occt=empty) and pruned. |
| `bc-no-curve-on-surface` | DOWNGRADE→GAP | All 4 cited fixtures (Gp001, Gp042, Gp019, Xp002) show occt=signal(11) — OCCT crashes before BRepCheck can ever run; classic crash-as-coverage, nothing survives live. |
| `bc-invalid-curve-on-surface` | UPHOLD | Gp041 (0.1mm PCURVE midspan offset vs 0.001mm tol, occt=shape(1)) and Gp021 (skewed pcurve LINE direction, shape(1)) genuine live demonstrations; N004/Twi070 dead (shape_null==True) and pruned. |
| `bc-invalid-curve-on-closed-surface` | UPHOLD | Twi022 (SEAM_CURVE same-pcurve-twice, shape(1)) and Gp011 (`SEAM_CURVE('',#3d,(#pc,#pc),...)`, shape(1)) genuine; Gp013 verified live-periodic post-translation; Twi071 dead and pruned. |
| `bc-free-edge` | UPHOLD | Tsh029: 5-face CLOSED_SHELL missing top face leaves 4 rim edges valence-1, occt=shape(1); Tsh044/Tsh072 reinforce; Tsh118 crashes (signal-11) and is pruned. |
| `bc-invalid-multi-connexity` | UPHOLD | Bo006 byte-verified: EDGE_CURVE #25 referenced by ORIENTED_EDGEs in 3 distinct faces (#78/#80/#82) of one live CLOSED_SHELL/MANIFOLD_SOLID_BREP; Tsh019 (incidence 4) and Tsh232 (incidence 3) confirm; Sw001 pruned — max incidence is actually 2 (same EDGE_LOOP #61 wrapped twice). |
| `bc-invalid-range` | UPHOLD | Gp007: edge domain [0,2.5] vs pcurve domain [0,1], occt=shape(1); Gp103 (CIRCLE-vs-trim mismatch) reinforces; Gp047 (crash) and Gp086 (dead) pruned. |
| `bc-empty-wire` | UPHOLD | Twi001 and Tsh023: literal `EDGE_LOOP('',())` wired via FACE_OUTER_BOUND → ADVANCED_FACE into a live OPEN_SHELL (shape(1)); Tfa246 pruned — its empty EDGE_LOOP (#9063–#9065) is a trailing orphan with zero back-references. |
| `bc-self-intersecting-wire` | DOWNGRADE→GAP | Geometry is live/reachable in all 4 fixtures but none survive as detect evidence: Twi049/Twi076 carry the corpus's explicit fixture-specific "the validity-checker does not flag [this]… tier-3 valid-flag should be ignored" annotation (confirmed non-firing); Twi157 cites ShapeAnalysis_Wire::CheckSelfIntersection (ShapeHealing, not BRepCheck_Wire — adjacent mechanism); Xp001 shares Twi049's exact pattern with no independent detection confirmation. |
| `bc-no-surface` | DOWNGRADE→GAP | Tfa001/Tfa054's own tier-3 assertion is `brepcheck.valid == True`, directly contradicting each fixture's embedded "must be False" comment — OCCT drops the null-face_geometry face before BRepCheck ever examines it; Sw004 cites BRepBuilderAPI_FastSewing (wrong subsystem) and confirms the same silent-drop (`n_faces_total==1` of 2 declared). |
| `bc-intersecting-wires` | DOWNGRADE→PARTIAL | Tfa039 survives (genuine outer/inner-wire UV crossing on a live OPEN_SHELL, matches BRepCheck_Face.cxx:279) though firing is unconfirmed; Tfa055 carries the explicit "validity-checker does not flag" annotation (confirmed non-firing); Tfa126 crashes (signal-11). |
| `bc-invalid-imbrication-of-wires` | UPHOLD | Tfa056 (hole-inside-hole, byte-verified edge_count==12) and Twi024 (inner wire same winding as outer, byte-verified) both live (occt=shape(1)) with no contradicting checker-firing evidence. |
| `bc-empty-shell` | UPHOLD | Bo001 byte-verified: `CLOSED_SHELL('outer',())` is the actual outer of MANIFOLD_SOLID_BREP wired to ABSR, occt=shape(1). Tsh077 structurally reachable but occt=unknown/unknown (never oracle-run) — flagged, not pruned. |
| `bc-redundant-face` | UPHOLD | Bo007 byte-verified: `CLOSED_SHELL('bo007_duplicate_face',(#36,#36))` — identical ADVANCED_FACE listed twice in a live MANIFOLD_SOLID_BREP, occt=shape(1). Sole fixture, unambiguous. |
| `bc-invalid-imbrication-of-shells` | DOWNGRADE→PARTIAL | Bo003 — the crisp two-nested-voids match with an explicit "OCCT fires InvalidImbricationOfShells" comment — crashes (signal-11), never reaching BRepCheck; Tsh067 (void protrudes through outer shell) is live and reachable (shape(1)) but is a related protrusion variant with no confirmation the named status fires. |
| `bc-unorientable-shape` | UPHOLD | Bo005 genuine: 3-face band with ADVANCED_FACE #82 `.F.` baking an orientation contradiction into live closed-loop topology, occt=shape(1); Tsh075/Tsh078 are occt=unknown/unknown (never oracle-run) and pruned — class survives on Bo005 alone (no subvariants). |
| `bc-not-closed` | UPHOLD | Wire level: Twi053/Twi034/Twi066 genuine open EDGE_LOOPs on live faces (shape(1)); shell level: Tsh029 (5-of-6-face CLOSED_SHELL) + Hea002 (MANIFOLD_SOLID_BREP wrapping OPEN_SHELL), both shape(1); Tsh118 (crash) struck. |
| `bc-not-connected` | UPHOLD | Twi003 (adjacent edges' VERTEX_POINTs genuinely offset, shape(1)) covers wire level; Bo022 (12-face CLOSED_SHELL in two disjoint vertex-sets, shape(1)) covers shell level; Twi068 (dead, shape_null==True) struck. |
| `bc-bad-orientation-of-subshape` | UPHOLD | Tsh011 wire-traced: ORIENTED_EDGE #26=.F. breaks head-to-tail chaining, flipping it fixes the loop (shape(1)); Tfa057/Ps010/Ps002 reversed-wire patterns confirmed against BRepCheck_Face::OrientationOfWires source; Tsh116 (crash) struck. |
| `bc-enclosed-region` | UPHOLD | Only Tsh015 survives: BREP_WITH_VOIDS with void shell oriented .T. (2 direct child shells, shape(1)) matches BRepCheck_Solid.cxx:297's ≥2-growths trigger; Bo004 has ONE CLOSED_SHELL (aNbVTS<2 early-returns — structurally cannot fire) and Bo003 crashes. Single-fixture base. |
| `seq-fix-shape` | (sampled — see VERDICT_AUDIT.md) | — |
| `seq-direct-faces` | UPHOLD | Ps003/Tsh032/Tsh010: single ADVANCED_FACE same_sense=.F. vs unmoved surface normal, wired into CLOSED_SHELL → MANIFOLD_SOLID_BREP, all occt=shape(1); Ad047 (no SHAPE_REPRESENTATION wrapper at all, occt=empty) pruned. |
| `seq-same-parameter` | UPHOLD | Gp022/Gp050 wire the pcurve↔3D-curve parameter desync through PCURVE → SURFACE_CURVE → EDGE_CURVE on live faces (shape(1)); Gp074/Gp130 (both shape_null==True) pruned. |
| `seq-split-angle` | UPHOLD | Twi032 (full-360° CYLINDRICAL_SURFACE single face, no seam) and Gs193 (full-360° CONICAL_SURFACE) both wired into shell/solid reps, occt=shape(1); no bogus citations. |
| `seq-to-bezier` | UPHOLD | Gn042 (interior double-knot surface) and Gn044 (degree-1 pcurve needing elevation) live (shape(1)); but Gn017/Gn052 are occt=empty and Gn058 crashes — 3 of 5 citations pruned. |
| `seq-split-continuity` | DOWNGRADE→PARTIAL | Pcurve subvariant survives (Gp120 composite-pcurve G0 kink, shape(1)); surface subvariant survives (Gs049/Gs070 C0 interior-knot surface as face_geometry, shape(1)); curve subvariant fails — Gp033 is occt=empty (shape_null==True) and Gn172's defect B-spline #6 is referenced by NO EDGE_CURVE/PCURVE (the green shape(1) is an unrelated flat quad of LINE edges — orphan hidden behind a live translation). |
| `seq-fix-wire-gaps` | UPHOLD | 3D subvariant: Twi053 (14.14-unit missing-edge gap) + Twi003 (4× 0.01-unit junction mismatches), both live; 2D subvariant: Gp020 (ΔU=0.05 pcurve gap at shared VERTEX_POINT #10, shape(1)); Gp034 pruned (gap is internal to a COMPOSITE_CURVE backing ONE edge — wire itself gapless, adjacent mechanism). |
| `seq-fix-face-size` | UPHOLD | Spot: Tfa072 (live CLOSED_SHELL, shape(1)); spot+strip: Tfa040 (area 1e-9, aspect ~1000, live OPEN_SHELL). Tfa073 (GEOMETRIC_CURVE_SET orphan), Tsh028 (its "sliver" is a normal ~0.5-area triangle; real defect is STYLED_ITEM loss), Tfa014 (0.05×0.05 square, by its own comment neither spot nor strip) all pruned. |
| `seq-split-closed-edges` | UPHOLD | Only Twi019 survives: full-360° CIRCLE EDGE_CURVE #13 with start==end vertex #7 wired into OPEN_SHELL (shape(1)); Twi099/Twi084 dead AND wrong-mechanism; Twi017 live but its defect (two distinct vertices at one point) is fixed by vertex-merge, not edge-split. Single-fixture base. |
| `seq-split-common-vertex` | UPHOLD | Only Twi009 survives: FACE_OUTER_BOUND #46 and FACE_BOUND #85 (hole) both reference VERTEX_POINT #7 at (0.5,0.5,0) — the exact two-wire pinch SplitCommonVertex targets, live OPEN_SHELL; Gs034 pruned (single-wire figure-eight — the sibling class). Single-fixture base. |

(`seq-fix-shape` row included only to note it was in the sampled set, not this pass; the
42 other rows plus `bc-no-3d-curve` above are the 43 re-verified classes.)

## Prune list (bogus fixture citations)

Citations that do not support their class and should be struck from `fixture_ids` on the
next `problems.json` revision. For the 7 classes downgraded to GAP, *all* citations are
implicitly struck; they are listed here anyway for grep-ability.

Dead / orphaned carriers (occt=empty, shape_null==True, or unreferenced entities):
- **Twi084** (`stp-closed-curve-two-vertices`): vertices 0.5 apart (not near-coincident) in an unreferenced GEOMETRIC_CURVE_SET, occt=empty. Also (`seq-split-closed-edges`): dead and wrong-mechanism.
- **Twi099** (`stp-loop-degenerate-edge-drop`, `seq-split-closed-edges`): single-edge orphaned GEOMETRIC_CURVE_SET, occt=empty.
- **Twi086** (`stp-loop-degenerate-edge-drop`): same pattern.
- **Gn033** (`stp-surface-force-periodic`): shape_null==True (C-1 break) contradicts successful force-to-periodic.
- **Tfa246** (`stp-edgeloop-empty`, `bc-empty-wire`): the empty EDGE_LOOP (#9063–#9065) is a trailing orphan with zero back-references — third and fourth classes this fixture has now been struck from (see VERDICT_AUDIT.md).
- **Ad085** (`stp-compcurve-cyclic-ref`): all entities disconnected, no SHAPE_REPRESENTATION anywhere in the file.
- **Xp008** (`stp-missing-geometry-definition`): null-geometry face #138 never referenced by its shell.
- **Tfa003** (`stp-missing-geometry-definition`): topological items type-skipped inside GEOMETRIC_CURVE_SET.
- **Ad005**, **Bo002**, **Ad123** (`stp-missing-geometry-definition`): dangling-undeclared-ID mechanism (different class), structurally disconnected.
- **M063**, **N028**, **N018** (`stp-missing-unit-context-default`): type-skipped inert / occt=empty.
- **M062** (`stp-srr-nauo-reversed`): NAUO/SRR entities type-skipped inside GEOMETRIC_CURVE_SET, occt=empty.
- **N004**, **Twi070** (`bc-invalid-curve-on-surface`): shape_null==True; N004 additionally targets the adjacent SameParameter-flag mechanism.
- **Twi071** (`bc-invalid-curve-on-closed-surface`): shape_null==True; placeholder-style assertions.
- **Gp086** (`bc-invalid-range`): shape_null==True.
- **Twi068** (`bc-not-connected`): shape_null==True.
- **Twi088** (`bc-no-3d-curve`): orphaned single-edge GEOMETRIC_CURVE_SET, occt=empty.
- **Ad047** (`seq-direct-faces`): ADVANCED_FACE never wrapped in any shell/rep, occt=empty.
- **Gp074**, **Gp130** (`seq-same-parameter`): shape_null==True.
- **Gn017**, **Gn052** (`seq-to-bezier`): occt=empty (Gn017's unrelated C-1 break kills translation).
- **Gp033** (`seq-split-continuity`): correctly wired C0 curve but occt=empty.
- **Gn172** (`seq-split-continuity`): defect B-spline #6 referenced by no EDGE_CURVE/PCURVE — orphan hidden behind a green occt=shape(1).
- **Tfa073** (`seq-fix-face-size`): ADVANCED_FACE inside GEOMETRIC_CURVE_SET, occt=empty.

Crash-as-coverage (occt=signal(11) — the cited branch provably never ran):
- **Ad050** (`stp-edgeloop-empty`); also no product scaffold at all.
- **Xp002** (`stp-missing-unit-context-default`; also one of the four all-crash citations of `bc-no-curve-on-surface` with **Gp001**, **Gp042**, **Gp019**).
- **M051** (`stp-geomset-gri-fallback`): sole fixture, crash.
- **Tsh118** (`bc-free-edge`, `bc-not-closed`): cited in two classes, crashes in both.
- **Gp047** (`bc-invalid-range`).
- **Tfa126** (`bc-intersecting-wires`).
- **Bo003** (`bc-invalid-imbrication-of-shells`, `bc-enclosed-region`): the canonical two-nested-voids fixture with an explicit "OCCT fires InvalidImbricationOfShells" comment — crashes before BRepCheck in both classes.
- **Tsh116** (`bc-bad-orientation-of-subshape`).
- **Gn058** (`seq-to-bezier`).

Wrong / adjacent mechanism (live geometry, wrong claim):
- **Twi002** (`stp-closed-curve-two-vertices`): edge geometry is an open LINE — the `IsClosed()==True` rebind path cannot trigger.
- **A102**, **P015** (`stp-shell-to-solid-promotion`): both explicitly demonstrate *failure* to promote (open shell / zero solids).
- **M052** (`stp-shell-to-solid-promotion`): broken one-triangle `'placeholder'` stub.
- **A034** (`stp-srr-nauo-reversed`): unrelated SHAPE_ASPECT null-deref crash.
- **Sw001** (`bc-invalid-multi-connexity`): max edge incidence is 2, not 3 — duplicate-face defect, wrong mechanism.
- **Sw004** (`bc-no-surface`): cites BRepBuilderAPI_FastSewing, not BRepCheck.
- **Twi157** (`bc-self-intersecting-wire`): cites ShapeAnalysis_Wire (ShapeHealing), not BRepCheck_Wire.
- **Gp034** (`seq-fix-wire-gaps`): gap internal to a COMPOSITE_CURVE backing one edge; the wire's junctions are gapless.
- **Tsh028** (`seq-fix-face-size`): "sliver" is a normal ~0.5-area triangle; real defect is STYLED_ITEM orphaning.
- **Tfa014** (`seq-fix-face-size`): 0.05×0.05 aspect-1:1 square — by its own comment neither spot nor strip.
- **Twi017** (`seq-split-closed-edges`): live, but the remedy for its defect is vertex-merge, not edge-split (it correctly serves `stp-closed-curve-two-vertices`).
- **Gs034** (`seq-split-common-vertex`): single-wire figure-eight — the sibling single-wire class, not two-wires-share-a-vertex.

Checker-does-not-fire (corpus's own annotation contradicts detect-coverage):
- **Twi049**, **Twi076**, **Xp001** (`bc-self-intersecting-wire`): explicit fixture-specific "the validity-checker does not flag [this]… tier-3 valid-flag should be ignored" annotation (Xp001 shares Twi049's exact pattern).
- **Tfa055** (`bc-intersecting-wires`): same annotation, confirmed non-firing.
- **Tfa001**, **Tfa054** (`bc-no-surface`): tier-3 `brepcheck.valid == True` directly contradicts their own embedded "must be False" comments.

Never-oracle-run (occt=unknown/unknown — cannot serve as evidence either way):
- **Tsh075**, **Tsh078** (`bc-unorientable-shape`): never oracle-run; own text says the mechanism crashes a downstream healer.
- (**Tsh077** in `bc-empty-shell` is the same state — flagged for oracle-run, not struck, since it is structurally reachable and the class already stands on Bo001.)

## Corrected exchange tallies

Starting point = `VERDICT_AUDIT.md`'s post-sample correction of the original 69/34/42:
**59 COVERED / 42 PARTIAL / 44 GAP**. Applying this pass's 12 downgrades (5 → PARTIAL,
7 → GAP):

| | classes | COVERED | PARTIAL | GAP |
|---|---:|---:|---:|---:|
| **All exchange-domain problem classes** | **145** | **47 (32.4%)** | **47 (32.4%)** | **51 (35.2%)** |
| sewing (`sew-*`) | 24 | 6 | 16 | 2 |
| STEP reader (`stp-*`) | 39 | 11 | 18 | 10 |
| heal-sequence (`seq-*`) | 20 | 12 | 6 | 2 |
| BRepCheck (`bc-*`) | 31 | 18 | 7 | 6 |
| IGES reader (`iges-*`) | 31 | 0 | 0 | 31 |
| **STEP-exercisable subset (excl. IGES)** | **114** | **47 (41.2%)** | **47 (41.2%)** | **20 (17.5%)** |

Every COVERED verdict in `problems.json` has now been re-verified exactly once (26 by the
stratified audit, 43 by this pass). Combined overturn rate across all 69: 22/69 (32%) —
13 → PARTIAL, 9 → GAP. The sampled audit's extrapolation ("expect ~16 ± 8 more downgrades,
true picture ~43 COVERED") was accurate: actual additional downgrades were 12, final
COVERED count 47.

## New cross-cutting findings (beyond VERDICT_AUDIT.md's three failure modes)

1. **Type-dispatch skip — a new orphan variant.** Non-GeometricRepresentationItem entities
   stuffed as `GEOMETRIC_CURVE_SET` members (NAUO/SRR/PRODUCT_DEFINITION in M062,
   `SHAPE_REPRESENTATION` in M063, `ADVANCED_FACE`/`EDGE_LOOP` in Tfa003) are silently
   skipped by `StepToTopoDS_Builder::Init(GeometricSet)`'s GRI-only dispatch. The file's
   own header comments insist the mechanism fires; it structurally cannot. This killed
   three stp classes.
2. **`occt=shape(1)` does NOT clear the orphan check.** Gn172 translates green while its
   defect B-spline is referenced by no EDGE_CURVE/PCURVE — the live shape is an unrelated
   healthy quad. Reachability must be traced *from the defect entity*, not inferred from a
   non-null file-level translation.
3. **`occt=unknown/unknown` is a fourth disqualifier** alongside empty/signal/adjacent:
   Tsh075/Tsh078/Tsh077 were never oracle-run at all and can support nothing.
4. **The corpus already self-reports non-firing checkers.** Fifteen fixture-specific
   "the validity-checker does not flag [this]" annotations exist corpus-wide (each names
   its defect — not boilerplate), plus tier-3 `brepcheck.valid` assertions that sometimes
   directly contradict a fixture's embedded intent comment (Tfa001/Tfa054). Three bc
   verdicts hinged on these. Recommendation: add a structured `brepcheck_fires: <status>`
   field per detect-only fixture so this is checkable without prose-mining.
5. **Catalog prose is unreliable; structured blocks are not.** The freeform `OCC behavior:`
   field is frequently stale verbatim boilerplate contradicting the `Expected validation`
   block (Gs005, Twi001, Ad050, Tsh023, M063, Ad123). Conversely, Ps010/Ps002 prose claims
   "passes BRepCheck" contradicted by BRepCheck source. Trust Expected/tier-3; flag prose
   for a correction pass.
6. **Severe citation rot even under upheld verdicts.** ~45% of the fixture citations
   examined in this pass were bogus. Three upheld classes now rest on a single fixture
   each (`bc-enclosed-region` → Tsh015, `seq-split-closed-edges` → Twi019,
   `seq-split-common-vertex` → Twi009) — one regression away from PARTIAL. Repeat
   offenders across multiple classes: Tfa246 (4 classes total incl. the sampled audit),
   Tsh118, Bo003, Twi099, Twi084, Xp002.
7. **Minor authoring bugs found in passing:** literal invalid `#?` Part-21 references in
   Twi022 and Twi088; Gs005's header comment claims `shape_null=True` while its Expected
   block records shape(1).
