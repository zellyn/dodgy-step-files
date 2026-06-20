"""Gs034 — Twisted / pinched face: EDGE_LOOP revisits a shared vertex (Möbius-cell pathology).

Catalog claim: An EDGE_LOOP that visits the same VERTEX_POINT more than once
produces a pinched face (figure-eight: shared vertex visited twice by outer wire).
Kernel must split the pinched face or reject as malformed.

OCC behavior: silently accepts, empty result. live oracle: occt=shape(1)/shape(1).

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry.
  - EDGE_LOOP visits the centre vertex (5,5,0) TWICE — forming a figure-eight
    topology where the outer wire self-touches at that centre point.
  - 6 ORIENTED_EDGEs in the loop (3 for each lobe of the figure-eight).
  - Byte assertions: count_entity_def(b'ORIENTED_EDGE') == 6,
                     contains(b'(5.0,5.0,0.0)').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry; the defect
    EDGE_LOOP IS the face boundary wired into face topology; the loop revisits
    the centre vertex at (5,5,0) twice (figure-eight pinch); pinched wire IS the
    defect wired into the face.
  - shape_null driver: pinched self-touching wire cannot be healed without
    splitting; strict reject-or-heal kernels produce null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs034",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; defect EDGE_LOOP IS face boundary; "
        "loop visits centre vertex (5.0,5.0,0.0) twice (figure-eight pinch); "
        "count_entity_def(ORIENTED_EDGE)==6; shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs034_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs034_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Figure-eight topology: 5 vertices, centre visited twice ──────────────────
# Left lobe: corners at (0,5), (5,0), (5,5=centre), back to (5,5=centre)→(0,5)
#   Vertices: A=(0,5,0), B=(5,0,0), C=(5,5,0)[centre], back A
# Right lobe: C=(5,5,0)[centre], D=(10,0,0), E=(10,5,0), back C
# EDGE_LOOP: A→B, B→C, C→A, then A→... wait — figure-eight from centre:
#   Better: centre vertex M=(5,5,0) visited twice.
#   Left triangle: M→A→B→M  (3 edges)
#   Right triangle: M→C→D→M (3 edges)
#   Wire: M→A, A→B, B→M, M→C, C→D, D→M → 6 oriented edges.

p_M = f.cartesian_point((5.0,  5.0, 0.0))   # byte assertion: (5.0,5.0,0.0)
p_A = f.cartesian_point((0.0,  5.0, 0.0))
p_B = f.cartesian_point((5.0,  0.0, 0.0))
p_C = f.cartesian_point((10.0, 5.0, 0.0))
p_D = f.cartesian_point((5.0, 10.0, 0.0))

v_M = f.vertex_point(p_M)   # shared centre vertex — visited twice
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
    pc  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Left lobe: M→A, A→B, B→M
e_MA = mk_edge_line(v_M, v_A, (5.0,5.0,0.0), (-1.0,0.0,0.0), 5.0,  (5.0,5.0), (-1.0,0.0), 5.0)
e_AB = mk_edge_line(v_A, v_B, (0.0,5.0,0.0), (1.0,-1.0,0.0), 7.07, (0.0,5.0), (1.0,-1.0), 7.07)
e_BM = mk_edge_line(v_B, v_M, (5.0,0.0,0.0), (0.0,1.0,0.0),  5.0,  (5.0,0.0), (0.0,1.0),  5.0)

# Right lobe: M→C, C→D, D→M
e_MC = mk_edge_line(v_M, v_C, (5.0,5.0,0.0), (1.0,0.0,0.0),  5.0,  (5.0,5.0), (1.0,0.0),  5.0)
e_CD = mk_edge_line(v_C, v_D, (10.0,5.0,0.0),(-1.0,1.0,0.0), 7.07, (10.0,5.0),(-1.0,1.0), 7.07)
e_DM = mk_edge_line(v_D, v_M, (5.0,10.0,0.0),(0.0,-1.0,0.0), 5.0,  (5.0,10.0),(0.0,-1.0), 5.0)

# EDGE_LOOP with 6 ORIENTED_EDGEs (byte assertion: count_entity_def(ORIENTED_EDGE)==6).
# The loop visits v_M at positions 1 and 4 — the pinch IS the defect wired into topology.
loop = f.edge_loop([
    f.oriented_edge(e_MA, True),
    f.oriented_edge(e_AB, True),
    f.oriented_edge(e_BM, True),
    f.oriented_edge(e_MC, True),
    f.oriented_edge(e_CD, True),
    f.oriented_edge(e_DM, True),
])

# PLANE IS the face_geometry; defect EDGE_LOOP IS the face boundary.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
