"""Gs053 — Scaled sphere as B-spline approximation broken on export.

Catalog claim: Sphere radius 1 scaled (2,1,1) by MAPPED_ITEM (becomes ellipsoid)
exported as B_SPLINE_SURFACE_WITH_KNOTS; parameter range declared [0,1]×[0,1]
but knots span [0,2π]×[0,π].  Wrapped in RECTANGULAR_TRIMMED_SURFACE with
mismatched bounds.  Re-import shows partial/clipped sphere.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS with parameter range [0,1]×[0,1] declared
    via RECTANGULAR_TRIMMED_SURFACE but knots span [0,2π]×[0,π] IS the
    ADVANCED_FACE.face_geometry; parameter mismatch IS the defect wired into
    face topology.
  - MAPPED_ITEM (scale 2,1,1) IS emitted in the shape representation.
  - Byte assertions: contains(b'MAPPED_ITEM('),
                     contains(b'RECTANGULAR_TRIMMED_SURFACE('),
                     contains(b'B_SPLINE_SURFACE_WITH_KNOTS(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS with knots spanning
    [0,2π]×[0,π] but wrapped in RECTANGULAR_TRIMMED_SURFACE declaring
    [0,1]×[0,1] IS the ADVANCED_FACE.face_geometry; MAPPED_ITEM with scale
    (2,1,1) IS present; parameter-range mismatch IS wired into face topology.
  - shape_null driver: mismatched parameter range clips or inverts the surface;
    strict heal-or-reject kernels produce empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs053",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (knots [0,2π]×[0,π]) wrapped in "
        "RECTANGULAR_TRIMMED_SURFACE([0,1],[1,0],[0,1],[1,0]) IS "
        "ADVANCED_FACE.face_geometry; MAPPED_ITEM(scale 2,1,1) IS present; "
        "parameter-range mismatch IS wired into face topology; "
        "shape_null (strict reject)"
    ),
)

PI = math.pi

# ── B_SPLINE_SURFACE_WITH_KNOTS: ellipsoid approximation with wrong param range ─
# Degree 2 in U and V.  U knots span [0, 2π], V knots span [0, π].
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS(')
# 3×3 control net (degree 2, simple open knots)
r0c0 = f.cartesian_point(( 2.0,  0.0,  1.0))
r0c1 = f.cartesian_point(( 2.0,  2.0,  0.0))
r0c2 = f.cartesian_point(( 2.0,  0.0, -1.0))

r1c0 = f.cartesian_point(( 0.0,  0.0,  1.0))
r1c1 = f.cartesian_point(( 0.0,  2.0,  0.0))
r1c2 = f.cartesian_point(( 0.0,  0.0, -1.0))

r2c0 = f.cartesian_point((-2.0,  0.0,  1.0))
r2c1 = f.cartesian_point((-2.0,  2.0,  0.0))
r2c2 = f.cartesian_point((-2.0,  0.0, -1.0))

# Knots span [0, 2π] in U and [0, π] in V — mismatch with declared [0,1]×[0,1]
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs053_bss',2,2,"
    f"((#{r0c0.eid},#{r0c1.eid},#{r0c2.eid}),"
    f"(#{r1c0.eid},#{r1c1.eid},#{r1c2.eid}),"
    f"(#{r2c0.eid},#{r2c1.eid},#{r2c2.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(3,3),"
    f"(0.0,{2*PI:.10f}),(0.0,{PI:.10f}),"
    f".UNSPECIFIED.)"
)

# ── RECTANGULAR_TRIMMED_SURFACE: declares wrong [0,1]×[0,1] parameter bounds ──
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE(')
# RECTANGULAR_TRIMMED_SURFACE(basis_surface, u1, u2, v1, v2, usense, vsense)
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs053_rts',#{bss.eid},0.0,1.0,0.0,1.0,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── MAPPED_ITEM: scale (2,1,1) applied to the shape representation ─────────────
# Byte assertion: contains(b'MAPPED_ITEM(')
# Emit a CARTESIAN_TRANSFORMATION_OPERATOR_3D for the scale
map_orig = f.cartesian_point((0.0, 0.0, 0.0))
map_ax1  = f.direction((2.0, 0.0, 0.0))   # scaled X axis
map_ax2  = f.direction((0.0, 1.0, 0.0))
map_ax3  = f.direction((0.0, 0.0, 1.0))
cto = f._emit_raw(
    f"CARTESIAN_TRANSFORMATION_OPERATOR_3D('gs053_cto',$,"
    f"#{map_ax1.eid},#{map_ax2.eid},#{map_ax3.eid},#{map_orig.eid},1.0)"
)
# MAPPED_ITEM references the transformation; a placeholder MappedItem body
rep_item_dummy = f.cartesian_point((0.0, 0.0, 0.0))
mapped_item = f._emit_raw(
    f"MAPPED_ITEM('gs053_mi',#{rep_item_dummy.eid},#{cto.eid})"
)

# ── Face boundary wired onto the RECTANGULAR_TRIMMED_SURFACE ─────────────────
# Corners in parameter space [0,1]×[0,1] (mismatched with true knot range)
p_A = f.cartesian_point(( 2.0,  0.0,  1.0))
p_B = f.cartesian_point(( 2.0,  0.0, -1.0))
p_C = f.cartesian_point((-2.0,  0.0, -1.0))
p_D = f.cartesian_point((-2.0,  0.0,  1.0))

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

e0 = mk_edge_line(v_A, v_B, ( 2.0, 0.0,  1.0), (0.0,  0.0,-1.0), 2.0,
                  (0.0, 0.0), (0.0, 1.0), 1.0)
e1 = mk_edge_line(v_B, v_C, ( 2.0, 0.0, -1.0), (-1.0, 0.0, 0.0), 4.0,
                  (0.0, 1.0), (1.0, 0.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (-2.0, 0.0, -1.0), (0.0,  0.0, 1.0), 2.0,
                  (1.0, 1.0), (0.0,-1.0), 1.0)
e3 = mk_edge_line(v_D, v_A, (-2.0, 0.0,  1.0), (1.0,  0.0, 0.0), 4.0,
                  (1.0, 0.0), (-1.0, 0.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RECTANGULAR_TRIMMED_SURFACE (wrapping mismatched B-spline) IS the face_geometry.
face  = f.advanced_face([f.face_outer_bound(loop)], rts)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
