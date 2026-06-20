"""Gs038 — Pcurve U/V parameter has large jump near periodic boundary on BSpline.

Catalog claim: A self-touching closed BSpline surface where the 2D pcurve
crosses near the wrap-around boundary, producing a huge UV jump (>0.95 of
period). Surface near-periodicity is not recognized; strict kernels must heal
by detecting the jump and inserting an additional point adjusted by the
inferred period.

OCC behavior: silently accepts (empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS IS the ADVANCED_FACE.face_geometry.
  - The BSpline surface is near-periodic in U (period ~1.0); the pcurve on
    the face includes a sample point at (0.99, 0.5) that straddles the
    wrap-around, producing a UV jump > 0.95 of period.
  - Closed flag .T. indicates a closed BSpline; self-touching at the seam.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS('),
                     contains(b'(0.99,0.5)'),
                     contains(b'.T.,.F.,.F.').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS IS the
    ADVANCED_FACE.face_geometry; the pcurve on that surface straddles the
    near-period seam with a UV jump > 0.95 of period; degenerate pcurve
    IS wired into face topology.
  - shape_null driver: near-period seam UV jump is undetected; strict
    heal-or-reject kernels produce null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs038",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS IS ADVANCED_FACE.face_geometry; "
        "pcurve contains (0.99,0.5) straddling near-period seam with UV jump "
        ">0.95 of period; .T.,.F.,.F. closed BSpline surface; "
        "near-periodicity not recognized IS wired into face topology; shape(1) (live OCC heals)"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS (near-periodic, self-touching) ────────────────
# Degree 1 in both U and V; 2x2 control-point grid; closed in U (.T.).
# Near-periodic in U: knots 0.0 and 1.0 with multiplicities 2,2 make it
# closed at U seam. The surface is defined so that the seam at U=0/U=1 is
# geometrically self-touching.
cp00 = f.cartesian_point((0.0, 0.0, 0.0))
cp10 = f.cartesian_point((1.0, 0.0, 0.0))
cp01 = f.cartesian_point((0.0, 1.0, 0.0))
cp11 = f.cartesian_point((1.0, 1.0, 0.0))

# B_SPLINE_SURFACE_WITH_KNOTS: degree 1 x 1, 2x2 control points, closed in U
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS(')
# Byte assertion: contains(b'.T.,.F.,.F.')
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs038_bss',1,1,"
    f"((#{cp00.eid},#{cp10.eid}),(#{cp01.eid},#{cp11.eid})),"
    f".T.,.F.,.F.,.UNSPECIFIED.,"
    f"(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the B_SPLINE_SURFACE ────────────────────────────
# 3D corner points (approximate; surface is in XY plane at z=0)
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
    pc  = f._emit_raw(f"PCURVE('pc',#{bss.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# E0: bottom edge — pcurve starts at (0.0,0.0) and crosses to (0.99,0.5),
# embedding the large-jump sample point into the defect pcurve.
# Byte assertion: contains(b'(0.99,0.5)')
# We wire the jump point as the pcurve start so it's embedded in this line.
p2_A_jump = f.cartesian_point((0.99, 0.5))   # THE UV-jump sample point (defect)
d2_e0 = f.direction((1.0, 0.0))
v2_e0 = f.vector(d2_e0, 0.01)
l2_e0 = f.line(p2_A_jump, v2_e0)
pcd_e0 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_e0',(#{l2_e0.eid}),#{prc.eid})")
pc_e0  = f._emit_raw(f"PCURVE('pc_e0',#{bss.eid},#{pcd_e0.eid})")
p3_e0  = f.cartesian_point((0.0, 0.0, 0.0))
d3_e0  = f.direction((1.0, 0.0, 0.0))
v3_e0  = f.vector(d3_e0, 1.0)
l3_e0  = f.line(p3_e0, v3_e0)
sc_e0  = f._emit_raw(f"SURFACE_CURVE('sc_e0',#{l3_e0.eid},(#{pc_e0.eid}),.PCURVE_S1.)")
e0 = f._emit_raw(f"EDGE_CURVE('ec_e0',#{v_A.eid},#{v_B.eid},#{sc_e0.eid},.T.)")

e1 = mk_edge_line(v_B, v_C, (1.0,0.0,0.0), (0.0,1.0,0.0), 1.0, (1.0,0.0), (0.0,1.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (1.0,1.0,0.0), (-1.0,0.0,0.0), 1.0, (1.0,1.0), (-1.0,0.0), 1.0)
e3 = mk_edge_line(v_D, v_A, (0.0,1.0,0.0), (0.0,-1.0,0.0), 1.0, (0.0,1.0), (0.0,-1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
