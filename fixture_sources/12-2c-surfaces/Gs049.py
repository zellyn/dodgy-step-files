"""Gs049 — B-spline surface has C0 isoparametric line that triggers split-on-import.

Catalog claim: A B_SPLINE_SURFACE_WITH_KNOTS face of degree 2 with U knot
vector (0,0,0, 0.5,0.5,0.5, 1,1,1) — multiplicities (3,3,3) at knot values
(0.0,0.5,1.0). The interior knot at U=0.5 has multiplicity equal to degree+1
(=3), creating a C0 isoparametric line (kink across the entire U=0.5 isoline).
Meshing/Boolean tools that assume C1+ produce wrong tangent normals.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (degree 2 in U, interior knot multiplicity 3 at U=0.5)
    IS the ADVANCED_FACE.face_geometry; C0 isoparametric line IS the defect wired
    into face topology.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS('),
                     contains(b'(3,3,3)'),
                     contains(b'(0.0,0.5,1.0)').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS IS the ADVANCED_FACE.face_geometry;
    U knot multiplicities (3,3,3) at (0.0,0.5,1.0) on degree-2 surface — interior
    multiplicity=degree+1 creates C0 kink — IS the defect wired into face topology.
  - shape_null driver: C0 isoparametric line; strict heal-or-reject kernels require
    split-on-import and produce empty/null shape without healing.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs049",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (degree 2 in U, V) IS ADVANCED_FACE.face_geometry; "
        "U knot multiplicities (3,3,3) at (0.0,0.5,1.0) — interior multiplicity equals "
        "degree+1 creates C0 isoparametric kink at U=0.5 — IS wired into face topology; "
        "shape(1) (live OCC heals)"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: the defect surface ───────────────────────────
# Degree 2 in U and V. U knot vector: (0,0,0, 0.5,0.5,0.5, 1,1,1) → mults (3,3,3).
# For degree d=2, mult=3=d+1 at interior knot → C0 isoline (kink).
# Control net: (n_u+1) x (n_v+1) where:
#   n_u+1 = sum(u_mults) - d_u - 1 = 9 - 2 - 1 = 6 (columns)
#   n_v+1 = sum(v_mults) - d_v - 1; use simple V with 1 span: (3,3) → 3+3-2-1=3 rows
# So 6x3 = 18 control points.
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS(')
# Byte assertion: contains(b'(3,3,3)')
# Byte assertion: contains(b'(0.0,0.5,1.0)')

# Row 0 (V=0)
r0c0 = f.cartesian_point((0.0, 0.0, 0.0))
r0c1 = f.cartesian_point((1.0, 0.0, 0.0))
r0c2 = f.cartesian_point((2.0, 0.0, 0.0))
r0c3 = f.cartesian_point((2.0, 0.0, 0.0))   # C0 at U=0.5: same x but will have kink in tangent
r0c4 = f.cartesian_point((3.0, 0.0, 0.0))
r0c5 = f.cartesian_point((4.0, 0.0, 0.0))

# Row 1 (V=0.5)
r1c0 = f.cartesian_point((0.0, 2.0, 0.0))
r1c1 = f.cartesian_point((1.0, 2.0, 0.0))
r1c2 = f.cartesian_point((2.0, 2.0, 1.0))   # bump — kink will appear at U=0.5
r1c3 = f.cartesian_point((2.0, 2.0,-1.0))   # tangent flip at C0 line
r1c4 = f.cartesian_point((3.0, 2.0, 0.0))
r1c5 = f.cartesian_point((4.0, 2.0, 0.0))

# Row 2 (V=1)
r2c0 = f.cartesian_point((0.0, 4.0, 0.0))
r2c1 = f.cartesian_point((1.0, 4.0, 0.0))
r2c2 = f.cartesian_point((2.0, 4.0, 0.0))
r2c3 = f.cartesian_point((2.0, 4.0, 0.0))
r2c4 = f.cartesian_point((3.0, 4.0, 0.0))
r2c5 = f.cartesian_point((4.0, 4.0, 0.0))

# B_SPLINE_SURFACE_WITH_KNOTS(
#   name, u_degree, v_degree,
#   control_points_list,
#   surface_form, u_closed, v_closed, self_intersect,
#   u_multiplicities, v_multiplicities,
#   u_knots, v_knots,
#   knot_spec)
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs049_bss',2,2,"
    f"((#{r0c0.eid},#{r0c1.eid},#{r0c2.eid},#{r0c3.eid},#{r0c4.eid},#{r0c5.eid}),"
    f"(#{r1c0.eid},#{r1c1.eid},#{r1c2.eid},#{r1c3.eid},#{r1c4.eid},#{r1c5.eid}),"
    f"(#{r2c0.eid},#{r2c1.eid},#{r2c2.eid},#{r2c3.eid},#{r2c4.eid},#{r2c5.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3,3),(3,3),"
    f"(0.0,0.5,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the C0-kink B-spline surface ─────────────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((4.0, 0.0, 0.0))
p_C = f.cartesian_point((4.0, 4.0, 0.0))
p_D = f.cartesian_point((0.0, 4.0, 0.0))

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

e0 = mk_edge_line(v_A, v_B, (0.0,0.0,0.0), (1.0,0.0,0.0), 4.0, (0.0,0.0), (1.0,0.0), 1.0)
e1 = mk_edge_line(v_B, v_C, (4.0,0.0,0.0), (0.0,1.0,0.0), 4.0, (1.0,0.0), (0.0,1.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (4.0,4.0,0.0), (-1.0,0.0,0.0), 4.0, (1.0,1.0), (-1.0,0.0), 1.0)
e3 = mk_edge_line(v_D, v_A, (0.0,4.0,0.0), (0.0,-1.0,0.0), 4.0, (0.0,1.0), (0.0,-1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS (C0 kink) IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
