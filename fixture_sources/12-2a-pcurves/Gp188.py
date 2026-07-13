"""Gp188 — Second independent COMPOSITE_CURVE fixture with a genuine
post-reorder connectivity gap, distinct geometry and distinct gap
location from Gp034 (stp-compcurve-disconnected, single-fixture-thin).

Work packet D2, item `stp-compcurve-disconnected` (PARTIAL,
single-fixture-thin), problem_id `stp-compcurve-disconnected`: "After
segment reordering, adjacent COMPOSITE_CURVE segments' endpoints still do
not coincide ... OCCT does not fail the whole composite-curve
translation for this; it flags the disconnection as a warning and still
returns the (locally disconnected) wire."
(StepToTopoDS_TranslateCompositeCurve::Init, StepToTopoDS_
TranslateCompositeCurve.cxx:275-278 -- sfw->FixConnected(preci);
StatusConnected(FAIL) -> warning only, translation still returns True.)

Distinctness from Gp034: Gp034 is a 2-segment, LINE+LINE, open (not
closed) COMPOSITE_CURVE used as ONE edge of a 4-edge rectangular face,
with a 5mm INTERIOR gap between its two segments. This fixture is a
3-segment, closed (`.T.`) COMPOSITE_CURVE used as the SOLE self-closed
boundary of a face (a single-edge loop, not one edge among four) with a
4mm gap specifically at the WRAP-AROUND CLOSURE -- segment 3's end does
not coincide with segment 1's start, a distinct connectivity-check
sub-case (closure-seam gap vs. interior-segment gap) on genuinely
different numeric geometry.

Mechanism: A face on a PLANE. Three LINE segments form an approximate
triangular rim: segment1 (0,0,0)->(6,0,0), segment2 (6,0,0)->(6,4,0),
segment3 (6,4,0)->(0.004,0,0) -- 4mm short of closing back to
(0,0,0), the true start of segment1. COMPOSITE_CURVE's closed_curve flag
is `.T.` (it is DECLARED closed) even though the third segment's actual
endpoint misses the first segment's start point by 4mm. A single
EDGE_CURVE (self-loop, same start/end VERTEX_POINT at the true origin)
uses this composite curve as its 3D geometry, forming the sole boundary
of the ADVANCED_FACE.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp188",
    defect=(
        "COMPOSITE_CURVE (closed_curve=.T.) of three LINE segments forming an "
        "approximate triangular rim: (0,0,0)->(6,0,0)->(6,4,0)->(0.004,0,0) -- "
        "segment 3 ends 4mm short of segment 1's true start (0,0,0), a "
        "wrap-around CLOSURE gap (not Gp034's interior 2-segment gap); "
        "single self-loop EDGE_CURVE forms the sole boundary of an ADVANCED_FACE"
    ),
)

# Flat PLANE at Z=0 as the host surface.
p_orig = f.cartesian_point((0.0, 0.0, 0.0))
p_norm = f.direction((0.0, 0.0, 1.0))
p_ref = f.direction((1.0, 0.0, 0.0))
p_axis = f.axis2_placement_3d(p_orig, p_norm, p_ref)
plane = f.plane(p_axis)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Rim points.
p0 = f.cartesian_point((0.0, 0.0, 0.0))     # true origin / declared vertex
p1 = f.cartesian_point((6.0, 0.0, 0.0))
p2 = f.cartesian_point((6.0, 4.0, 0.0))
p_gap_end = f.cartesian_point((0.004, 0.0, 0.0))  # 4mm short of p0 -- THE GAP

v0 = f.vertex_point(p0)

# Segment 1: p0 -> p1 (length 6).
seg1_line = f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 6.0))
# Segment 2: p1 -> p2 (length 4).
seg2_line = f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 4.0))
# Segment 3: p2 -> p_gap_end (length ~5.999666, direction back toward p0 but
# stopping 4mm short).
import math
dx = 0.004 - 6.0
dy = 0.0 - 4.0
seg3_len = math.hypot(dx, dy)
seg3_dir = (dx / seg3_len, dy / seg3_len, 0.0)
seg3_line = f.line(p2, f.vector(f.direction(seg3_dir), seg3_len))

seg1 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{seg1_line.eid})")
seg2 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{seg2_line.eid})")
seg3 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{seg3_line.eid})")

# THE DEFECT: declared closed_curve=.T. even though segment3's actual
# endpoint (0.004,0,0) misses segment1's true start (0,0,0) by 4mm.
composite_curve = f._emit_raw(
    f"COMPOSITE_CURVE('triangular_rim_closure_gap',"
    f"(#{seg1.eid},#{seg2.eid},#{seg3.eid}),.T.)"
)

# Matching-ish pcurve: a single straight UV LINE spanning roughly the same
# overall extent as the 3D rim (same simplification Gp034 uses for its
# composite-curve edge: one LINE representation, not a per-segment trace).
# Not required to trace the gap byte-for-byte; only the 3D composite curve
# carries the connectivity defect.
pc_p0 = f.cartesian_point((0.0, 0.0))
pc_line = f.line(pc_p0, f.vector(f.direction((1.0, 0.0)), 6.0))
pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp188_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp188_uv',#{plane.eid},#{pc_def.eid})")

sc = f._emit_raw(
    f"SURFACE_CURVE('triangular_rim',#{composite_curve.eid},"
    f"(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('rim_edge',#{v0.eid},#{v0.eid},#{sc.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
