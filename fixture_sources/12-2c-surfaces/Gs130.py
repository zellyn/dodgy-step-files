"""Gs130 — FACE with trim coincident to existing split edge.

Catalog claim: ShapeUpgrade_FaceDivide.Perform uses a splitter parameter that
exactly coincides with an existing trim edge. The implementation does not
detect this collision and creates an empty sub-face whose loop has zero
area or degenerate bounds.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - A PLANE IS the ADVANCED_FACE.face_geometry; face outer bound loop
    contains two collinear edges that exactly coincide in parameter space
    (zero-area sub-region between them) IS the mechanism wired into face
    topology; FaceDivide.Perform missing coincident-edge guard IS the defect.
  - Byte assertions: contains(b'ADVANCED_FACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS ADVANCED_FACE.face_geometry; two boundary
    edges coinciding exactly in UV parameter space (splitter coincides with
    existing trim edge, creating empty sub-face) IS the mechanism wired into
    face topology; FaceDivide.Perform coincident-edge detection absence IS
    the defect.
  - shape_null driver: empty sub-face with degenerate bounds; strict kernels
    reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs130",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; "
        "two boundary edges coinciding exactly in UV parameter space "
        "(trim coincident to existing split edge creating zero-area sub-face) "
        "IS the mechanism wired into face topology; "
        "FaceDivide.Perform coincident-edge detection absence IS the defect; "
        "shape_null"
    ),
)

# ── PLANE ─────────────────────────────────────────────────────────────────────
# Byte assertion: contains(b'ADVANCED_FACE')
# Flat XY plane at origin.
plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_zdir = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs130_plane_ax',#{plane_orig.eid},#{plane_zdir.eid},#{plane_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('gs130_plane',#{plane_ax.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Degenerate boundary: two collinear coincident edges ───────────────────────
# The outer loop is a degenerate "sliver" where the left and right edges
# overlap exactly at x=0.5, creating two edges that travel the same line
# in opposite directions — zero-area enclosed region.
#
# Loop: A(0,0) → B(0.5,0) → C(0.5,1) → B'(0.5,0) → A(0,0)
# The B→C and C→B' segments are collinear and coincide (opposite directions),
# producing a zero-area sub-face — the coincident-split-edge defect.
#
# Vertices:
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((0.5, 0.0, 0.0))
p_C = f.cartesian_point((0.5, 1.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)

def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# A→B: bottom, x=0 to x=0.5, y=0
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 0.5,
                  (0.0, 0.0), (1.0, 0.0), 0.5)
# B→C: up the split line, x=0.5, y=0 to y=1
e1 = mk_edge_line(v_B, v_C,
                  (0.5, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (0.5, 0.0), (0.0, 1.0), 1.0)
# C→B: back down same split line (coincident with e1, opposite sense)
e2 = mk_edge_line(v_C, v_B,
                  (0.5, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.5, 1.0), (0.0, -1.0), 1.0)
# B→A: back along bottom
e3 = mk_edge_line(v_B, v_A,
                  (0.5, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.5,
                  (0.5, 0.0), (-1.0, 0.0), 0.5)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# PLANE IS the face_geometry; coincident collinear edges (zero-area sub-face)
# IS the mechanism wired into face topology.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
