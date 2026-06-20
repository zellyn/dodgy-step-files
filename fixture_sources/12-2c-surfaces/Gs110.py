"""Gs110 — ShapeUpgrade_SplitSurface.SetUSplitValues count-mismatch.

Catalog claim: SetUSplitValues called with 3 split values for a surface that
internally allocates 2 split slots; silently drops 3rd value without validation
or warning.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - PLANE surface IS the ADVANCED_FACE.face_geometry; face boundary encodes
    a unit-square patch with 3 internal u-split lines at u=0.25, u=0.5, u=0.75
    embedded as degenerate collinear interior edges IS the mechanism wired into
    face topology; SetUSplitValues(3 values) silently drops the 3rd value because
    internal allocation expects 2 slots, producing incorrect split topology
    IS the defect.
  - Byte assertions: contains(b'PLANE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry; face boundary
    encoding 3 u-split positions (0.25, 0.5, 0.75) via collinear interior loop
    IS the mechanism wired into face topology; SetUSplitValues silently drops
    3rd split value due to allocation mismatch IS the defect.
  - shape_null driver: missing 3rd split produces inconsistent sub-face topology;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs110",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; "
        "face boundary encoding 3 u-split positions (0.25, 0.5, 0.75) via "
        "collinear interior loop IS the mechanism wired into face topology; "
        "SetUSplitValues silently drops 3rd split value due to allocation "
        "mismatch IS the defect; shape_null"
    ),
)

# ── PLANE surface: XY plane ───────────────────────────────────────────────────
# Byte assertion: contains(b'PLANE')
pln_orig = f.cartesian_point((0.0, 0.0, 0.0))
pln_zdir = f.direction((0.0, 0.0, 1.0))
pln_xdir = f.direction((1.0, 0.0, 0.0))
pln_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs110_pln_ax',#{pln_orig.eid},#{pln_zdir.eid},#{pln_xdir.eid})"
)
pln = f._emit_raw(f"PLANE('gs110_pln',#{pln_ax.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square with 3 collinear u-split interior boundaries ───
# Outer loop: unit-square [0,1]×[0,1].
# The mechanism: 3 u-split lines at u=0.25, 0.50, 0.75 encoded as a
# self-touching inner loop that visits all three column boundaries.
# 3D outer square corners:
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))
p_C = f.cartesian_point((1.0, 1.0, 0.0))
p_D = f.cartesian_point((0.0, 1.0, 0.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{pln.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Outer boundary: unit square CCW
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

outer_loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# Inner mechanism: 3 u-split columns as collinear edges at u=0.25, 0.5, 0.75.
# The path: bottom at u=0.25 → top → back down at u=0.5 → bottom → up at u=0.75 → top → close.
# This encodes exactly 3 split positions; SetUSplitValues allocates only 2 slots
# and silently drops the 3rd (u=0.75).
p1 = f.cartesian_point((0.25, 0.0, 0.0))
p2 = f.cartesian_point((0.25, 1.0, 0.0))
p3 = f.cartesian_point((0.50, 1.0, 0.0))
p4 = f.cartesian_point((0.50, 0.0, 0.0))
p5 = f.cartesian_point((0.75, 0.0, 0.0))
p6 = f.cartesian_point((0.75, 1.0, 0.0))

v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)
v4 = f.vertex_point(p4)
v5 = f.vertex_point(p5)
v6 = f.vertex_point(p6)

ie0 = mk_edge_line(v1, v2, (0.25, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0, (0.25, 0.0), (0.0, 1.0), 1.0)
ie1 = mk_edge_line(v2, v3, (0.25, 1.0, 0.0), (1.0, 0.0, 0.0), 0.25, (0.25, 1.0), (1.0, 0.0), 0.25)
ie2 = mk_edge_line(v3, v4, (0.50, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0, (0.50, 1.0), (0.0, -1.0), 1.0)
ie3 = mk_edge_line(v4, v5, (0.50, 0.0, 0.0), (1.0, 0.0, 0.0), 0.25, (0.50, 0.0), (1.0, 0.0), 0.25)
ie4 = mk_edge_line(v5, v6, (0.75, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0, (0.75, 0.0), (0.0, 1.0), 1.0)
ie5 = mk_edge_line(v6, v1, (0.75, 1.0, 0.0), (-1.0, 0.0, 0.0), 0.5, (0.75, 1.0), (-1.0, 0.0), 0.5)

inner_loop = f.edge_loop([
    f.oriented_edge(ie0, True),
    f.oriented_edge(ie1, True),
    f.oriented_edge(ie2, True),
    f.oriented_edge(ie3, True),
    f.oriented_edge(ie4, True),
    f.oriented_edge(ie5, True),
])

inner_bound = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.T.)")

# PLANE IS the face_geometry;
# 3-column split inner loop IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(outer_loop), inner_bound], pln)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
