# §12.3c — Face / sewing / free-bound defects (Tfa-prefix)

Face-level topology defects: missing/wrong face bounds, free-bound usage errors, face-surface mismatches, sewing tolerance failures, advanced-face/oriented-face wrapper issues, and inconsistent face_outer_bound vs face_bound usage.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.3c) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Hea001](Hea001.stp) | Top-level shape-healing pipeline must converge over multi-defect GEOMETRIC_SET (mixed defective ADVANCED_FACE, OPEN_SHELL, free EDGE_LOOP wire) |
| [Hea002](Hea002.stp) | Solid-level healing on MANIFOLD_SOLID_BREP wrapping an OPEN_SHELL (instead of CLOSED_SHELL): iterate shell fixes and re-evaluate closure |
| [Hea003](Hea003.stp) | Free-bound properties pipeline computes area/perimeter/notches together |
| [Hea004](Hea004.stp) | Free-bound contour analysis filters EDGE_LOOPs with sub-precision wiggle vertices (many short sub-segments, deviations below tolerance) |
| [Hea005](Hea005.stp) | Triangular notch detour detected on a free-bound EDGE_LOOP contour (sub-mm vertices break a straight side into 3+ segments) |
| [Hea006](Hea006.stp) | Shape-contents inventory: subshape histogram (e.g., GEOMETRIC_SET counting one ADVANCED_FACE plus one free EDGE_LOOP wire) |
| [Hea007](Hea007.stp) | Transferring parameter values between 3D curve and pcurve when EDGE_CURVE has B_SPLINE_CURVE_WITH_KNOTS in 3D and a LINE pcurve with non-affine reparam |
| [Hea008](Hea008.stp) | Transfer parameters using projection (not affine remapping) |
| [Hea009](Hea009.stp) | Convert curves and surfaces of a shape (e.g., FACE_OUTER_BOUND on a degree-2 B_SPLINE_CURVE_WITH_KNOTS) to Bezier representation |
| [Hea010](Hea010.stp) | Shape-divide pipeline propagates B_SPLINE_SURFACE C0 knot-line splits (e.g., U-knot multiplicity = degree) to topology |
| [Hea011](Hea011.stp) | Shape-healing driver runs a runtime-configured operator sequence over a GEOMETRIC_SET with sub-tolerance EDGE_CURVE, OPEN_SHELL, and same-parameter violation |
| [Hea012](Hea012.stp) | Shape-process operator contract: pluggable healing step over face with scrambled inner FACE_BOUND triangle (near-coincident vertices, edges out of order) |
| [Hea013](Hea013.stp) | User-defined shape-process operator (UOperator) on face with scrambled inner FACE_BOUND triangle (near-coincident vertices, edges out of order) |
| [Hea014](Hea014.stp) | Compound rebuild misses location chain when child SHAPE_REPRESENTATION via REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION at non-identity placement |
| [Hea015](Hea015.stp) | Shape healing regression: shared EDGE_CURVE between two ADVANCED_FACEs on same PLANE has duplicate PCURVE_S1_AND_S2 entries (identical UV start and direction) |
| [Tfa001](Tfa001.stp) | FACE_SURFACE.face_geometry is null |
| [Tfa002](Tfa002.stp) | Unbound ADVANCED_FACE (no FACE_OUTER_BOUND, no FACE_BOUND) |
| [Tfa003](Tfa003.stp) | FaceOuterBound translation failed (face incomplete without outer wire) |
| [Tfa004](Tfa004.stp) | Missing natural bound on sphere / torus face |
| [Tfa005](Tfa005.stp) | Periodic face given by single belt wire (degenerate pole case) |
| [Tfa006](Tfa006.stp) | Spot face: face collapsed to a point |
| [Tfa007](Tfa007.stp) | Strip face: face one-dimensional within tolerance |
| [Tfa008](Tfa008.stp) | Pin / sliver face |
| [Tfa010](Tfa010.stp) | Splitting vertex within face (vertex of one wire on edge of another) |
| [Tfa011](Tfa011.stp) | `ADVANCED_FACE` with multiple `FACE_OUTER_BOUND` entries (face needs split) |
| [Tfa012](Tfa012.stp) | Face area zero / negative after fixshape |
| [Tfa013](Tfa013.stp) | Face area exceeds limit (needs split) |
| [Tfa014](Tfa014.stp) | Small `ADVANCED_FACE` below area threshold (FixFaceSize) |
| [Tfa015](Tfa015.stp) | DropSmallSolids / debris solids from booleans |
| [Tfa016](Tfa016.stp) | Adjacent faces share same supporting surface (redundant internal edge) |
| [Tfa017](Tfa017.stp) | Same-domain face merge inflates vertex tolerance on the result |
| [Tfa018](Tfa018.stp) | Same-domain face merge across periodic seam: shared `EDGE_CURVE` reused with `.T.`/`.F.` on both halves (missed-seam reconstruction) |
| [Tfa019](Tfa019.stp) | Adjacent `ADVANCED_FACE`s with distinct `VERTEX_POINT`/`EDGE_CURVE` for the same shared boundary (FaceConnect: vertices not shared) |
| [Tfa020](Tfa020.stp) | Sewing — free bounds on closed shell |
| [Tfa022](Tfa022.stp) | Almost-closed `EDGE_LOOP` with sub-tolerance gap and wrong Closed flag (ConnectEdgesToWires) |
| [Tfa023](Tfa023.stp) | STEP file delivers disjoint faces with no shell wrapping (sewing required) |
| [Tfa024](Tfa024.stp) | Glue Faces (coincident faces) |
| [Tfa025](Tfa025.stp) | Glue Edges: duplicate `EDGE_CURVE` instances over duplicated `LINE` / `VERTEX_POINT` entities (coincident edges) |
| [Tfa026](Tfa026.stp) | OFFSET_SURFACE used (out of AP214 scope) |
| [Tfa028](Tfa028.stp) | Full-revolution `CYLINDRICAL_SURFACE` `ADVANCED_FACE` with single seam `EDGE_CURVE` used twice (split_angle: angular span exceeds cap) |
| [Tfa030](Tfa030.stp) | `ADVANCED_FACE` `PLANE` `AXIS2_PLACEMENT_3D` ignored relative to raw-global `CARTESIAN_POINT` bounds (subshape replacement helper drops local placement) |
| [Tfa031](Tfa031.stp) | Locations attached to sub-shapes — instance flattening |
| [Tfa032](Tfa032.stp) | Same-domain face merge introduces overlap / self-intersection on boolean result |
| [Tfa034](Tfa034.stp) | Face orientation flag inconsistent with shell normal (FixFaceOrientation) |
| [Tfa036](Tfa036.stp) | Face on composite surface with boundary crossing patch seams |
| [Tfa037](Tfa037.stp) | Face-level healing pipeline must orchestrate wire/orientation/seam/area sub-fixes (e.g., ADVANCED_FACE with outer rectangle plus a defective inner FACE_INNER_BOUND triangle) |
| [Tfa038](Tfa038.stp) | Face on closed surface lacks outer boundary |
| [Tfa039](Tfa039.stp) | Face has multiple wires that intersect in UV |
| [Tfa040](Tfa040.stp) | Small-face dispatcher orchestrates spot/strip/pin classification (e.g., sub-tolerance ADVANCED_FACE outer loop ~0.001x0.001 mm) |
| [Tfa041](Tfa041.stp) | Spot face: face collapsed to a near-point |
| [Tfa042](Tfa042.stp) | Strip face: face whose width is below tolerance |
| [Tfa043](Tfa043.stp) | Single-face dispatcher: classify-and-heal small face |
| [Tfa044](Tfa044.stp) | Pin face: long thin protrusion at a vertex |
| [Tfa045](Tfa045.stp) | Multiple inner FACE_BOUND wires of an ADVANCED_FACE touch tangentially at a single point (kissing wires sharing a VERTEX_POINT) |
| [Tfa046](Tfa046.stp) | Spot-face diagnostic emits Pnt-located warning before healing (sub-tolerance ADVANCED_FACE outer EDGE_LOOP ~0.001x0.001 mm) |
| [Tfa047](Tfa047.stp) | Single-strip ADVANCED_FACE detection with U/V direction classification (long thin face, e.g., 100 x 0.001 mm rectangle outer EDGE_LOOP) |
| [Tfa048](Tfa048.stp) | Strip face flagged using caller-supplied tolerance |
| [Tfa049](Tfa049.stp) | Pin diagnostic: classify smooth vs sharp vs stretched pin (long thin triangular ADVANCED_FACE outer EDGE_LOOP, e.g., 10mm long with sub-mm width tip) |
| [Tfa050](Tfa050.stp) | Pin face (long thin triangular ADVANCED_FACE) produces edge-correspondence map for healing |
| [Tfa051](Tfa051.stp) | Face needs splitting (knot insertion / sub-faces) for downstream tools |
| [Tfa052](Tfa052.stp) | ADVANCED_FACE split because surface area exceeds threshold (e.g., a 100x100 mm square face must be divided into bounded-area sub-faces) |
| [Tfa053](Tfa053.stp) | Composite-surface patches do not connect on shared boundary |
| [Tfa054](Tfa054.stp) | Face has no underlying surface |
| [Tfa055](Tfa055.stp) | Two distinct wires of one face cross each other in UV |
| [Tfa056](Tfa056.stp) | Face has a redundant wire (wire fully inside another wire of same face) |
| [Tfa057](Tfa057.stp) | Face wire's orientation contradicts the outer/inner role |
| [Tfa058](Tfa058.stp) | Plane-typed face whose vertices are non-coplanar |
| [Tfa059](Tfa059.stp) | Pcurve projection failed: 3D edge curve cannot be lifted onto the host surface |
| [Tfa060](Tfa060.stp) | Shell parametric coverage exceeds host surface bounds |
| [Tfa061](Tfa061.stp) | Sewing of thin faces takes excessive time during seam-edge creation |
| [Tfa062](Tfa062.stp) | Face crash during fix on invalid face — null inner wire |
| [Tfa063](Tfa063.stp) | Stack overflow on `RemoveSmallFaces` due to unbounded recursion |
| [Tfa064](Tfa064.stp) | Missing-seam reconstruction fails on ADVANCED_FACE on CYLINDRICAL_SURFACE whose wire contains a partial seam line plus horizontal CIRCLE arcs |
| [Tfa065](Tfa065.stp) | Healed face uses inflated tolerance instead of original (small gap between adjacent EDGE_LOOP vertices, e.g., 1e-3 mm between V3 and next-edge start) |
| [Tfa066](Tfa066.stp) | Pipe-like face with seam edge wrongly removed as "small" |
| [Tfa067](Tfa067.stp) | Top face dropped after STEP import (CLOSED_SHELL cube whose top FACE_OUTER_BOUND edge has 3D LINE vs B_SPLINE_CURVE_WITH_KNOTS pcurve mismatch) |
