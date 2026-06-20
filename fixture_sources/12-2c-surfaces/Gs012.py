"""Gs012 — Non-simple EDGE_LOOP (face boundary self-crosses in UV: bow-tie quadrilateral).

Catalog claim: A face's outer EDGE_LOOP has four segments whose pcurves form a
bow-tie / self-crossing quadrilateral in UV parameter space: two diagonal edges
((0,0)→(10,10) and (10,0)→(0,10)) interleaved with axial edges so the UV
contour crosses itself at (5,5). 3D positions look fine but the loop violates
the Jordan-curve theorem; CADfix needs a dedicated repair flow.

OCC behavior: silently accepts (no diagnostic, empty result).
Expected: occt=empty. Closure intent: reject.

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry (byte assertion contains(b'PLANE(')).
  - EDGE_LOOP contains exactly 4 ORIENTED_EDGEs over 4 EDGE_CURVEs whose
    pcurves form a bow-tie in the face UV plane:
      E0: (0,0,0)→(10,10,0), UV (0,0)→(10,10)  — diagonal 1
      E1: (10,0,0)→(0,10,0), UV (10,0)→(0,10)  — diagonal 2 (crosses E0 at (5,5))
      E2: (0,10,0)→(0,0,0),  UV (0,10)→(0,0)   — left edge
      E3: (10,10,0)→(10,0,0),UV (10,10)→(10,0) — right edge
    The two diagonals cross in UV; the loop is non-simple (Jordan-curve violation).
  - Byte assertions: contains(b'EDGE_LOOP('),
                     count_entity_def(b'ORIENTED_EDGE') == 4,
                     contains(b'PLANE(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry; the four
    EDGE_CURVE 3D LINEs ARE the curve_3d of SURFACE_CURVEs whose PCURVE LINEs
    form a bow-tie (self-crossing) EDGE_LOOP in UV; Jordan-curve violation drives
    shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs012",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; 4-edge EDGE_LOOP whose PCURVE "
        "LINEs form a bow-tie in UV: diagonals (0,0)→(10,10) and (10,0)→(0,10) "
        "cross at UV (5,5); Jordan-curve violation; count_entity_def(ORIENTED_EDGE)==4; "
        "shape_null=True"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs012_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs012_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# 3D vertices
p_00   = f.cartesian_point((0.0,  0.0,  0.0))
p_1010 = f.cartesian_point((10.0, 10.0, 0.0))
p_100  = f.cartesian_point((10.0, 0.0,  0.0))
p_010  = f.cartesian_point((0.0,  10.0, 0.0))

v_00   = f.vertex_point(p_00)
v_1010 = f.vertex_point(p_1010)
v_100  = f.vertex_point(p_100)
v_010  = f.vertex_point(p_010)

diag_len = math.sqrt(200.0)  # 10√2

def mk_edge(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    """EDGE_CURVE with SURFACE_CURVE (3D LINE + PCURVE) on the plane."""
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)         # 3D LINE IS the defect curve_3d
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

# E0: diagonal (0,0,0)→(10,10,0); UV (0,0)→(10,10)
e0 = mk_edge(v_00, v_1010,
    (0.0, 0.0, 0.0),   (1.0, 1.0, 0.0),   diag_len,
    (0.0, 0.0),        (1.0, 1.0),          diag_len)

# E1: diagonal (10,0,0)→(0,10,0); UV (10,0)→(0,10) — crosses E0 at UV (5,5)
e1 = mk_edge(v_100, v_010,
    (10.0, 0.0, 0.0),  (-1.0, 1.0, 0.0),  diag_len,
    (10.0, 0.0),       (-1.0, 1.0),         diag_len)

# E2: left edge (0,10,0)→(0,0,0); UV (0,10)→(0,0)
e2 = mk_edge(v_010, v_00,
    (0.0, 10.0, 0.0),  (0.0, -1.0, 0.0),  10.0,
    (0.0, 10.0),       (0.0, -1.0),         10.0)

# E3: right edge (10,10,0)→(10,0,0); UV (10,10)→(10,0)
e3 = mk_edge(v_1010, v_100,
    (10.0, 10.0, 0.0), (0.0, -1.0, 0.0),  10.0,
    (10.0, 10.0),      (0.0, -1.0),         10.0)

# EDGE_LOOP with 4 ORIENTED_EDGEs — bow-tie UV contour, non-simple
loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# PLANE IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
