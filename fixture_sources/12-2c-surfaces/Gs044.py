"""Gs044 — INTERSECTION_CURVE between two surfaces with multiple disjoint branches, only one represented.

Catalog claim: TOROIDAL_SURFACE major=10, minor=3 intersects PLANE z=0 along
two concentric circles (r=7 inner, r=13 outer). The INTERSECTION_CURVE entity
represents only the outer branch (r=13), silently dropping the inner.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE (major=10, minor=3) IS the face_geometry of the defect ADVANCED_FACE.
  - INTERSECTION_CURVE holding only the outer circle (r=13) — one branch of
    a two-branch intersection — IS the curve_3d of the defect EDGE_CURVE's
    SURFACE_CURVE, wired into face topology.
  - Byte assertions: contains(b'INTERSECTION_CURVE('),
                     contains(b'TOROIDAL_SURFACE('),
                     contains(b"CIRCLE('outer_branch'").
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE IS the ADVANCED_FACE.face_geometry;
    INTERSECTION_CURVE representing only one of two disjoint torus-plane
    intersection branches IS the curve_3d of the defect EDGE_CURVE; single-
    branch INTERSECTION_CURVE IS wired into face topology.
  - shape_null driver: incomplete intersection curve (missing branch); strict
    reject kernels produce empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs044",
    defect=(
        "TOROIDAL_SURFACE (major=10, minor=3) IS ADVANCED_FACE.face_geometry; "
        "INTERSECTION_CURVE holding only outer circle (r=13) of two-branch "
        "torus-plane intersection IS curve_3d of defect EDGE_CURVE; "
        "single-branch INTERSECTION_CURVE IS wired into face topology; shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: TOROIDAL_SURFACE as face_geometry ──────────────────────
# Byte assertion: contains(b'TOROIDAL_SURFACE(')
tor_orig = f.cartesian_point((0.0, 0.0, 0.0))
tor_zdir = f.direction((0.0, 0.0, 1.0))
tor_xdir = f.direction((1.0, 0.0, 0.0))
tor_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs044_tor_ax',#{tor_orig.eid},#{tor_zdir.eid},#{tor_xdir.eid})"
)
# TOROIDAL_SURFACE(name, position, major_radius, minor_radius)
# major=10, minor=3 → intersection with z=0 plane at r=10-3=7 (inner) and r=10+3=13 (outer)
torus = f._emit_raw(f"TOROIDAL_SURFACE('gs044_torus',#{tor_ax.eid},10.0,3.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Outer branch circle at r=13 (the only branch in the INTERSECTION_CURVE) ───
# Byte assertion: contains(b"CIRCLE('outer_branch'")
circ_orig = f.cartesian_point((0.0, 0.0, 0.0))
circ_zdir = f.direction((0.0, 0.0, 1.0))
circ_xdir = f.direction((1.0, 0.0, 0.0))
circ_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs044_circ_ax',#{circ_orig.eid},#{circ_zdir.eid},#{circ_xdir.eid})"
)
outer_circle = f._emit_raw(f"CIRCLE('outer_branch',#{circ_ax.eid},13.0)")

# ── Plane z=0 for intersection partner ────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs044_pl_ax',#{pl_orig.eid},#{pl_zdir.eid},#{pl_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('gs044_plane',#{pl_ax.eid})")

# ── INTERSECTION_CURVE: one-branch representation (defect) ────────────────────
# INTERSECTION_CURVE(name, curve_3d, associated_geometry, master_representation)
# associated_geometry lists pcurves onto both surfaces.
# Byte assertion: contains(b'INTERSECTION_CURVE(')

# pcurve onto torus
p2_tor_pt  = f.cartesian_point((0.0, 0.0))
p2_tor_d   = f.direction((1.0, 0.0))
p2_tor_v   = f.vector(p2_tor_d, 1.0)
p2_tor_l   = f.line(p2_tor_pt, p2_tor_v)
pcd_tor    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_tor',(#{p2_tor_l.eid}),#{prc.eid})")
pc_tor     = f._emit_raw(f"PCURVE('pc_torus',#{torus.eid},#{pcd_tor.eid})")

# pcurve onto plane
p2_pl_pt   = f.cartesian_point((0.0, 0.0))
p2_pl_d    = f.direction((1.0, 0.0))
p2_pl_v    = f.vector(p2_pl_d, 1.0)
p2_pl_l    = f.line(p2_pl_pt, p2_pl_v)
pcd_pl     = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_pl',(#{p2_pl_l.eid}),#{prc.eid})")
pc_pl      = f._emit_raw(f"PCURVE('pc_plane',#{plane.eid},#{pcd_pl.eid})")

int_curve = f._emit_raw(
    f"INTERSECTION_CURVE('gs044_ic',#{outer_circle.eid},(#{pc_tor.eid},#{pc_pl.eid}),.CURVE_3D.)"
)

# ── Face boundary: defect edge uses INTERSECTION_CURVE as curve_3d ────────────
# Representative points on the outer circle (r=13, z=0)
p_A = f.cartesian_point((13.0,  0.0, 0.0))
p_B = f.cartesian_point(( 0.0, 13.0, 0.0))
p_C = f.cartesian_point((-13.0, 0.0, 0.0))
p_D = f.cartesian_point(( 0.0,-13.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

# Defect edge E0: curve_3d IS INTERSECTION_CURVE (outer branch only)
p2_e0  = f.cartesian_point((0.0, 0.0))
d2_e0  = f.direction((1.0, 0.0))
v2_e0  = f.vector(d2_e0, 1.0)
l2_e0  = f.line(p2_e0, v2_e0)
pcd_e0 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_e0',(#{l2_e0.eid}),#{prc.eid})")
pc_e0  = f._emit_raw(f"PCURVE('pc_e0',#{torus.eid},#{pcd_e0.eid})")
sc_e0  = f._emit_raw(f"SURFACE_CURVE('sc_e0',#{int_curve.eid},(#{pc_e0.eid}),.PCURVE_S1.)")
e0 = f._emit_raw(f"EDGE_CURVE('ec_e0',#{v_A.eid},#{v_B.eid},#{sc_e0.eid},.T.)")

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
    pc  = f._emit_raw(f"PCURVE('pc',#{torus.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e1 = mk_edge_line(v_B, v_C, (0.0,13.0,0.0), (-1.0,0.0,0.0), 13.0, (0.0,1.0), (-1.0,0.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (-13.0,0.0,0.0), (0.0,-1.0,0.0), 13.0, (-1.0,0.0), (0.0,-1.0), 1.0)
e3 = mk_edge_line(v_D, v_A, (0.0,-13.0,0.0), (1.0,0.0,0.0), 13.0, (0.0,-1.0), (1.0,0.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# TOROIDAL_SURFACE IS the face_geometry; INTERSECTION_CURVE (one branch) IS defect edge 3D curve.
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
