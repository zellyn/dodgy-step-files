"""Gs118 — B-spline surface with zero-span knot interval (identical adjacent knots at non-end).

Catalog claim: B_SPLINE_SURFACE_WITH_KNOTS where two interior knot values are
identical (zero-span interval) without exceeding the degree multiplicity limit —
the values simply repeat when they should be distinct. OCCT's ShapeFix_Surface
silently processes the zero-span interval without detecting the degenerate
parameterization.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (degree=2, u-knots with consecutive interior
    values 0.5, 0.5 in the flat knot sequence yielding a zero-length parametric
    span between two distinct knot entries) IS the ADVANCED_FACE.face_geometry;
    zero-span interior interval IS the mechanism wired into face topology;
    ShapeFix_Surface silent processing without span-length validation IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (degree=2, zero-span interior
    interval at u=0.5 from two consecutive equal knot-value entries) IS the
    ADVANCED_FACE.face_geometry; zero-span knot interval IS the mechanism wired
    into face topology; ShapeFix_Surface silent acceptance IS the defect.
  - shape_null driver: degenerate zero-span parameterization; strict kernels
    reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs118",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (degree=2, zero-span interior interval "
        "at u=0.5 from duplicate knot-value entries) "
        "IS ADVANCED_FACE.face_geometry; "
        "zero-span interior knot interval IS the mechanism wired into face topology; "
        "ShapeFix_Surface silent acceptance without span-length check IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: degree=2, zero-span interior interval ────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# degree=2 in u; 5 poles → sum_mults = 5+2+1 = 8.
# Knot values: (0.0, 0.5, 0.5, 1.0) — the flat list has 0.5 appearing twice
# as separate knot *entries* each with mult=1, giving zero span between them.
# mults=(3,1,1,3) → sum=8 ✓; but knot values (0.0,0.5,0.5,1.0) have duplicate.
ctrl = [
    [(0.0,0.0,0.0),(0.25,0.0,0.0),(0.5,0.0,0.0),(0.75,0.0,0.0),(1.0,0.0,0.0)],
    [(0.0,1.0,0.0),(0.25,1.0,0.0),(0.5,1.0,0.0),(0.75,1.0,0.0),(1.0,1.0,0.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(5)) + ")"
    for r in range(2)
) + ")"

# mults=(3,1,1,3)=8 for 5 poles degree=2; knot values (0.0,0.5,0.5,1.0)
# → adjacent distinct entries both = 0.5 → zero-span interior interval.
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs118_bss',2,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,1,1,3),(2,2),"
    f"(0.0,0.5,0.5,1.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square in parameter space ─────────────────────────────
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

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS (zero-span interior interval) IS the face_geometry;
# duplicate adjacent knot values IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
