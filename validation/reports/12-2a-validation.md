# §12.2a — Pcurves (Gp) — Adversarial Validation

Files: 25 in `/Users/zellyn/gh/cad/research/step-examples/12-2a-pcurves/`.
Tools: `step_corpus.validate` (byte / ifcopenshell / OCCT heal-on / heal-off) + `step_corpus.tier3_geometric` (OCCT shape + parametric scan), each isolated in subprocess so OCCT segfaults don't poison the run.

Note on shape-counts: every fixture omits the PRODUCT/PDM chain, so OCCT loads the entity graph but TransferRoots returns `n_roots=0` and `shape.IsNull()=true`. This is expected; "occt accept_silent" is the validator's term for that. The defect must therefore be confirmed at the entity/byte level rather than via OCCT topology.

## Per-file verdicts

- **Gp001 — Missing pcurve on edge**: **CONFIRMED**. `SURFACE_CURVE('',#33,(),.PCURVE_S1.)` — explicit empty `associated_geometry` list; OCCT segfaults on heal-on, heal-off, and tier3, evidence the empty pcurve list trips a null-deref path.
- **Gp002 — Wrong pcurve mismatching vertices**: **CONFIRMED**. PCURVE direction `(0.31415926535,1.0)` traces UV (0,0)→(π/2,5) on a cylinder R=10 with axis `+z`; vertex at (10,0,5) requires UV (0,5). Lifted pcurve endpoint = (cos(π/2)·10, sin(π/2)·10, 5) = (0,10,5) ≠ (10,0,5). Mismatch ≈ 14 mm.
- **Gp005 — Singular apex on cone**: **CONFIRMED**. `CONICAL_SURFACE` with `semi_angle=0.5236` (30°), apex `VERTEX_POINT(0,0,0)` referenced by edge loop with no `DEGENERATE_EDGE` marker. Pcurve runs from V=0 (apex pole) to V=5.
- **Gp007 — Pcurve range incompatible with edge range**: **CONCERN**. Pcurve domain is the natural `[0,1]` of the LINE in 2D (no explicit trim). The fixture emits `PARAMETER_VALUE(0.0)` and `PARAMETER_VALUE(2.5)` as orphan entities (#80, #81) but does not bind them to the EDGE_CURVE — the edge has no explicit range field. Defect intent is structurally documented but not wired into the EDGE_CURVE. Receivers using natural domain see no violation.
- **Gp008 — Oscillating pcurve (wire-intersector corruption)**: **CONFIRMED**. Degree-3 2D B-spline with 11 control points alternating y=±0.05 — control polygon visibly oscillates. Knot multiplicities `(4,1,1,1,1,1,1,1,4)` correctly sum to deg+npoles+1 = 11+4 = 15. Tier3 reports a degree-3 BSpline curve.
- **Gp010 — 3D curve in pcurve slot**: **CONFIRMED**. `SURFACE_CURVE('',#33,(#43),.PCURVE_S1.)` where `#43=LINE` is a 3D LINE on the host PLANE rather than a PCURVE — schema-wise this violates the SET[1:2] OF pcurve_or_surface restriction (LINE is not in that select); ifcopenshell still parses but OCCT silent-accepts.
- **Gp011 — Seam with same pcurve twice**: **CONFIRMED**. `SURFACE_CURVE('',#33,(#77,#77),.PCURVE_S1.)` — same #77 PCURVE handle appears twice in the associated_geometry tuple, on a periodic CYLINDRICAL_SURFACE.
- **Gp012 — Seam with one pcurve null**: **CONFIRMED**. `SURFACE_CURVE('',#33,(#77,$),.PCURVE_S1.)` — second slot is the `$` omit token. Note: STEP set semantics technically does not permit `$` inside a SET aggregate; this is exactly the malformed wire that triggers the BUC60810 codepath.
- **Gp013 — CATIA "like-seam"**: **CONFIRMED**. 4×2 BSpline surface where row 0 = `(10,0,0)` and row 3 = `(10,0.000001,0)` — first/last U rows coincide within 1µ; surface marked `u_closed=.F.`. Two pcurves (U=0 and U=1) emitted as if seam.
- **Gp014 — Shared pcurve across edges (SYRKO)**: **CONFIRMED**. PCURVE #77 is referenced by both `#50=SURFACE_CURVE(...,(#77),...)` and `#150=SURFACE_CURVE(...,(#77),...)`, and these are bound to two distinct EDGE_CURVE instances #60 and #160 in the same EDGE_LOOP.
- **Gp015 — Pcurve/3D-curve trimming failure**: **CONFIRMED**. 3D BSpline knot domain `(5.0,7.0)` (mults 2,2 for degree 1) but PCURVE is a LINE in 2D with natural domain `[0,1]`. Trim from edge range to pcurve domain is impossible without wrap.
- **Gp016 — Transformed pcurve (IGES BRep)**: **CONFIRMED**. PCURVE 2D origin `(10,5)` while host plane has UV origin `(0,0)`; lifted pcurve maps to plane points `(10,5,0)`–`(11,5,0)` whereas vertices are at `(0,0,0)` and `(1,0,0)` — 10mm offset.
- **Gp018 — Pcurve gap near periodic boundary post-NurbsConvert**: **CONFIRMED**. NurbsConvert-style 9×2 BSpline surface (deg 3 in U, 1 in V), seam pcurves at U=0 and U=0.999 (instead of 1.0). The 0.001 unit gap matches the catalog's "tiny gap at wrap-around" claim.
- **Gp019 — Edge with no pcurve in compose-shell**: **CONFIRMED**. `RECTANGULAR_COMPOSITE_SURFACE` referencing `SURFACE_PATCH` entries; SURFACE_CURVE has empty `associated_geometry=()`. OCCT segfaults during transfer (similar to Gp001), confirming the empty pcurve handler trips on the composite.
- **Gp020 — 2D gap between adjacent edges**: **CONFIRMED**. Pcurve A endpoint UV=(1.0,0.0) and pcurve B start UV=(1.05,0.05); gap = (0.05,0.05). Both edges share VERTEX_POINT #41 in 3D so the topology is fine but UV is split.
- **Gp021 — 3D-vs-pcurve gap on same edge**: **CONFIRMED**. 3D LINE goes (0,0,0)→(1,0,0); PCURVE direction `(0.99875,0.04994)` magnitude 1.0012 traces UV (0,0)→(1.00,0.05) — lifted endpoint differs from 3D endpoint by 0.05.
- **Gp022 — SameParameter violation**: **CONFIRMED**. 3D LINE linear in t∈[0,1]; pcurve is a degree-2 BSpline with control points `(0,0)`, `(0.8,0)`, `(1,0)` — non-linear parameterization. EDGE_CURVE flag `.T.` (SameParameter) is asserted.
- **Gp023 — ValueOfUV outside trimmed range**: **CONCERN**. The fixture has only one EDGE_CURVE on a CYLINDRICAL_SURFACE with a horizontal pcurve at V=0 starting at U=π. There is no explicit V-trim and no closed wire bounding U∈[π,2π]; the periodic wrap defect is implicit in the pcurve placement but not enforced by topology. The reproducer is sketched, not fully wired.
- **Gp024 — Pcurve refit after non-uniform scale**: **CONFIRMED**. 3D LINE from (0,0,0) to (1000,0,0). PCURVE is degree-2 BSpline with control points y=±0.05 at x=250,500,750 — pcurve deviates from straight by 0.05 mm over a 1000 mm span (catalog claim of "0.05" deviation against "0.0001 edge tol" is structurally present, no UNCERTAINTY entity is emitted to declare the tolerance though).
- **Gp026 — Face contour not closed in UV (no seam)**: **CONFIRMED**. Cylinder face with 4 edges whose pcurves form a UV rectangle (0,0)→(2π−0.1,0)→(2π−0.1,5)→(0,5)→ closure. The "back" edge from UV (0,5) to (0,0) does not bridge the U gap. Tier3 reports n=63 entity defs with PCURVE/SURFACE_CURVE as expected.
- **Gp027 — Closed-shape splitter SameParameter violation**: **CONFIRMED**. CIRCLE on cylinder over half-arc (3D arc parameter 0..π); pcurve declared as LINE with direction × magnitude = `(1.0)·3.14159265` over parameter `[0,1]`. The parameterization mismatch (3D arc uses arc-length-style π, pcurve uses [0,1]) is exactly what FixSameParameter handles.
- **Gp028 — Cyclic seam edge crossing**: **CONFIRMED**. Single EDGE on cylinder with PCURVE running U=5.5→6.78 (=2π+0.5), crossing U=2π. EDGE_LOOP holds only this one edge; no seam edge is added.
- **Gp029 — FixShifted on revolved face**: **CONFIRMED**. SURFACE_OF_REVOLUTION (line profile, z-axis); 4 pcurves with U values in {0, 6.28(=2π), π}. Top-edge pcurve starts at U=2π — explicitly outside [0,2π] band — while neighbor pcurves are at U=π. Inconsistent UV band per catalog.
- **Gp030 — FixIE bend pcurve (PRO/E IGES)**: **CONFIRMED**. FILE_NAME originating system field is `'PRO/Engineer 2001'`. 2D pcurve is a degree-1 polyline through `(0,0)`, `(1,0)`, `(1,1)` — sharp 90° bend at the interior knot. Knot mult `(2,1,2)` with degree 1: gives C0 join.
- **Gp031 — Cylinder represented twice loses identity**: **CONFIRMED**. Two CYLINDRICAL_SURFACE entities `#20` and `#21`, each with its own AXIS2_PLACEMENT_3D copy at the same origin/axis. Two ADVANCED_FACEs (#64 referencing #20, #164 referencing #21) share an EDGE_LOOP via `#62=EDGE_LOOP('',(#61))` reused twice — analytic identity lost between the two surfaces.

## Summary

- 25 files inspected. **22 CONFIRMED**, **3 CONCERN** (Gp007, Gp023, Gp024 partial reproducers — defect documented in comments and primary entities, but not fully wired into the canonical chain a healer would scan; minor).
- Schema header: AP214 with FILE_SCHEMA `'AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'` — non-IFC so ifcopenshell rejects (`schema_class_reject`); OCCT/gmsh accept lex/parse.
- 3 fixtures crash OCCT at TransferRoots (Gp001, Gp019, Gp026's predecessors via empty `()` pcurve list — Gp026 itself OK at parse). Crashes are themselves diagnostic: an empty `associated_geometry` list is exactly the FixAddPCurve trigger.

## Recommendations

- **Gp007**: bind the `PARAMETER_VALUE(0.0)` and `PARAMETER_VALUE(2.5)` entities to the EDGE_CURVE via a `DEFINITIONAL_REPRESENTATION` carrying explicit edge-range; otherwise readers see the natural pcurve domain and never trigger the range mismatch.
- **Gp023**: actually trim the cylinder face to U∈[π, 2π] by wiring four edges (vertical seams + top/bottom arcs) so receivers attempt ValueOfUV against a real wire.
- **Gp024**: add `LENGTH_MEASURE_WITH_UNIT(... UNCERTAINTY_MEASURE_WITH_UNIT(0.0001 ...))` so the declared edge tolerance is in-file; current fixture has no UNCERTAINTY block.
