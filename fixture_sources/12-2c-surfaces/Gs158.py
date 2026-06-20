"""Gs158 — AddFace null geometry propagation.

Catalog claim: BRepBuilderAPI_Sewing::AddFace does not validate non-null surface
reference on ADVANCED_FACE. Invalid geometry propagates silently, breaking shell
coherence.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - ADVANCED_FACE referencing a null (absent) surface entity (face_geometry
    attribute resolves to $) IS the ADVANCED_FACE; face boundary edge pcurves
    referencing the null-geometry face IS the mechanism wired into face topology;
    AddFace null-geometry propagation without validation IS the defect.
  - Byte assertions: contains(b'ADVANCED_FACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: ADVANCED_FACE with null face_geometry (surface ref = $)
    IS the face; face boundary EDGE_LOOP with pcurves referencing absent surface
    IS the mechanism wired into face topology; AddFace failure to validate
    non-null surface reference IS the defect.
  - shape_null driver: null surface reference propagates into shell; sewing
    produces incoherent shell; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs158",
    defect=(
        "ADVANCED_FACE with null face_geometry (surface ref = $) IS the face; "
        "face boundary EDGE_LOOP with pcurves referencing absent surface IS "
        "the mechanism wired into face topology; AddFace null-geometry "
        "propagation without validation IS the defect; shape_null"
    ),
)

# ── ADVANCED_FACE with null face_geometry ─────────────────────────────────────
# Byte assertion: contains(b'ADVANCED_FACE')
# We build a complete EDGE_LOOP boundary with proper pcurves, then emit the
# ADVANCED_FACE with face_geometry = $ (null).  This is the exact state that
# BRepBuilderAPI_Sewing::AddFace should catch but silently propagates.

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square in XY plane ────────────────────────────────────
# 3D corners at z=0; pcurves in UV parameterized as [0,1]x[0,1].
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))
p_C = f.cartesian_point((1.0, 1.0, 0.0))
p_D = f.cartesian_point((0.0, 1.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_edge_line_null_surf(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    """Build edge with pcurve referencing a null (absent) surface context."""
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    # PCURVE references $  — null surface, the propagation mechanism
    pc  = f._emit_raw(f"PCURVE('pc',$,#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Bottom: A→B
e0 = mk_edge_line_null_surf(v_A, v_B,
                            (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                            (0.0, 0.0), (1.0, 0.0), 1.0)
# Right: B→C
e1 = mk_edge_line_null_surf(v_B, v_C,
                            (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                            (1.0, 0.0), (0.0, 1.0), 1.0)
# Top: C→D
e2 = mk_edge_line_null_surf(v_C, v_D,
                            (1.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                            (1.0, 1.0), (-1.0, 0.0), 1.0)
# Left: D→A
e3 = mk_edge_line_null_surf(v_D, v_A,
                            (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                            (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

fob = f.face_outer_bound(loop)

# ADVANCED_FACE with null face_geometry ($) IS the face; face boundary EDGE_LOOP
# with pcurves referencing null surface IS the mechanism wired into face topology
# — exercises BRepBuilderAPI_Sewing::AddFace null-geometry propagation.
# We emit ADVANCED_FACE directly to pass null ($) as face_geometry.
face = f._emit_raw(
    f"ADVANCED_FACE('gs158_null_face',(#{fob.eid}),$,.T.)"
)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
