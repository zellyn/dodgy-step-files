# Unintended OCCT segfault characterizations

8 fixtures trigger OCCT segfault (signal 11) when their catalog entries do NOT
explicitly predict a crash. This document characterizes each, identifying the
minimal trigger pattern, hypothesizing the failure path, and noting where the
catalog should be updated. All fixtures crash identically under both
`occt_heal_on` and `occt_heal_off`, and under gmsh's OCCT-backed reader as
well; diagnostics are empty (immediate signal 11 with no captured stderr),
which is itself diagnostic: the crash happens deep enough inside OCCT that
its message handler never gets to flush.

## Tsh023: Empty `EDGE_LOOP` and empty face/shell lists
- **Catalog claim**: STEP file with empty `EDGE_LOOP(...,())` "crashes reader",
  also `FACE_BASED_SURFACE_MODEL` / `OPEN_SHELL` with empty face lists.
- **Trigger pattern**: `#410=EDGE_LOOP('empty_edge_loop',())` cascading into
  `#420=ADVANCED_FACE` referencing it; combined with
  `#500=FACE_BASED_SURFACE_MODEL('empty_FBSM',())` and
  `#510=OPEN_SHELL('empty_shell',())`. Multiple defects in one file.
- **OCCT diagnostic before crash**: none captured (signal 11 with empty stderr).
- **Hypothesized failure path**: `STEPControl_ActorRead::TransferEntity` →
  `StepToTopoDS_TranslateEdgeLoop` iterates the (empty) `TColStd_HArray1OfTransient`
  and either dereferences a null-built wire when constructing the face, or
  later in `BRep_Builder::Add` when assembling the face, the inner shape handle
  is null and a downstream `TopoDS::Face(...)` cast on a null shape segfaults.
- **Severity vs catalog claim**: matches; catalog uses the word "crashes".
- **Suggested catalog update**: add `**Notes**: Observed: OCCT signal 11; crash
  occurs during shape translation, not parsing, so file is read past HEADER
  before abort.`

## Twi044: Internal wire below area threshold
- **Catalog claim**: face contains a tiny inner ("hole") wire with area below
  threshold (artifact, not real hole); kernel should heal via
  `ShapeFix_Face::FixSmallAreaWire` / `ShapeUpgrade_RemoveInternalWires`.
- **Trigger pattern**: 100 mm² square outer bound + ~5e-7 mm² inner triangle
  (vertices 1e-3 apart) on the same `ADVANCED_FACE`, wrapped in the minimal
  PRODUCT/SHAPE_DEFINITION_REPRESENTATION chain so OCCT actually invokes
  `TransferRoots`.
- **OCCT diagnostic before crash**: none captured.
- **Hypothesized failure path**: `BRepBuilderAPI` + `ShapeFix_Wire` interaction
  on a sub-tolerance wire. The 1e-3 mm vertex spacing is at or below the
  global uncertainty (1e-7) ratio that triggers `ShapeAnalysis_Wire` to
  collapse vertices; subsequent `BRepLib::SameParameter` recomputes
  pcurves on a degenerate edge whose 3D curve has zero length, yielding NaN
  parameters and a downstream null-pointer deref in pcurve evaluation.
  Alternative: `IntPatch` on collapsed wire produces empty intersection set,
  consumer reads `[0]` of an empty array.
- **Severity vs catalog claim**: stronger; catalog says "heal", does not say
  "may segfault if the kernel doesn't heal".
- **Suggested catalog update**: add `**Notes**: Observed: OCCT signal 11 in
  current build when this wire is reached during TransferRoots — confirms the
  "needs healing" claim with a hard-failure reproducer. Healing is not just
  cosmetic; absence of healing is a stability bug.`

## U008: NX subassemblies with mixed inch + mm
- **Catalog claim**: inch + mm contexts joined by `MAPPED_ITEM` cause
  inconsistent scaling; expected behavior is per-context unit application.
  Catalog frames this as a *scaling* defect, not a stability defect.
- **Trigger pattern**: two `GEOMETRIC_REPRESENTATION_CONTEXT`s (mm + inch via
  `CONVERSION_BASED_UNIT('INCH',...)`) referenced from sibling
  `SHAPE_REPRESENTATION`s, joined via `REPRESENTATION_MAP` →
  `MAPPED_ITEM` placed inside the mm-context assembly representation.
- **OCCT diagnostic before crash**: none captured.
- **Hypothesized failure path**: `STEPCAFControl_Reader` resolves the
  `MAPPED_ITEM` and looks up `representation_map.mapped_representation`'s
  context to fetch its unit. The cross-context reference confuses the
  context cache (`Transfer_TransientProcess` indexed by entity), and a later
  `XSAlgo_AlgoContainer::PrepareForTransfer` call dereferences a null
  context handle. Suspect: `UnitsMethods::DimensionalExponents` called on
  the wrong context, or null returned from a context-lookup map.
- **Severity vs catalog claim**: stronger; catalog only predicts mis-scale,
  not crash.
- **Suggested catalog update**: add `**Notes**: Observed: OCCT signal 11 on
  this minimal repro; cross-context MAPPED_ITEM appears to corrupt the
  Transfer context cache, escalating the defect from silent mis-scale to
  hard abort.`

## U009: KiCad board mm + component inch, naive merge
- **Catalog claim**: vendor inch component + mm board via `MAPPED_ITEM`;
  naive merger places components 25.4× off. Same family as U008, framed as
  a scaling defect, not a stability defect.
- **Trigger pattern**: identical structural pattern to U008: two
  `GEOMETRIC_REPRESENTATION_CONTEXT`s (mm board, inch component), one
  `MAPPED_ITEM` crossing the boundary, with the inch component placed at
  `(0.5, 0.5, 0.0)` inch coordinates. Smaller and PCB-styled compared to U008
  but the same shape of defect.
- **OCCT diagnostic before crash**: none captured.
- **Hypothesized failure path**: same as U008. Cross-context
  `MAPPED_ITEM` triggers a null deref in `STEPCAFControl_Reader` /
  `StepToGeom` context resolution. The fact that *both* U008 and U009
  segfault with no diagnostics, despite different geometric content but
  identical context-mixing pattern, strongly implicates the
  `MAPPED_ITEM`-with-foreign-context code path itself.
- **Severity vs catalog claim**: stronger; catalog only predicts mis-scale.
- **Suggested catalog update**: add `**Notes**: Observed: OCCT signal 11,
  same failure mode as U008. The two fixtures together isolate the cross-
  context MAPPED_ITEM as the trigger; geometric content is irrelevant.`

## A021: CDORSI WR1 violated by mixed style_context
- **Catalog claim**: `CONTEXT_DEPENDENT_OVER_RIDING_STYLED_ITEM` whose
  `style_context` mixes a `mapped_item` with `representation_relationship`s
  (violates WR1). Recommendation: kernels should accept it. Framed as a
  *conformance* / acceptance defect.
- **Trigger pattern**: `#98 = CONTEXT_DEPENDENT_OVER_RIDING_STYLED_ITEM(
  'view_hide',(#96),#67,#67,(#67,#84,#85))`. The fifth attribute mixes one
  `MAPPED_ITEM` (#67) with two `SHAPE_REPRESENTATION_RELATIONSHIP`s
  (#84, #85). Also notable: the `DRAUGHTING_MODEL` has an empty items list
  `()`, possibly a co-trigger.
- **OCCT diagnostic before crash**: none captured.
- **Hypothesized failure path**: `STEPCAFControl_Reader::ReadColors` /
  `STEPConstruct_Styles::LoadStyles` walks the `style_context` SELECT list
  expecting all elements to be of one type (per WR1). When a heterogeneous
  list reaches the dispatcher, the `Handle_Standard_Transient` downcasts
  produce a null Handle for the unexpected type, and `->Type()` /
  `->StyleContext()` is invoked on the null. Alternative: empty
  `DRAUGHTING_MODEL` items causes a null-shape lookup when the styled item
  is resolved.
- **Severity vs catalog claim**: stronger; catalog framed as "kernel should
  accept" (graceful degradation expected); observed is hard crash.
- **Suggested catalog update**: add `**Notes**: Observed: OCCT signal 11 on
  this minimal repro. The combined heterogeneous style_context plus empty
  DRAUGHTING_MODEL items list crashes the styled-item loader, escalating
  this from "kernel ought to accept" to "kernel currently aborts".`

## Pmi049: Tessellated solid with no styled_item
- **Catalog claim**: `TESSELLATED_SOLID` with no `STYLED_ITEM` referencing
  it; viewers default to neutral grey. Framed as a presentation/cosmetic
  defect.
- **Trigger pattern**: `#40=TESSELLATED_SOLID('unstyled_solid',(#35),$)` plus
  `#36=TESSELLATED_SHELL('shell',(#35),$)` both referencing the same
  `TRIANGULATED_FACE` `#35`. Notable secondary: the `SHAPE_REPRESENTATION`
  `#90` mixes an `AXIS2_PLACEMENT_3D` with a `TESSELLATED_SOLID`, and
  `ANNOTATION_PLANE` `#62` has an empty elements list. Also: file lacks the
  leading `ISO-10303-21;` token (block-comment first), so `starts_with_iso_token`
  is `false` per byte_signature, but the file is still parsed.
- **OCCT diagnostic before crash**: none captured.
- **Hypothesized failure path**: most likely the shared
  `TRIANGULATED_FACE` is consumed twice (once into `TESSELLATED_SHELL`, once
  into `TESSELLATED_SOLID`); OCCT's `RWStepVisual_RWTessellatedSolid` builds
  a `Poly_Triangulation` and stores it on the parent shape; second consumer
  receives the already-moved triangulation handle, downstream ownership /
  refcount logic produces a use-after-free or null-handle deref. Secondary
  candidate: missing `STYLED_ITEM` plus `ANNOTATION_PLANE` empty list trips
  XCAF color-applier null guard.
- **Severity vs catalog claim**: stronger; catalog only predicts visual
  drabness, not abort.
- **Suggested catalog update**: add `**Notes**: Observed: OCCT signal 11 on
  this fixture. Probable trigger is the shared TRIANGULATED_FACE between
  TESSELLATED_SHELL and TESSELLATED_SOLID rather than the missing
  styled_item per se; consider splitting into two fixtures (Pmi049a:
  unstyled-only, Pmi049b: shared-triangulated_face).`

## M005: "Number of facets" includes degenerates
- **Catalog claim**: writer-faithful facet count includes degenerate
  triangles (zero-area / collinear / repeated vertex). Some receivers strip
  them and report mismatch. Framed as a *validation property* defect.
- **Trigger pattern**: `#110=TRIANGULATED_FACE('flat',#100,$,$,(),
  ((1,2,3),(1,3,4),(1,5,2),(3,3,4)))`. The fourth triangle has repeated index
  `(3,3,4)`. Note the empty `pnindex` list `()` in attribute 5 (the
  fifth argument), which is suspicious in itself.
- **OCCT diagnostic before crash**: none captured.
- **Hypothesized failure path**: the `(3,3,4)` triangle has a repeated
  vertex index. `Poly_Triangulation::SetTriangle` accepts it, but downstream
  `BRepMesh_NormalEstimator` or `Poly::ComputeNormals` computes
  `(P3-P3) × (P4-P3) = (0,0,0)` and normalizes; division by zero produces
  NaN, which then propagates into a `Bnd_Box::Add` that asserts and
  segfaults. Alternative: empty `pnindex` list `()` in argument 5 is
  read as a zero-length array; subsequent `pnindex[0]` access is
  out-of-bounds.
- **Severity vs catalog claim**: stronger; catalog only predicts
  count-mismatch, not crash.
- **Suggested catalog update**: add `**Notes**: Observed: OCCT signal 11.
  Likely trigger: the repeated-index triangle (3,3,4) producing NaN normal,
  or the empty pnindex list. Either way the defect is a stability bug
  on top of the count-mismatch issue.`

## M018: Empty `TESSELLATED_SHELL((), $)`
- **Catalog claim**: `TESSELLATED_SHELL` argument 1 must be `BAG[1:?]` per
  schema; producer emits empty `()`. Catalog states "ReadFile crashes",
  which *is* an explicit crash claim.
- **Trigger pattern**: `#607638=TESSELLATED_SHELL('',(),$)` referenced by a
  `TESSELLATED_SHAPE_REPRESENTATION`. 5-entity file, near-minimal.
- **OCCT diagnostic before crash**: none captured.
- **Hypothesized failure path**: `RWStepVisual_RWTessellatedShell::ReadStep`
  reads the items array (length 0) and constructs a
  `StepVisual_HArray1OfTessellatedItem`. Constructing
  `Handle(TColStd_HArray1OfTransient)` with bounds `(1, 0)` either
  throws `Standard_RangeError` or yields a null handle; downstream the
  shell items getter returns a null array and `->Length()` /
  `->Value(1)` segfaults. Matches OCCT issue #667 documentation.
- **Severity vs catalog claim**: matches; catalog explicitly says
  "ReadFile crashes". (Re-reading: catalog *does* say "crashes",
  so this is catalog-consistent. Including here only because the task
  list named it; arguably should not have been counted as
  "no explicit crash predicted". Marking as catalog-consistent.)
- **Suggested catalog update**: minor; add `**Notes**: Observed: OCCT
  signal 11 (matches catalog claim and OCCT #667).`

## Summary

Of the 8 fixtures:

- **2 catalog-consistent** (catalog explicitly mentions crash):
  - `Tsh023`: catalog says "crashes reader"
  - `M018`: catalog says "ReadFile crashes"
- **6 stronger than catalog says** (catalog predicts a softer failure mode,
  observed is hard segfault):
  - `Twi044`: catalog says "needs healing"; observed: crash
  - `U008`: catalog says "mis-scaled"; observed: crash
  - `U009`: catalog says "mis-scaled"; observed: crash
  - `A021`: catalog says "kernel should accept"; observed: crash
  - `Pmi049`: catalog says "neutral grey"; observed: crash
  - `M005`: catalog says "count mismatch"; observed: crash

The pattern across the 6 stronger-than-catalog cases: all involve
attribute-level malformation (empty inner lists, sub-tolerance geometry,
heterogeneous SELECT lists, repeated indices, cross-context references)
that the catalog frames as semantic / cosmetic defects but that current
OCCT escalates to abort-on-read.

## Recommendation

1. For the 6 stronger-than-catalog fixtures (`Twi044`, `U008`, `U009`,
   `A021`, `Pmi049`, `M005`): update each `**Notes**` field to add
   `Observed: OCCT signal 11 on minimal repro — defect is a stability
   issue, not just <semantic / cosmetic / mis-scale>.` This warns
   downstream kernel implementers that hardening for these patterns is
   defensive-coding-required, not best-effort-quality-of-life.

2. For the 2 catalog-consistent fixtures (`Tsh023`, `M018`): light
   touch; add `Observed: OCCT signal 11 (matches catalog claim).` so
   the catalog distinguishes "predicted-and-confirmed" from
   "predicted-and-not-yet-tested".

3. Consider splitting `Pmi049` into two fixtures: the missing-styled_item
   case (cosmetic-only, the original catalog intent) and the
   shared-TRIANGULATED_FACE case (the actual crash trigger). The current
   file conflates both.

4. Empty diagnostics across all 8 (signal 11 with no captured stderr)
   suggests the crashes occur in the geometry/topology kernel below
   OCCT's `Message_Messenger` flush boundary, consistent with
   `BRepLib::SameParameter`, `Poly::ComputeNormals`, or
   `STEPCAFControl_Reader` context-cache deref hypotheses, and
   inconsistent with parser-level rejections (which would emit a Fail
   message before exiting cleanly).

5. None of these need to be filed upstream; the goal here is downstream
   kernel implementers' awareness, and OCCT users hitting these will
   already discover the crashes empirically.
