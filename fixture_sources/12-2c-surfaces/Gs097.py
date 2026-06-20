"""Gs097 — ShapeUpgrade_FaceDivideArea.Perform threshold reset.

Catalog claim: ShapeUpgrade_FaceDivideArea splits a face when area exceeds a
runtime threshold. Threshold value 0.0 should be a no-op ("don't split") but
is incorrectly treated as "split every sub-face", triggering unbounded recursion.
The threshold is a runtime API argument; this fixture provides the geometric
setup (large planar face) on which the defect is observable.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - PLANE (XY-plane, Z=0) IS the ADVANCED_FACE.face_geometry; large face
    boundary (10×10 unit square) IS the mechanism wired into face topology;
    FaceDivideArea with SetMaxArea(0.0) triggers unbounded recursion on every
    sub-face because threshold 0.0 is treated as "always split" rather than
    no-op IS the defect.
  - Byte assertions: contains(b'PLANE'),
                     contains(b'10.').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE (Z=0, XY-plane) IS the ADVANCED_FACE.face_geometry;
    large 10×10 face boundary IS the mechanism wired into face topology;
    FaceDivideArea(SetMaxArea=0.0) treats zero threshold as "always split"
    instead of no-op, causing unbounded recursion IS the defect.
  - shape_null driver: geometry setup for runtime-triggered recursion; strict
    kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs097",
    defect=(
        "PLANE (XY-plane, Z=0) IS ADVANCED_FACE.face_geometry; large 10×10 "
        "face boundary IS the mechanism wired into face topology; "
        "FaceDivideArea SetMaxArea(0.0) treats zero as 'always split' not "
        "no-op, triggering unbounded recursion IS the defect; shape_null"
    ),
)

# ── PLANE: XY-plane at Z=0 ────────────────────────────────────────────────────
# Byte assertion: contains(b'PLANE')
pln_orig = f.cartesian_point((0.0, 0.0, 0.0))
pln_zdir = f.direction((0.0, 0.0, 1.0))
pln_xdir = f.direction((1.0, 0.0, 0.0))
pln_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs097_pln_ax',#{pln_orig.eid},#{pln_zdir.eid},#{pln_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('gs097_plane',#{pln_ax.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: large 10×10 square ─────────────────────────────────────────
# Byte assertion: contains(b'10.')
# Large area ensures FaceDivideArea threshold comparison is triggered.
p_A = f.cartesian_point(( 0.0,  0.0, 0.0))
p_B = f.cartesian_point((10.0,  0.0, 0.0))
p_C = f.cartesian_point((10.0, 10.0, 0.0))
p_D = f.cartesian_point(( 0.0, 10.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

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

# e0: bottom A→B (v=0, u: 0→10)
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 10.0,
                  (0.0, 0.0), (1.0, 0.0), 10.0)
# e1: right B→C (u=10, v: 0→10)
e1 = mk_edge_line(v_B, v_C,
                  (10.0, 0.0, 0.0), (0.0, 1.0, 0.0), 10.0,
                  (10.0, 0.0), (0.0, 1.0), 10.0)
# e2: top C→D (v=10, u: 10→0)
e2 = mk_edge_line(v_C, v_D,
                  (10.0, 10.0, 0.0), (-1.0, 0.0, 0.0), 10.0,
                  (10.0, 10.0), (-1.0, 0.0), 10.0)
# e3: left D→A (u=0, v: 10→0)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 10.0, 0.0), (0.0, -1.0, 0.0), 10.0,
                  (0.0, 10.0), (0.0, -1.0), 10.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# PLANE IS the face_geometry; large 10×10 boundary IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
