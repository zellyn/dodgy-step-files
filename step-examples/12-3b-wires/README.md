# §12.3b — Wire / loop / edge defects (Twi-prefix)

Wire and edge-loop defects: open wires where closed required, edge-loop ordering errors, vertex sharing issues, edge-curve direction confusion, oriented-edge `same_sense` defects, pcurve-shifted wires, and self-intersecting loops.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.3b) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Twi001](Twi001.stp) | Empty edge_list in EDGE_LOOP |
| [Twi002](Twi002.stp) | Single-edge EDGE_LOOP with non-coincident start/end vertex |
| [Twi003](Twi003.stp) | EDGE_LOOP edges not head-to-tail — adjacent edges' shared vertices don't coincide |
| [Twi004](Twi004.stp) | ORIENTED_EDGE wrapping another ORIENTED_EDGE |
| [Twi005](Twi005.stp) | ORIENTED_EDGE.edge_element references non-EDGE_CURVE |
| [Twi006](Twi006.stp) | ORIENTED_EDGE underlying EDGE_CURVE is null/missing reference |
| [Twi007](Twi007.stp) | Disordered edges in wire — listed out of traversal order but reorderable |
| [Twi008](Twi008.stp) | Wire ordering ambiguous between 2D and 3D ("miscible mode") on periodic surface |
| [Twi009](Twi009.stp) | Common vertex shared between two distinct wires (STEP-invalid) |
| [Twi010](Twi010.stp) | Figure-eight / pinched wire (wire revisits a vertex twice) |
| [Twi011](Twi011.stp) | Wire tail / hair (thin spike beyond max-angle/width threshold) |
| [Twi013](Twi013.stp) | Small / sliver / zero-length edges in wire (endpoints near-coincident) |
| [Twi017](Twi017.stp) | Closed 3D curve with two distinct VERTEX_POINTs (single-edge closed) |
| [Twi018](Twi018.stp) | Edge with start==end vertex but open curve (zero arc length) |
| [Twi019](Twi019.stp) | Closed edges need splitting at parametric break |
| [Twi020](Twi020.stp) | Missing seam edge on closed (periodic) surface |
| [Twi021](Twi021.stp) | Missing degenerate edge at surface singularity (cone apex / sphere pole) |
| [Twi022](Twi022.stp) | Seam edge with swapped or duplicated pcurves on a periodic face |
| [Twi024](Twi024.stp) | Wires forming inner loops outside outer loop (mis-classified hole) |
| [Twi027](Twi027.stp) | ConnectEdgesToWires fails on INTERNAL-only edges / non-determinism |
| [Twi028](Twi028.stp) | Scrambled (out-of-cyclic-order) `EDGE_LOOP` edge_list on `TOROIDAL_SURFACE` — wire-reorder triggers no replacement |
| [Twi029](Twi029.stp) | STEP writer drops entire wire if it contains a degenerate edge |
| [Twi030](Twi030.stp) | Degenerate edge re-encountered for multiple faces |
| [Twi031](Twi031.stp) | Degenerate edges duplicated at apex (Pro/E) |
| [Twi032](Twi032.stp) | Periodic face wraps a full period and needs splitting at the seam |
| [Twi033](Twi033.stp) | Wire contains two distinct edges that geometrically coincide |
| [Twi034](Twi034.stp) | `EDGE_LOOP` missing the closing edge (open near-closed wire treated as intentionally open) |
| [Twi035](Twi035.stp) | Sphere given by two meridians (special wire shape) |
| [Twi036](Twi036.stp) | Lacking edge: UV gap not closable by vertex tolerance |
| [Twi037](Twi037.stp) | Free bounds need joining (sewing) — adjacent faces don't share a single edge instance |
| [Twi038](Twi038.stp) | Scrambled `EDGE_LOOP` requiring only reorder: wire-only-reorder healing doesn't update the parent face |
| [Twi039](Twi039.stp) | Wire self-intersection check fails on mirrored-then-rotated arc footprints |
| [Twi040](Twi040.stp) | `EDGE_CURVE` `LINE` slightly off `CYLINDRICAL_SURFACE` (~`Precision::Confusion()` deviation): `Could not fix wire in surface` regression after OCCT version bump |
| [Twi041](Twi041.stp) | `ADVANCED_FACE` `FACE_BOUND` contains a `VERTEX_LOOP` wrapping a single internal `VERTEX_POINT` (infinite loop in outer-wire detection) |
| [Twi043](Twi043.stp) | Disjoined / nearly-coincident wire vertices need merge or split decision |
| [Twi044](Twi044.stp) | Internal `FACE_BOUND` hole-wire with sub-tolerance enclosed area (degenerate tiny inner wire) |
| [Twi045](Twi045.stp) | Small-area wire removal on a reversed or located face mis-orients output wires |
| [Twi046](Twi046.stp) | Edge 3D curve evaluation does not match its declared end vertices |
| [Twi047](Twi047.stp) | EDGE_CURVE has only a pcurve, no 3D space curve (orphan EDGE_CURVE missing PCURVE / SURFACE_CURVE wrapping) |
| [Twi048](Twi048.stp) | Vertex tolerance smaller than the edge endpoint discrepancy it must absorb |
| [Twi049](Twi049.stp) | Wire on a face self-intersects in the host surface's parameter space |
| [Twi050](Twi050.stp) | Two distinct wires share a VERTEX_POINT instance that needs to be split |
| [Twi051](Twi051.stp) | Wire-level healing pipeline must order reorder/connect/lacking/closed fixes (e.g., inner FACE_BOUND triangle with near-coincident vertices and EDGE_LOOP ORIENTED_EDGEs out of head-to-tail order) |
| [Twi052](Twi052.stp) | Wire whose edges accumulate several pcurve / 3D-curve defects at once |
| [Twi053](Twi053.stp) | EDGE_LOOP wire is open: closing edge entirely missing (last vertex doesn't match first vertex; large 3D gap between dangling endpoints) |
| [Twi054](Twi054.stp) | EDGE_LOOP wire has a notch: short detour edge between two near-collinear long edges (e.g., 5-edge rectangle wire with one VERTEX_POINT offset ~1e-3 forming a sub-mm triangular bump) |
| [Twi055](Twi055.stp) | Wire-segment edge claims an out-of-grid patch index on a composite surface (or two ADVANCED_FACEs aliasing the same FACE_OUTER_BOUND on two different host PLANEs) |
| [Twi056](Twi056.stp) | Wire vertices that should share a coordinate differ by sub-precision amounts |
| [Twi057](Twi057.stp) | Two edges of one face are confused along their full length (strip pair) |
| [Twi058](Twi058.stp) | Two edges form a pin: meet at a vertex with near-zero opening angle |
| [Twi059](Twi059.stp) | Vertex 3D point and edge 3D-curve endpoint disagree beyond tolerance |
| [Twi060](Twi060.stp) | Vertex 3D point and edge pcurve endpoint disagree beyond tolerance |
| [Twi061](Twi061.stp) | Vertex tolerance check returns required inflation amount (rectangular wire with VERTEX_POINT offset from underlying LINE endpoint; UNCERTAINTY_MEASURE_WITH_UNIT too small to absorb the gap) |
| [Twi062](Twi062.stp) | 3D curve and pcurve traverse the same edge in opposite parameter senses |
| [Twi063](Twi063.stp) | Two edges describe overlapping segments of the same curve |
| [Twi064](Twi064.stp) | Wire-analysis pipeline collects all sub-check status flags without short-circuit (e.g., inner FACE_BOUND triangle with near-coincident VERTEX_POINTs and EDGE_LOOP ORIENTED_EDGEs out of head-to-tail order) |
| [Twi065](Twi065.stp) | Wire edge-curves analysis: 3D/2D consistency in one report (EDGE_LOOP with reversed pcurve direction, vertex/3D LINE start mismatch, junction gap, and pcurve/3D length parameter mismatch) |
| [Twi066](Twi066.stp) | Closure check separately reports 3D and 2D failures (e.g., EDGE_LOOP with missing closing edge AND last edge's 3D LINE end disagreeing with declared end VERTEX_POINT) |
| [Twi067](Twi067.stp) | Lacking edge: 2D gap not absorbable by vertex tolerance |
| [Twi068](Twi068.stp) | Wire 3D-gap analysis must enumerate all gaps (EDGE_LOOP with multiple junctions where consecutive ORIENTED_EDGEs have mismatched VERTEX_POINTs, e.g., 0.05-0.07 mm gaps) |
| [Twi069](Twi069.stp) | Wire 2D-gap analysis must enumerate all pcurve gaps |
| [Twi070](Twi070.stp) | Curve gap within a single edge: 3D curve and pcurve drift mid-edge |
| [Twi071](Twi071.stp) | Seam edge has its two pcurves swapped |
| [Twi072](Twi072.stp) | Per-junction 3D gap query returns localized fault (EDGE_LOOP with missing closing edge; last ORIENTED_EDGE's end VERTEX_POINT also disagrees with its 3D LINE endpoint) |
| [Twi073](Twi073.stp) | Per-junction 2D pcurve gap query |
| [Twi074](Twi074.stp) | Notch detection between a single pair of EDGE_CURVEs (e.g., 5-edge rectangle wire with one VERTEX_POINT offset ~1e-3 forming a sub-mm triangular bump) |
| [Twi075](Twi075.stp) | Connect-shape diagnostic: how does a foreign ORIENTED_EDGE attach to an EDGE_LOOP wire (e.g., open 3-edge wire plus a free edge near its tail with a sub-mm gap)? |
| [Twi076](Twi076.stp) | EDGE_LOOP self-intersects (figure-eight): edges crisscross inside the wire (e.g., diagonal-like edges between rectangle corners) |
| [Twi077](Twi077.stp) | Wire tail / sliver: two adjacent EDGE_CURVEs form a sharp 180° fold over sub-tolerance width (one edge nearly retraces the other in opposite direction) |
| [Twi078](Twi078.stp) | Wire-order analysis: reorder unordered edges (no reversal needed) |
| [Twi079](Twi079.stp) | Internal hole wire whose enclosed area is below threshold |
| [Twi080](Twi080.stp) | Wire splitting must propagate from underlying edge/curve splits |
| [Twi081](Twi081.stp) | Edge has multiple distinct 3D curves attached |
| [Twi082](Twi082.stp) | Edge `same_range` flag claims parametric agreement that does not hold |
| [Twi083](Twi083.stp) | EDGE_CURVE flagged degenerate but its 3D LINE has positive length (non-zero distance between distinct VERTEX_POINTs) |
| [Twi084](Twi084.stp) | Closed-curve edge has different start and end vertex points |
| [Twi085](Twi085.stp) | Edge endpoint vertex's 3D point disagrees with curve evaluation at the boundary parameter |
| [Twi086](Twi086.stp) | Edge geometry is a line through two coincident points (zero-length line edge) |
| [Twi087](Twi087.stp) | Wire is non-manifold: a vertex is incident to >2 edges of the wire |
| [Twi088](Twi088.stp) | Edge in topology has no 3D curve attached |
| [Twi089](Twi089.stp) | Two collinear edges meeting at a degree-2 vertex should be fused into one edge |
| [Twi090](Twi090.stp) | Cached EDGE_LOOP closed-flag not refreshed after one ORIENTED_EDGE replaced by two collinear halves at a midpoint vertex |
| [Twi091](Twi091.stp) | Inner wire on closed surface lacks natural bound: face read with no boundary |
| [Twi092](Twi092.stp) | Wire with degenerated edge dropped silently on export |
| [Twi093](Twi093.stp) | Synthesised seam edge is inserted through existing wire path on cylinder |
| [Twi094](Twi094.stp) | Wire endpoint first/last edge skipped during wire build (open EDGE_LOOP missing first ORIENTED_EDGE; orphan VERTEX_POINT defined but never referenced) |
| [Twi095](Twi095.stp) | Touching wires on a face form a tangential contact at single vertex |
| [Twi096](Twi096.stp) | Wire with internal cross-loop translates incorrectly |
| [Twi097](Twi097.stp) | Edge-projection-aux range computation loses precision on periodic curves |
| [Twi098](Twi098.stp) | `FixTails` removes wire tail edges incorrectly (EDGE_LOOP with intentional short feature edges, e.g., a chamfer edge plus a disconnected free-floating short edge) |
