"""Gs009 — Self-intersecting / figure-eight EDGE_LOOP wire on planar face
(non-simple polygon).

Catalog claim: An EDGE_LOOP on a planar ADVANCED_FACE whose four LINE edges
visit corners in the order (0,0)→(10,10)→(10,0)→(0,10)→(0,0), crossing at
the centre — a figure-eight / non-simple polygon. Kernels that do not detect
self-intersection before meshing produce corrupt geometry.

OCC behavior: silently accepts (no diagnostic, empty result).
Expected: occt=empty. Closure intent: heal.

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry.
  - EDGE_LOOP contains 4 ORIENTED_EDGEs over 4 EDGE_CURVEs; vertices visit
    corners in crossing order: (0,0)→(10,10)→(10,0)→(0,10)→back to (0,0).
    The two diagonals (0,0)→(10,10) and (10,0)→(0,10) cross at (5,5,0).
    Byte assertions: contains(b'EDGE_LOOP('),
                     count_entity_def(b'ORIENTED_EDGE') == 4,
                     count_entity_def(b'EDGE_CURVE') == 4.
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: figure-eight EDGE_LOOP wire — four EDGE_CURVEs whose
    LINE segments self-intersect at centre — IS the wired boundary of the
    ADVANCED_FACE; PLANE IS the face_geometry; crossing wires drive
    shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs009",
    defect=(
        "EDGE_LOOP 4 edges visiting corners (0,0)→(10,10)→(10,0)→(0,10)→(0,0); "
        "figure-eight / non-simple polygon; diagonals cross at (5,5,0); "
        "PLANE IS ADVANCED_FACE.face_geometry; "
        "4 ORIENTED_EDGEs 4 EDGE_CURVEs; shape_null=True"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs009_ax',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs009_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Figure-eight wire: corners in crossing order ──────────────────────────────
# Vertex order:  A=(0,0,0) → B=(10,10,0) → C=(10,0,0) → D=(0,10,0) → back to A
# Edges: A→B (diagonal), B→C (right side), C→D (diagonal crosses A→B!), D→A (left side)
p_a = f.cartesian_point((0.0,  0.0, 0.0))
p_b = f.cartesian_point((10.0, 10.0, 0.0))
p_c = f.cartesian_point((10.0, 0.0,  0.0))
p_d = f.cartesian_point((0.0,  10.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

def mk_plane_edge(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e  = f.cartesian_point(p3_start)
    d3e  = f.direction(d3t)
    v3e  = f.vector(d3e, p3_len)
    l3e  = f.line(p3e, v3e)
    p2e  = f.cartesian_point(p2_start)
    d2e  = f.direction(d2t)
    v2e  = f.vector(d2e, p2_len)
    l2e  = f.line(p2e, v2e)
    pcd  = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc   = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

import math
diag_len = math.sqrt(200.0)  # ||(10,10)|| = 10√2 ≈ 14.142

# Edge 0: A(0,0)→B(10,10) — first diagonal
e0 = mk_plane_edge(v_a, v_b,
    (0.0, 0.0, 0.0),  (1.0, 1.0, 0.0),   diag_len,
    (0.0, 0.0),       (1.0, 1.0),          diag_len)

# Edge 1: B(10,10)→C(10,0) — right vertical, going down
e1 = mk_plane_edge(v_b, v_c,
    (10.0, 10.0, 0.0), (0.0, -1.0, 0.0), 10.0,
    (10.0, 10.0),      (0.0, -1.0),       10.0)

# Edge 2: C(10,0)→D(0,10) — second diagonal (CROSSES e0 at (5,5))
e2 = mk_plane_edge(v_c, v_d,
    (10.0, 0.0, 0.0),  (-1.0, 1.0, 0.0),  diag_len,
    (10.0, 0.0),       (-1.0, 1.0),         diag_len)

# Edge 3: D(0,10)→A(0,0) — left vertical, going down
e3 = mk_plane_edge(v_d, v_a,
    (0.0, 10.0, 0.0),  (0.0, -1.0, 0.0), 10.0,
    (0.0, 10.0),       (0.0, -1.0),       10.0)

# EDGE_LOOP with 4 ORIENTED_EDGEs over 4 EDGE_CURVEs — figure-eight wire IS the defect.
loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# PLANE IS the face_geometry — wired into the face topology.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
