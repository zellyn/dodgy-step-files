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
| [Twi099](Twi099.stp) | `EDGE_CURVE` whose start and end vertex point at the same `VERTEX_POINT` |
| [Twi100](Twi100.stp) | `COMPOSITE_CURVE_ON_SURFACE` LoadONBrep stub (BRL-CAD step-g) |
| [Twi101](Twi101.stp) | `POLYLINE` basis curve LoadONBrep stub (BRL-CAD step-g) |
| [Twi102](Twi102.stp) | ShapeFix_Wire.FixDegenerated modulo-index wraparound at wire end |
| [Twi103](Twi103.stp) | ShapeFix_Wire.FixSelfIntersectingEdge 30-iteration convergence silently exits |
| [Twi104](Twi104.stp) | ShapeAnalysis_Wire.CheckTail misclassifies degenerate orientation |
| [Twi105](Twi105.stp) | ShapeAnalysis_Wire.CheckIntersectingEdges seam-gap tolerance filter miss |
| [Twi106](Twi106.stp) | ShapeFix_Wire.FixIntersectingEdges accumulation cascade without upper bound |
| [Twi107](Twi107.stp) | FixReorder Mode-Cascade |
| [Twi108](Twi108.stp) | FixGaps3d 3D-Gap Repair |
| [Twi109](Twi109.stp) | FixShifted Period-Shift on Closed Surface |
| [Twi110](Twi110.stp) | CheckEdgeCurves 3D-vs-2D Coherence |
| [Twi111](Twi111.stp) | FixDummySeam Dummy-Seam Removal |
| [Twi112](Twi112.stp) | ShapeFix_Wire.FixGaps2d 2D-gap repair on cylindrical surface |
| [Twi113](Twi113.stp) | ShapeAnalysis_Wire.CheckOuterBound outer-bound mis-identification |
| [Twi114](Twi114.stp) | ShapeFix_Wire.FixTails tail-elimination |
| [Twi115](Twi115.stp) | ShapeAnalysis_Wire.CheckGap3d threshold-comparison edge |
| [Twi116](Twi116.stp) | ShapeFix_Wire.FixConnected vertex-sharing mismatch |
| [Twi117](Twi117.stp) | ShapeFix_Wire.FixNotchedEdges singular-derivative |
| [Twi118](Twi118.stp) | ShapeAnalysis_Wire.CheckLacking lacking-edge tangency |
| [Twi119](Twi119.stp) | ShapeFix_Wire.FixSmall threshold-on-tolerance |
| [Twi120](Twi120.stp) | ShapeAnalysis_Wire.CheckShapeConnect 4-way orientation encoding |
| [Twi121](Twi121.stp) | ShapeFix_Wire.FixSeam closed-surface seam reset |
| [Twi122](Twi122.stp) | ShapeFix_Wire.FixTails wire-tail asymmetry |
| [Twi123](Twi123.stp) | ShapeAnalysis_Wire.CheckGap2d tolerance-equality misclassification |
| [Twi124](Twi124.stp) | ShapeFix_Wire.FixIntersectingEdges 2.0000001 magic-constant |
| [Twi125](Twi125.stp) | ShapeAnalysis_Wire.CheckSelfIntersection bounding-box pruning |
| [Twi126](Twi126.stp) | ShapeFix_Wire.FixClosed linear submethod cascade |
| [Twi127](Twi127.stp) | ShapeFix_Wire.FixReorder UV-disjoint regions |
| [Twi128](Twi128.stp) | ShapeAnalysis_Wire.CheckTail tail-edge orientation flip |
| [Twi129](Twi129.stp) | ShapeFix_Wire.FixSelfIntersectingEdge inflection-self-touch |
| [Twi130](Twi130.stp) | ShapeAnalysis_Wire.CheckIntersectingEdges adjacency exemption |
| [Twi131](Twi131.stp) | ShapeFix_Wire.FixLacking degenerate-edge insertion |
| [Twi132](Twi132.stp) | ShapeFix_Wire.FixDummySeam non-periodic-surface |
| [Twi133](Twi133.stp) | ShapeAnalysis_Wire.CheckCurveGap bspline endpoint precision |
| [Twi134](Twi134.stp) | ShapeFix_Wire.FixShifted non-2π shift |
| [Twi135](Twi135.stp) | ShapeAnalysis_Wire.CheckGap2d trimmed-pcurve gap |
| [Twi136](Twi136.stp) | ShapeFix_Wire.FixConnected vertex-replacement chain |
| [Twi137](Twi137.stp) | ShapeFix_Wire.FixIntersectingEdges 2D-only intersection |
| [Twi138](Twi138.stp) | ShapeAnalysis_Wire.CheckSmall edge-length comparison |
| [Twi139](Twi139.stp) | ShapeFix_Wire.FixReorder seed-edge choice |
| [Twi140](Twi140.stp) | ShapeAnalysis_Wire.CheckTail B-spline tail |
| [Twi141](Twi141.stp) | ShapeFix_Wire.FixSelfIntersectingEdge close-loop iteration |
| [Twi142](Twi142.stp) | ShapeFix_Wire.FixDegenerated insertion at index 0 |
| [Twi143](Twi143.stp) | ShapeAnalysis_Wire.CheckIntersectingEdges parallel edges |
| [Twi144](Twi144.stp) | ShapeFix_Wire.FixSeam non-cylindrical periodic surface |
| [Twi145](Twi145.stp) | ShapeAnalysis_Wire.CheckGap3d 3D-only with valid 2D |
| [Twi146](Twi146.stp) | ShapeFix_Wire.FixLacking wrap-around on closed surface |
| [Twi147](Twi147.stp) | ShapeFix_Wire.FixGaps3d edge-replacement |
| [Twi148](Twi148.stp) | ShapeAnalysis_Wire.CheckClosed degenerate-tolerance |
| [Twi149](Twi149.stp) | ShapeFix_Wire.FixDummySeam non-orientable surface |
| [Twi150](Twi150.stp) | ShapeAnalysis_Wire.CheckLacking parallel-tangent |
| [Twi151](Twi151.stp) | ShapeFix_Wire.FixSelfIntersectingEdge cusp-cusp |
| [Twi152](Twi152.stp) | ShapeFix_Wire.FixIntersectingEdges line-segment-vs-circle-arc |
| [Twi153](Twi153.stp) | ShapeAnalysis_Wire.CheckIntersectingEdges B-spline self-intersection |
| [Twi154](Twi154.stp) | ShapeFix_Wire.FixSeam edge-direction reversed |
| [Twi155](Twi155.stp) | ShapeAnalysis_Wire.CheckGap3d zero-length-edge |
| [Twi156](Twi156.stp) | ShapeFix_Wire.FixReorder duplicate-edge |
| [Twi157](Twi157.stp) | ShapeAnalysis_Wire.CheckSelfIntersection figure-8 wire |
| [Twi158](Twi158.stp) | ShapeFix_Wire.FixGaps2d 2D-gap on periodic surface |
| [Twi159](Twi159.stp) | ShapeAnalysis_Wire.CheckOrder wire-completely-reversed |
| [Twi160](Twi160.stp) | ShapeFix_Wire.FixLacking degenerate-vertex-gap |
| [Twi161](Twi161.stp) | ShapeAnalysis_Wire.CheckGap2d on B-spline pcurve |
| [Twi162](Twi162.stp) | ShapeFix_Wire.FixIntersectingEdges 3-edge-mutual-intersection |
| [Twi163](Twi163.stp) | ShapeAnalysis_Wire.CheckIntersectingEdges trimmed-edges-overlap-base-curve |
| [Twi164](Twi164.stp) | ShapeFix_Wire.FixReorder algorithm-cycle |
| [Twi165](Twi165.stp) | ShapeAnalysis_Wire.CheckTail B-spline subdivided |
| [Twi166](Twi166.stp) | ShapeFix_Wire.FixSelfIntersectingEdge near-grazing |
| [Twi167](Twi167.stp) | ShapeFix_Wire.FixIntersectingEdges loop-collapse |
| [Twi168](Twi168.stp) | ShapeAnalysis_Wire.CheckShapeConnect different-vertex-counts |
| [Twi169](Twi169.stp) | ShapeFix_Wire.FixDegenerated insert-between-degenerate |
| [Twi170](Twi170.stp) | ShapeAnalysis_Wire.CheckGap3d 3D-vs-pcurve-disagreement |
| [Twi171](Twi171.stp) | ShapeFix_Wire.FixReorder reverse-then-forward |
| [Twi172](Twi172.stp) | ShapeFix_Wire.FixSelfIntersectingEdge cusp-edge |
| [Twi173](Twi173.stp) | ShapeAnalysis_Wire.CheckLacking endpoint-degenerate |
| [Twi174](Twi174.stp) | ShapeFix_Wire.FixDummySeam non-cylindrical |
| [Twi175](Twi175.stp) | ShapeAnalysis_Wire.CheckTail negative-parameter |
| [Twi176](Twi176.stp) | ShapeFix_Wire.FixIntersectingEdges concurrent-modification |
| [Twi177](Twi177.stp) | ShapeAnalysis_Wire.CheckOuterBound nested-faces |
| [Twi178](Twi178.stp) | ShapeFix_Wire.FixSelfIntersection convergence-oscillation |
| [Twi179](Twi179.stp) | ShapeAnalysis_Wire.CheckGap2d on-trimmed-pcurve |
| [Twi180](Twi180.stp) | ShapeFix_Wire.FixGaps3d 4-edge-gap-chain |
| [Twi181](Twi181.stp) | ShapeAnalysis_Wire.CheckGap3d B-spline-vs-LINE |
| [Twi182](Twi182.stp) | ShapeFix_Wire.FixTails very-small-tail |
| [Twi183](Twi183.stp) | ShapeAnalysis_Wire.CheckSeam non-cylindrical-seam |
| [Twi184](Twi184.stp) | ShapeFix_Wire.FixConnected zero-length-edge-between |
| [Twi185](Twi185.stp) | ShapeAnalysis_Wire.CheckSelfIntersection coincident-curves |
| [Twi186](Twi186.stp) | ShapeFix_Wire.FixIntersectingEdges parametric-overlap |
| [Twi187](Twi187.stp) | ShapeFix_Wire.FixLacking insertion-cascade |
| [Twi188](Twi188.stp) | ShapeAnalysis_Wire.CheckSelfIntersectingEdge B-spline-with-loop |
| [Twi189](Twi189.stp) | ShapeFix_Wire.FixGaps3d directional-extension |
| [Twi190](Twi190.stp) | ShapeAnalysis_Wire.CheckShapeConnect three-edge-fan |
| [Twi191](Twi191.stp) | ShapeFix_Wire.FixIntersectingEdges parameter-monotonicity |
| [Twi192](Twi192.stp) | FixGaps2d 2D-only-bridge |
| [Twi193](Twi193.stp) | CheckOrder index-mode-clash |
| [Twi194](Twi194.stp) | FixIntersectingEdges shared-vertex-misclassification |
| [Twi195](Twi195.stp) | CheckClosed open-tail-vs-spur |
| [Twi196](Twi196.stp) | FixDegenerated zero-length-after-trim |
| [Twi197](Twi197.stp) | ShapeFix_Wire.FixTails iteration-with-removal |
| [Twi198](Twi198.stp) | ShapeAnalysis_Wire.CheckSelfIntersection coincident-line-segments |
| [Twi199](Twi199.stp) | ShapeFix_Wire.FixGaps3d gap-larger-than-Confusion-but-less-than-vertex-tolerance |
| [Twi200](Twi200.stp) | ShapeAnalysis_Wire.CheckOrder cycle-vs-acyclic |
| [Twi201](Twi201.stp) | ShapeFix_Wire.FixSeam mismatched-pcurve-direction |
| [Twi202](Twi202.stp) | ShapeFix_Wire.FixReorder duplicate-vertex-causes-cycle |
| [Twi203](Twi203.stp) | ShapeAnalysis_Wire.CheckTail B-spline tail-detection |
| [Twi204](Twi204.stp) | ShapeFix_Wire.FixIntersectingEdges 3-edges-at-vertex |
| [Twi205](Twi205.stp) | ShapeAnalysis_Wire.CheckIntersectingEdges B-spline-tangent-touch |
| [Twi206](Twi206.stp) | ShapeFix_Wire.FixSelfIntersectingEdge cusp-at-vertex |
| [Twi207](Twi207.stp) | ShapeFix_Wire.FixGaps2d gap-at-knot-discontinuity |
| [Twi208](Twi208.stp) | ShapeAnalysis_Wire.CheckSelfIntersection coincident-with-tangency |
| [Twi209](Twi209.stp) | ShapeFix_Wire.FixReorder mixed-curve-types-vertex-merge |
| [Twi210](Twi210.stp) | ShapeAnalysis_Wire.CheckClosed near-closed-with-perpendicular-distance |
| [Twi211](Twi211.stp) | ShapeFix_Wire.FixLacking surface-edge-direction-mismatch |
| [Twi212](Twi212.stp) | ShapeFix_Wire.FixIntersectingEdges trim-aware-intersection |
| [Twi213](Twi213.stp) | ShapeAnalysis_Wire.CheckGap3d using-pcurve-distance |
| [Twi214](Twi214.stp) | ShapeFix_Wire.FixSelfIntersection figure-eight-pattern |
| [Twi215](Twi215.stp) | ShapeAnalysis_Wire.CheckTail multi-tail-detection |
| [Twi216](Twi216.stp) | ShapeFix_Wire.FixDegenerated removal-cascade |
| [Twi217](Twi217.stp) | ShapeFix_Wire.FixSeam pcurve-direction-not-matching-3d |
| [Twi218](Twi218.stp) | ShapeAnalysis_Wire.CheckShapeConnect with-degenerate-vertex |
| [Twi219](Twi219.stp) | ShapeFix_Wire.FixIntersectingEdges 2D-and-3D-disagree |
| [Twi220](Twi220.stp) | ShapeAnalysis_Wire.CheckLacking degenerate-fill-in |
| [Twi221](Twi221.stp) | ShapeFix_Wire.FixDummySeam non-canonical-seam-position |
| [Twi222](Twi222.stp) | ShapeFix_Wire.FixTails consecutive-removal |
| [Twi223](Twi223.stp) | ShapeAnalysis_Wire.CheckOrder mode-3D-vs-2D-disagree |
| [Twi224](Twi224.stp) | ShapeFix_Wire.FixGaps3d gap-bigger-than-edge |
| [Twi225](Twi225.stp) | ShapeAnalysis_Wire.CheckSelfIntersection branch-point |
| [Twi226](Twi226.stp) | ShapeFix_Wire.FixIntersectingEdges with-edge-on-surface-boundary |
| [Twi227](Twi227.stp) | ShapeFix_Wire.FixGaps2d on-bspline-surface |
| [Twi228](Twi228.stp) | ShapeAnalysis_Wire.CheckGap3d with-very-large-coordinates |
| [Twi229](Twi229.stp) | ShapeFix_Wire.FixReorder all-edges-degenerate |
| [Twi230](Twi230.stp) | ShapeAnalysis_Wire.CheckIntersectingEdges B-spline-edge-with-many-knots |
| [Twi231](Twi231.stp) | ShapeFix_Wire.FixLacking with-existing-wire-degenerate-vertex |
| [Twi232](Twi232.stp) | ShapeFix_Wire.FixSelfIntersection two-edges-two-intersections |
| [Twi233](Twi233.stp) | ShapeAnalysis_Wire.CheckOuterBound winding-number-zero |
| [Twi234](Twi234.stp) | ShapeFix_Wire.FixDegenerated zero-vertex |
| [Twi235](Twi235.stp) | ShapeAnalysis_Wire.CheckTail B-spline-tangent-mismatch |
| [Twi236](Twi236.stp) | ShapeFix_Wire.FixGaps3d bridge-creates-degeneracy |
| [Twi237](Twi237.stp) | ShapeFix_Wire.FixSmall edge-coalescing tolerance |
| [Twi238](Twi238.stp) | ShapeFix_Wire.FixConnected disconnected-endpoints vertex-merge-fails |
| [Twi239](Twi239.stp) | ShapeFix_Wire.FixClosed open-wire-closure-degenerate |
| [Twi240](Twi240.stp) | ShapeFix_Wire.FixShifted seam-vertex-position-mismatch |
| [Twi241](Twi241.stp) | ShapeFix_Wire.FixNotchedEdges notch-at-multi-edge-junction |
| [Twi242](Twi242.stp) | ShapeAnalysis_Wire.CheckOrder |
| [Twi243](Twi243.stp) | ShapeAnalysis_Wire.CheckConnected |
| [Twi244](Twi244.stp) | ShapeAnalysis_Wire.CheckSmall |
| [Twi245](Twi245.stp) | ShapeAnalysis_Wire closure gap |
| [Twi246](Twi246.stp) | ShapeAnalysis_Wire.CheckSameParameter |
| [Twi247](Twi247.stp) | BRepLib::SameParameter exception silent skip |
| [Twi248](Twi248.stp) | BRepLib::SameParameter null 3D curve dereference |
| [Twi249](Twi249.stp) | ShapeFix_IntersectionTool CutEdge range too small |
| [Twi250](Twi250.stp) | ShapeFix_IntersectionTool FindVertAndSplitEdge endpoint selection |
| [Twi251](Twi251.stp) | ShapeFix_IntersectionTool FixIntersectingWires null input guard |
| [Twi252](Twi252.stp) | ShapeAnalysis_Wire.CheckConnected.WIRE_NOT_LOADED |
| [Twi253](Twi253.stp) | ShapeAnalysis_Wire.CheckConnected.NULL_EDGE_VERTICES |
| [Twi254](Twi254.stp) | ShapeAnalysis_Wire.CheckConnected.SAME_VERTEX_BOTH_ENDS |
| [Twi255](Twi255.stp) | ShapeAnalysis_Wire.CheckLoop.null-vertices |
| [Twi256](Twi256.stp) | ShapeAnalysis_Wire.CheckLoop.degenerated-edge-filter |
| [Twi257](Twi257.stp) | unloaded-or-trivial-wire |
| [Twi258](Twi258.stp) | self-loop-small-edge |
| [Twi259](Twi259.stp) | self-loop-binding |
| [Twi260](Twi260.stp) | multi-vertex-self-loop-check |
| [Twi261](Twi261.stp) | dual-vertex-binding |
| [Twi262](Twi262.stp) | CheckOrder nullface |
| [Twi263](Twi263.stp) | CheckSelfIntersection acyclic-crossing |
| [Twi264](Twi264.stp) | FixConnected gap-skip |
| [Twi265](Twi265.stp) | FixClosed endpoint-mismatch |
| [Twi266](Twi266.stp) | FixGap3d parameter-discontinuity |
| [Twi267](Twi267.stp) | ShapeAnalysis_Wire.CheckOuterBound |
| [Twi268](Twi268.stp) | ShapeAnalysis_Wire.CheckSeam |
| [Twi269](Twi269.stp) | ShapeAnalysis_Wire.CheckSelfIntersectingEdge |
| [Twi270](Twi270.stp) | ShapeAnalysis_Wire.CheckShapeConnect |
| [Twi271](Twi271.stp) | ShapeAnalysis_Wire.CheckTail |
| [Twi272](Twi272.stp) | CheckLoop Unloaded/Trivial |
| [Twi273](Twi273.stp) | CheckLoop Null Vertices |
| [Twi274](Twi274.stp) | CheckLoop Seam Classification |
| [Twi275](Twi275.stp) | CheckLoop Multi-Vertex Self-Loop |
| [Twi276](Twi276.stp) | CheckLoop Multi-Vertex V2-Check |
| [Twi277](Twi277.stp) | SURFACE_CURVE wraps null after StepGeom_SurfaceCurve downcast (OCE legacy) |
| [Twi278](Twi278.stp) | AP242 Ed.3 length-constrained curve/topology triad (`BOUNDED_CURVE_WITH_LENGTH` + `EDGE_BOUNDED_CURVE_WITH_LENGTH` + `EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT`) dropped by Ed.2/AP214 readers |
| [Twi279](Twi279.stp) | AP242 Ed.3 `CONNECTED_EDGE_SUB_SET` semantic sub-region grouping dropped by Ed.2/AP214 readers |
| [Twi280](Twi280.stp) | AP242 Ed.3 `SUBPATH` named path sub-region dropped by Ed.2/AP214 readers |
| [Twi281](Twi281.stp) | `VERTEX_LOOP` point-loop used as the sole `FACE_OUTER_BOUND` of an `ADVANCED_FACE` on a non-singular `PLANE` (loop-degeneracy flag vs flat geometry) |
| [Twi282](Twi282.stp) | Cyclic `ORIENTED_EDGE.edge_element` self-reference → unbounded `EdgeStart`/`EdgeEnd` recursion (stack-overflow DoS) |
| [Twi284](Twi284.stp) | Consecutive wire edges share a corner location via two distinct `VERTEX_POINT` entities (coincident, not reused) |
| [Twi285](Twi285.stp) | Two arbitrary, non-adjacent edges (different faces) register as touching via coincident-but-distinct `VERTEX_POINT` entities in a broader connectivity graph |
| [Twi286](Twi286.stp) | Minimal self-intersecting (bow-tie) wire on a single real `ADVANCED_FACE`, no confounding defects |
| [Twi287](Twi287.stp) | Full-period closed meridian edges on a `TOROIDAL_SURFACE` belt need splitting at the seam (insurance fixture, distinct surface kind from Twi019) |
| [Twi288](Twi288.stp) | Non-convex dart outer wire and inner triangle hole share a common pinch `VERTEX_POINT` at the face centre (insurance fixture, distinct geometry from Twi009) |
| [Twi289](Twi289.stp) | Edge with neither a 3D curve nor a usable pcurve is REMOVED from the wire (not reconstructed) |
| [Twi290](Twi290.stp) | Non-closed curve whose two distinct vertices project to an identical parameter (null arc length) is discarded in favor of a straight-line fallback |
| [Twi291](Twi291.stp) | Two adjacent wire edges' shared corner is encoded as two distinct `VERTEX_POINT`s coincident within tolerance (not bit-identical) |
| [Twi292](Twi292.stp) | Short arc straddling a closed curve's parameter seam: projected endpoint parameters come back swapped (w1 > w2) |
| [Twi293](Twi293.stp) | Full-period closed edge nested inside a TRIMMED_CURVE wrapper defeats the closed-curve split entirely |
| [Twi294](Twi294.stp) | Open chain of two arcs of the same CIRCLE entity (not yet closing to a full circle) should be fused into one arc |
| [Twi295](Twi295.stp) | Chain of two tangent-continuous cubic Bezier edges should be concatenated under ConcatBSplines mode |
| [Twi296](Twi296.stp) | Degenerated ("spindle") torus (major radius < minor radius) missing its apex edge at aPhi = acos(-R/r) |
| [Twi297](Twi297.stp) | B-spline surface pinched to a single point at its V=0 boundary (bug 24055 path), missing degenerate edge |
| [Twi298](Twi298.stp) | Two NON-ADJACENT wire edges share a large (>50%) collinear overlap, forcing the 3-edge reconstruction path |
| [Twi299](Twi299.stp) | Whole-circle edge whose VERTEX_POINT sits at the circle's own center (no unique nearest point for projection) |
| [Twi300](Twi300.stp) | Edge trimmed onto an unbounded LINE by a vertex enormously far along the line's own direction |
| [Twi301](Twi301.stp) | EDGE_CURVE flagged degenerate but its 3D LINE has positive length, face-hosted on a real ADVANCED_FACE/CONICAL_SURFACE |
| [Twi302](Twi302.stp) | Small SEAM edge on a periodic face, adjacent to another seam segment: seam-with-seam merge |
| [Twi303](Twi303.stp) | Small edge at a sharp corner (non-collinear neighbors on both sides): drop-mode-only merge |
| [Twi304](Twi304.stp) | Multi-face shared full-circle edge that must NOT be collapsed as a "small edge" (protection case) |
| [Twi305](Twi305.stp) | Apex-bridging edge already PRESENT at the cone singularity (single, correctly positioned): dgnr/replace input |
