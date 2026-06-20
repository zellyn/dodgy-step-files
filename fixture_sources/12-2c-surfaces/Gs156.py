"""Gs156 — EditVertex ordering corruption on CYLINDRICAL_SURFACE.

Catalog claim: ShapeExtend_WireData::EditVertex() corrupts edge-to-vertex
connectivity during in-place reorder of a multi-edge wire. When two edges
share a vertex and EditVertex reorders their connectivity, the resulting
EDGE_LOOP breaks the CLOSED_SHELL invariant: one or more vertices are
referenced by a non-adjacent oriented edge, producing an open wire that
strict kernels reject.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE (radius 1.5) IS the ADVANCED_FACE.face_geometry;
    face boundary EDGE_LOOP with shared-vertex edges whose connectivity has
    been reordered (start vertex of edge N+1 != end vertex of edge N) IS the
    mechanism wired into face topology; EditVertex in-place reorder corrupting
    edge-to-vertex connectivity IS the defect.
  - Byte assertions: contains(b'CYLINDRICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE IS ADVANCED_FACE.face_geometry;
    face boundary EDGE_LOOP with vertex-connectivity break (shared vertex
    misassigned after in-place reorder) IS the mechanism wired into face
    topology; EditVertex ordering corruption IS the defect.
  - shape_null driver: wire closure invariant violated; EDGE_LOOP open;
    strict kernels reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs156",
    defect=(
        "CYLINDRICAL_SURFACE (radius 1.5) IS ADVANCED_FACE.face_geometry; "
        "face boundary EDGE_LOOP with shared-vertex connectivity break (end "
        "vertex of edge N != start vertex of edge N+1 after reorder) IS the "
        "mechanism wired into face topology; EditVertex in-place ordering "
        "corruption of edge-to-vertex connectivity IS the defect; shape_null"
    ),
)

# ── CYLINDRICAL_SURFACE: radius 1.5, axis along Z ──────────────────────────────
# Byte assertion: contains(b'CYLINDRICAL_SURFACE')
# The face boundary EDGE_LOOP encodes a vertex-connectivity break that
# EditVertex produces during in-place reorder: edge N's end vertex ID and
# edge N+1's start vertex ID differ despite sharing the same 3D location.
# This mimics the post-EditVertex corrupted wire state.
RADIUS = 1.5
TWO_PI = 2.0 * math.pi

cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs156_cyl_ax',#{cyl_orig.eid},#{cyl_zdir.eid},#{cyl_xdir.eid})"
)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('gs156_cyl',#{cyl_ax.eid},{RADIUS})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary with corrupted vertex connectivity ─────────────────────────
# CYLINDRICAL_SURFACE: x = r*cos(u), y = r*sin(u), z = v.
# Face: u in [0, pi/2], v in [0, 1.0].
# Normally edge sequence: e0(A→B), e1(B→C), e2(C→D), e3(D→A).
# Post-EditVertex corruption: the shared vertex at the A↔B join uses two
# *separate* vertex entities at the same 3D location — v_B_end and v_B_start —
# breaking the EDGE_LOOP closure invariant. Edge e0 ends at v_B_end; edge e1
# starts at v_B_start (same point, different entity). This is the corrupted
# connectivity that EditVertex produces and that strict kernels reject.
U_END = math.pi / 2.0
V_TOP = 1.0

def cyl_pt(u, v):
    return (RADIUS * math.cos(u), RADIUS * math.sin(u), v)

A3  = cyl_pt(0.0, 0.0)
B3  = cyl_pt(U_END, 0.0)
C3  = cyl_pt(U_END, V_TOP)
D3  = cyl_pt(0.0, V_TOP)

p_A       = f.cartesian_point(A3)
# Corruption: two vertices at same location for the A↔(e0_end)/(e3_start) join
p_A_end   = f.cartesian_point(A3)   # same 3D point as p_A — separate entity
p_B       = f.cartesian_point(B3)
p_C       = f.cartesian_point(C3)
p_D       = f.cartesian_point(D3)

v_A       = f.vertex_point(p_A)
v_A_end   = f.vertex_point(p_A_end)  # duplicate vertex — connectivity break
v_B       = f.vertex_point(p_B)
v_C       = f.vertex_point(p_C)
v_D       = f.vertex_point(p_D)

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
    pc  = f._emit_raw(f"PCURVE('pc',#{cyl.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

arc_len = RADIUS * U_END

# e0: A→B (normal start vertex, normal end)
e0 = mk_edge_line(v_A, v_B,
                  A3, (B3[0]-A3[0], B3[1]-A3[1], 0.0), arc_len,
                  (0.0, 0.0), (1.0, 0.0), U_END)
# e1: B→C
e1 = mk_edge_line(v_B, v_C,
                  B3, (0.0, 0.0, 1.0), V_TOP,
                  (U_END, 0.0), (0.0, 1.0), V_TOP)
# e2: C→D
e2 = mk_edge_line(v_C, v_D,
                  C3, (D3[0]-C3[0], D3[1]-C3[1], 0.0), arc_len,
                  (U_END, V_TOP), (-1.0, 0.0), U_END)
# e3: D→v_A_end — end vertex is a DUPLICATE of v_A (different entity, same 3D)
# This is the corruption: e3 closes to v_A_end, not v_A, so e0.start != e3.end
# The EDGE_LOOP is topologically open despite sharing the same 3D position.
e3 = mk_edge_line(v_D, v_A_end,
                  D3, (A3[0]-D3[0], A3[1]-D3[1], 0.0), V_TOP,
                  (0.0, V_TOP), (0.0, -1.0), V_TOP)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CYLINDRICAL_SURFACE IS the face_geometry; face boundary EDGE_LOOP with
# vertex-connectivity break (e3 ends at v_A_end != e0's start v_A, same 3D
# point but distinct entities) IS the mechanism wired into face topology —
# exercises EditVertex in-place ordering corruption of edge-to-vertex
# connectivity.
face  = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
