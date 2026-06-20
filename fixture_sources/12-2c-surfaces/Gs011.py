"""Gs011 — Crossed-trim EDGE_LOOP with non-shared diagonals
(mesh-derived BRep, STL→STEP).

Catalog claim: A mesh-to-BRep utility (e.g. FreeCAD Part/Create shape from
mesh) emits an ADVANCED_FACE whose EDGE_LOOP contains exactly two EDGE_CURVEs
running as diagonals of a quad: one from (0,0)→(10,10) and another from
(0,10)→(10,0). The two diagonals cross in UV at the centre and do not share
endpoints; the wire loop is two disjoint crossed diagonals. Every subsequent
Boolean operation fails.

OCC behavior: silently accepts (no diagnostic, empty result).
Expected: occt=empty. Closure intent: ambiguous (heal or reject).

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (bilinear, 2×2 control net) IS the
    ADVANCED_FACE.face_geometry.
  - EDGE_LOOP contains exactly 2 ORIENTED_EDGEs over 2 EDGE_CURVEs:
      EDGE_CURVE 0: (0,0,0)→(10,10,0) — diagonal 1
      EDGE_CURVE 1: (0,10,0)→(10,0,0) — diagonal 2 (crosses diagonal 1 at (5,5,0))
    The two EDGEs do not share vertex endpoints; loop is malformed (non-closed).
    Each EDGE_CURVE 3D curve IS the curve_3d of its SURFACE_CURVE.
    Byte assertions: contains(b'EDGE_LOOP('),
                     count_entity_def(b'ORIENTED_EDGE') == 2,
                     count_entity_def(b'EDGE_CURVE') == 2.
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: two crossed-diagonal EDGE_CURVEs — defect 3D LINEs ARE
    the curve_3d of SURFACE_CURVEs in the EDGE_CURVE entities — form an
    EDGE_LOOP with 2 ORIENTED_EDGEs whose diagonals cross at (5,5,0) and share
    no endpoints; B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry; crossed
    non-shared diagonals drive shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs011",
    defect=(
        "EDGE_LOOP 2 edges: diagonal (0,0,0)→(10,10,0) and diagonal "
        "(0,10,0)→(10,0,0); cross at (5,5,0), no shared endpoints; "
        "crossed-trim STL→BRep wire; B_SPLINE_SURFACE_WITH_KNOTS IS "
        "ADVANCED_FACE.face_geometry; 2 ORIENTED_EDGEs 2 EDGE_CURVEs; "
        "shape_null=True"
    ),
)

# ── CATALOG MECHANISM: bilinear BSpline surface as face_geometry ──────────────
# Degree 1×1, 2×2 control net, clamped (2,2)×(2,2) knots.
# Surface covers a 10×10 quad in XY at Z=0.
def cp(x, y, z=0.0):
    return f.cartesian_point((x, y, z))

r0 = [cp(0.0,  0.0),  cp(0.0,  10.0)]
r1 = [cp(10.0, 0.0),  cp(10.0, 10.0)]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)})"

surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs011_bilinear',1,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Crossed diagonal EDGE_CURVEs ──────────────────────────────────────────────
# Diagonal 1: (0,0,0) → (10,10,0)
# Diagonal 2: (0,10,0) → (10,0,0)   ← crosses diagonal 1 at (5,5,0), no shared vertex
diag_len = math.sqrt(200.0)  # 10√2

p_00  = f.cartesian_point((0.0,  0.0,  0.0))
p_1010 = f.cartesian_point((10.0, 10.0, 0.0))
p_010 = f.cartesian_point((0.0,  10.0, 0.0))
p_100 = f.cartesian_point((10.0, 0.0,  0.0))

v_00   = f.vertex_point(p_00)
v_1010 = f.vertex_point(p_1010)
v_010  = f.vertex_point(p_010)
v_100  = f.vertex_point(p_100)

def mk_diag_edge(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    """Make an EDGE_CURVE with SURFACE_CURVE (3D line + pcurve) on surf."""
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)       # 3D LINE IS the defect curve_3d
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

# Edge 0: diagonal (0,0,0)→(10,10,0); UV: (0,0)→(1,1)
e0 = mk_diag_edge(v_00, v_1010,
    (0.0, 0.0, 0.0),  (1.0, 1.0, 0.0),  diag_len,
    (0.0, 0.0),       (1.0, 1.0),         math.sqrt(2.0))

# Edge 1: diagonal (0,10,0)→(10,0,0); UV: (0,1)→(1,0) — CROSSES e0 at (5,5,0)
e1 = mk_diag_edge(v_010, v_100,
    (0.0, 10.0, 0.0), (1.0, -1.0, 0.0), diag_len,
    (0.0, 1.0),       (1.0, -1.0),        math.sqrt(2.0))

# EDGE_LOOP with exactly 2 ORIENTED_EDGEs — crossed, non-shared-endpoint diagonals.
loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
