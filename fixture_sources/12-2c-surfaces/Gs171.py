"""Gs171 — ShapeAnalysis_Surface: surface domain mismatch on projection result.

Catalog claim: NextValueOfUV returns UV outside RECTANGULAR_TRIMMED_SURFACE
domain bounds [0.2,0.8]²; bounds-check missing on result validation.
Defect: unchecked UV parameter alignment.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RECTANGULAR_TRIMMED_SURFACE (PLANE basis, u1=0.2, u2=0.8, v1=0.2,
    v2=0.8) IS the ADVANCED_FACE.face_geometry; face boundary edge pcurves
    referencing the trimmed surface with bounds [0.2,0.8]² IS the mechanism
    wired into face topology; ShapeAnalysis_Surface NextValueOfUV returning
    UV outside [0.2,0.8]² without bounds-check IS the defect.
  - Byte assertions: contains(b'RECTANGULAR_TRIMMED_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RECTANGULAR_TRIMMED_SURFACE (PLANE basis, domain
    [0.2,0.8]²) IS ADVANCED_FACE.face_geometry; face boundary edge pcurves
    on trimmed surface IS the mechanism wired into face topology;
    ShapeAnalysis_Surface NextValueOfUV result not validated against
    [0.2,0.8]² domain bounds IS the defect.
  - shape_null driver: out-of-domain UV projection used without check;
    downstream UV-based operations produce invalid results; strict kernels
    reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs171",
    defect=(
        "RECTANGULAR_TRIMMED_SURFACE (PLANE basis, domain [0.2,0.8]²) IS "
        "ADVANCED_FACE.face_geometry; face boundary edge pcurves on trimmed "
        "surface IS the mechanism wired into face topology; "
        "ShapeAnalysis_Surface NextValueOfUV result not validated against "
        "[0.2,0.8]² domain bounds (unchecked UV parameter alignment) IS the "
        "defect; shape_null"
    ),
)

# ── PLANE basis for the trimmed surface ───────────────────────────────────────
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
#
# The RECTANGULAR_TRIMMED_SURFACE clips the infinite plane to domain
# [0.2, 0.8] × [0.2, 0.8]. ShapeAnalysis_Surface.NextValueOfUV iterates
# sampling points; when it steps past the trimmed domain boundary, the
# returned UV (e.g., u=0.9) is outside [0.2,0.8] but no bounds-check is
# applied, causing misaligned UV parameter usage.

plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_norm = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs171_pl_ax',#{plane_orig.eid},#{plane_norm.eid},#{plane_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('gs171_plane',#{plane_ax.eid})")

# RECTANGULAR_TRIMMED_SURFACE: domain [0.2, 0.8]²
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs171_rts',#{plane.eid},0.2,0.8,0.2,0.8,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary in trimmed surface UV domain [0.2,0.8]² ────────────────────
p_A = f.cartesian_point((0.2, 0.2, 0.0))
p_B = f.cartesian_point((0.8, 0.2, 0.0))
p_C = f.cartesian_point((0.8, 0.8, 0.0))
p_D = f.cartesian_point((0.2, 0.8, 0.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{rts.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# Bottom: A→B, u=0.2→0.8 at v=0.2
e0 = mk_edge_line(v_A, v_B,
                  (0.2, 0.2, 0.0), (1.0, 0.0, 0.0), 0.6,
                  (0.2, 0.2), (1.0, 0.0), 0.6)
# Right: B→C, v=0.2→0.8 at u=0.8
e1 = mk_edge_line(v_B, v_C,
                  (0.8, 0.2, 0.0), (0.0, 1.0, 0.0), 0.6,
                  (0.8, 0.2), (0.0, 1.0), 0.6)
# Top: C→D, u=0.8→0.2 at v=0.8
e2 = mk_edge_line(v_C, v_D,
                  (0.8, 0.8, 0.0), (-1.0, 0.0, 0.0), 0.6,
                  (0.8, 0.8), (-1.0, 0.0), 0.6)
# Left: D→A, v=0.8→0.2 at u=0.2
e3 = mk_edge_line(v_D, v_A,
                  (0.2, 0.8, 0.0), (0.0, -1.0, 0.0), 0.6,
                  (0.2, 0.8), (0.0, -1.0), 0.6)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RECTANGULAR_TRIMMED_SURFACE (domain [0.2,0.8]²) IS the face_geometry; face
# boundary edge pcurves on the trimmed surface IS the mechanism wired into face
# topology — exercises ShapeAnalysis_Surface NextValueOfUV missing bounds-check
# against [0.2,0.8]² domain.
face  = f.advanced_face([f.face_outer_bound(loop)], rts)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
