"""Bo006 — One edge is shared by three or more faces in a 2-manifold shell.

Catalog claim: A single EDGE_CURVE is referenced by ORIENTED_EDGEs belonging
to three distinct faces of one shell (non-manifold T-junction).

Mechanism IS the CLOSED_SHELL edge/face topology: one EDGE_CURVE IS referenced
by three face edge loops inside a single CLOSED_SHELL. The triple-incident edge
IS wired into the shell's face structure. BRepCheck_Edge fires
InvalidMultiConnexity.

Tier-3 assertions: face[0].surface_type == "plane", face[2].surface_type == "plane"
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo006",
    defect=(
        "CLOSED_SHELL contains one EDGE_CURVE referenced by 3 face EDGE_LOOPs "
        "(T-junction non-manifold); triple-incident edge IS wired into "
        "closed-shell face/edge topology; BRepCheck fires InvalidMultiConnexity"
    ),
)

# ── Shared plane ──────────────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
# Layout: two unit squares side by side (A left, B right) plus a third square C
# hanging below the shared vertical edge between A and B.
#
#   (0,1)---(1,1)---(2,1)
#     |       |       |
#     |   A   | B     |
#     |       |       |
#   (0,0)---(1,0)---(2,0)
#             |
#             |  C (below)
#             |
#           (1,-1)-(2,-1)

pA0 = f.cartesian_point((0.0,  0.0, 0.0)); pA1 = f.cartesian_point((1.0,  0.0, 0.0))
pA2 = f.cartesian_point((1.0,  1.0, 0.0)); pA3 = f.cartesian_point((0.0,  1.0, 0.0))
pB1 = f.cartesian_point((2.0,  0.0, 0.0)); pB2 = f.cartesian_point((2.0,  1.0, 0.0))
pC0 = f.cartesian_point((1.0, -1.0, 0.0)); pC1 = f.cartesian_point((2.0, -1.0, 0.0))

vA0 = f.vertex_point(pA0); vA1 = f.vertex_point(pA1)
vA2 = f.vertex_point(pA2); vA3 = f.vertex_point(pA3)
vB1 = f.vertex_point(pB1); vB2 = f.vertex_point(pB2)
vC0 = f.vertex_point(pC0); vC1 = f.vertex_point(pC1)

def mk_edge(va, vb, p_start, dx, dy, length):
    d = f.direction((dx, dy, 0.0)); v = f.vector(d, length)
    return f.edge_curve(va, vb, f.line(p_start, v))

# ── CATALOG MECHANISM: shared_edge shared by ALL THREE faces ──────────────────
# This EDGE_CURVE (the vertical boundary at x=1 between y=0 and y=1) is the
# non-manifold edge — it appears in loops of A, B, and C.
shared_edge = mk_edge(vA1, vA2, pA1, 0, 1, 1.0)

# Face A edges
eA_bot = mk_edge(vA0, vA1, pA0,  1,  0, 1.0)
eA_top = mk_edge(vA2, vA3, pA2, -1,  0, 1.0)
eA_lft = mk_edge(vA3, vA0, pA3,  0, -1, 1.0)

# Face B edges
eB_bot = mk_edge(vA1, vB1, pA1,  1,  0, 1.0)
eB_rgt = mk_edge(vB1, vB2, pB1,  0,  1, 1.0)
eB_top = mk_edge(vB2, vA2, pB2, -1,  0, 1.0)

# Face C edges
eC_bot = mk_edge(vC0, vC1, pC0,  1,  0, 1.0)
eC_rgt = mk_edge(vC1, vB1, pC1,  0,  1, 1.0)
eC_lft = mk_edge(vA1, vC0, pA1,  0, -1, 1.0)

# ── Edge loops — shared_edge used in all three loops ─────────────────────────
loopA = f.edge_loop([
    f.oriented_edge(eA_bot, True),
    f.oriented_edge(shared_edge, True),   # ← 1st use
    f.oriented_edge(eA_top, True),
    f.oriented_edge(eA_lft, True),
])
loopB = f.edge_loop([
    f.oriented_edge(eB_bot, True),
    f.oriented_edge(eB_rgt, True),
    f.oriented_edge(eB_top, True),
    f.oriented_edge(shared_edge, False),  # ← 2nd use (reversed)
])
loopC = f.edge_loop([
    f.oriented_edge(eC_lft, True),
    f.oriented_edge(eC_bot, True),
    f.oriented_edge(eC_rgt, True),
    f.oriented_edge(shared_edge, False),  # ← 3rd use — T-junction!
])

faceA = f.advanced_face([f.face_outer_bound(loopA)], plane)
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane)
faceC = f.advanced_face([f.face_outer_bound(loopC)], plane)

# Wrap in CLOSED_SHELL — the triple-incident edge is the non-manifold defect
face_refs = f"#{faceA.eid},#{faceB.eid},#{faceC.eid}"
shell = f._emit_raw(f"CLOSED_SHELL('bo006_nonmanifold',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('bo006_solid',#{shell.eid})")

f.add_product_chain(msb, mode="brep_shape")
