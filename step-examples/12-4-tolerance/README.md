# §12.4 — Tolerance & numerical-precision defects (N-prefix)

Numerical-precision and tolerance defects: precision/tolerance mismatch, `uncertainty_measure_with_unit` errors, geometric-set tolerance issues, snap-to-grid artefacts, near-zero magnitudes, and other floating-point-precision corner cases.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.4) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [N001](N001.stp) | Vertex `UNCERTAINTY_MEASURE_WITH_UNIT` larger than edge / face value (tolerance hierarchy violation) |
| [N002](N002.stp) | Wireframe gap-fix inflates tolerance instead of bridging the gap |
| [N003](N003.stp) | Same-domain face merge inflates shared-vertex tolerance to worst input |
| [N004](N004.stp) | Edge same-parameter flag asserted but 3D curve and pcurve disagree at sampled parameters (`SameParameter=.T.` lie) |
| [N005](N005.stp) | Splitting a closed periodic face leaves new edges with reversed pcurve vs 3D curve parameterisation |
| [N006](N006.stp) | Pcurve drifts out of sync with 3D-curve parameterisation (geometric flavour) |
| [N007](N007.stp) | Vertex tolerance bump factor hard-coded `1.000001 *` on disagreement |
| [N008](N008.stp) | Vertex tolerance inflation by repeated self-intersection healing cascades |
| [N009](N009.stp) | Vertex 3D point lies far from incident-edge curve endpoints (dispersion exceeds tolerance) |
| [N010](N010.stp) | `EDGE_CURVE` shorter than vertex tolerance (tiny edge covered by vertices, `distance_accuracy` exceeds edge length) |
| [N011](N011.stp) | Seam edge inserted inside an existing vertex tolerance ball produces zero-length edge |
| [N012](N012.stp) | Setting face tolerance to a tiny value then ShapeFix produces vertex/vertex intersections |
| [N013](N013.stp) | Boolean cascade vertex deviation (independently computed pairwise intersections) |
| [N014](N014.stp) | Spurious tiny `EDGE_CURVE` that should have collapsed: vertex separation below declared tolerance |
| [N015](N015.stp) | `xstep.cascade.unit M` meters setting inflates tolerance and corrupts geometry |
| [N016](N016.stp) | Edge tolerance 2-3 orders of magnitude > file tolerance (CATIA per-edge precision) |
| [N017](N017.stp) | `UNCERTAINTY_MEASURE_WITH_UNIT` populated with a fixed field-default value (untrustworthy) |
| [N018](N018.stp) | `GEOMETRIC_REPRESENTATION_CONTEXT` missing `GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT` leaf → fall back to read.precision |
| [N019](N019.stp) | `OFFSET_SURFACE` with sub-tolerance offset (fixed-tolerance importer hard-codes 1e-3) |
| [N020](N020.stp) | Coordinate-system origin offset: hard-coded BOARD_OFFSET 0.05mm in PCB→MCAD pipeline |
| [N021](N021.stp) | VRML/STEP origin convention mismatch within same producer |
| [N023](N023.stp) | `EDGE_CURVE` based on `LINE` displaced from true vertex position |
| [N024](N024.stp) | `EDGE_CURVE` 3D `LINE` stale relative to translated host `PLANE` (rebuild-edge case) |
| [N025](N025.stp) | Coincident-but-not-shared vertices/edges (cross-translator round-off) |
| [N026](N026.stp) | Cross-kernel topology rejection: source-valid, target-invalid by tolerance bookkeeping |
| [N027](N027.stp) | Small-mm `CYLINDRICAL_SURFACE` with target-unit mismatch (gmsh `OCCTargetUnit` silently ignored on `importShapesNativePointer` path) |
| [N028](N028.stp) | `GEOMETRIC_REPRESENTATION_CONTEXT` missing `LENGTH_UNIT` (only angle units present) → user-configured cascade.unit ignored |
| [N029](N029.stp) | Inch-units silent treatment as mm (25.4× scale error) |
| [N030](N030.stp) | Quarter `CYLINDRICAL_SURFACE` stored as `B_SPLINE_SURFACE_WITH_KNOTS` (canonical recognition tolerance budget) |
| [N031](N031.stp) | Surface discontinuities introduced by translation (G0/G1/G2 break at shared edges) |
| [N032](N032.stp) | Tolerance type entity coverage: AP242 tolerance entities dropped on import |
| [N033](N033.stp) | Tolerance value polymorphic encoding (`MeasureRepresentationItem` vs plain measure) |
| [N034](N034.stp) | `+/-` tolerance bounds inverted, equal, or wrong measure type |
| [N035](N035.stp) | Default tolerance precision: missing decimal-place qualifier |
| [N036](N036.stp) | Centroid validation breaks down when relative threshold goes below modeling tolerance |
| [N037](N037.stp) | Curve gaps between adjacent segments after format conversion (LOTAR exchange defect) |
| [N038](N038.stp) | Patrikalakis interval-solid violation: face-pair gap exceeds bound |
| [N039](N039.stp) | Healing pass over-eagerly inflates tolerances 1000× on sub-shapes that needed no fix (post-fix `UNCERTAINTY_MEASURE_WITH_UNIT` bloat) |
| [N040](N040.stp) | `Limit Tolerance` clamp re-exposes gaps that bloated tolerances were hiding (Salome) |
| [N041](N041.stp) | Manifold ε-validity contract: cumulative transform error inflates ε beyond input scale |
| [N042](N042.stp) | Self-intersecting wire from coarse-discretization bbox check (sample-count too small) |
| [N043](N043.stp) | Shape-to-shape distance reports nonzero gap for clearly intersecting parts |
| [N044](N044.stp) | Persistent IDs lost across editing/translation breaks PMI tolerance attachment |
| [N045](N045.stp) | Vertex tolerance under-checked: edge-internal intersection ignored |
| [N046](N046.stp) | Default tolerance projection wrong on non-default tolerance shapes (free CARTESIAN_POINT off PLANE within declared tolerance but beyond hard-coded internal tolerance) |
| [N047](N047.stp) | Linear and angular tolerance for same-surface face merging not user-specifiable |
| [N048](N048.stp) | Walk-line initial step unrelated to tolerance during surface intersection |
| [Tb001](Tb001.stp) | Sub-tolerance vertex gap that closes at 1e-3 but yawns open at 1e-7 |
| [Tb002](Tb002.stp) | Sub-tolerance vertex gap that closes at 1e-7 but inflates at 1e-3 |
| [Tb003](Tb003.stp) | Vertex-edge-face tolerance hierarchy holds in mm but inverts in m |
| [Tb004](Tb004.stp) | Vertex-edge-face hierarchy holds in mm but inverts when scaled to inches |
| [Tb005](Tb005.stp) | Face area sub-tolerance squared (`tol*tol` threshold defect) |
| [Tb006](Tb006.stp) | Edge length sub-tolerance squared in 2D pcurve length |
| [Tb007](Tb007.stp) | NURBS knot-difference quantum below tolerance: knot collapses or doesn't |
| [Tb008](Tb008.stp) | NURBS knot-difference quantum scaled by parametric range |
| [Tb009](Tb009.stp) | Self-intersection visible at full precision but rounded out at receiver tolerance |
| [Tb010](Tb010.stp) | Self-intersection that vanishes when round-tripped through float32 |
| [Tb011](Tb011.stp) | Periodic-surface seam matching requires period-relative tolerance |
| [Tb012](Tb012.stp) | Sphere seam matching across pole singularity |
| [Tb013](Tb013.stp) | Coordinate at 1e-300 tests as "near zero" only under denormalized math |
| [Tb014](Tb014.stp) | Sliver triangle whose smallest internal angle is at the hardcoded trigger |
| [Tb015](Tb015.stp) | Sliver edge length at sqrt(tol) — under squared comparison or linear? |
| [Tb016](Tb016.stp) | Tolerance budget exhausted by accumulation across long edge chain |
| [Tb017](Tb017.stp) | Two coincident faces at distance equal to declared tolerance |
| [Tb018](Tb018.stp) | UNCERTAINTY value of exactly zero — no fuzzy compare |
| [Tb019](Tb019.stp) | UNCERTAINTY value of `1.0E-30` — below any sane working precision |
| [Tb020](Tb020.stp) | UNCERTAINTY value of `1.0E+30` — astronomically loose |
| [Tb021](Tb021.stp) | Multiple UNCERTAINTY entries with conflicting values, no labels |
| [Tb022](Tb022.stp) | Tolerance declared in different units than coordinates |
