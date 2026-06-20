"""Tsh013 — Face has multiple outer wires (face needs splitting into disjoint regions).

Catalog claim: A single face carries two or more outer wires that enclose
disjoint regions of the supporting surface. The STEP spec requires exactly one
outer bound per face; this describes a multiply-connected region that should
have been emitted as multiple faces.

Mechanism IS the shell structure: a single ADVANCED_FACE on a plane has TWO
FACE_OUTER_BOUND entries pointing to two disjoint rectangular edge loops on the
same plane. The two outer bounds ARE wired directly into the face's bound list.
Strict receivers must split or reject; OCCT silently accepts.

Byte assertions:
  - count(b'FACE_OUTER_BOUND') >= 2
  - count_entity_def(b'ADVANCED_FACE') == 1

Tier-3 assertion: load == "ok"
live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh013",
    defect=(
        "Single ADVANCED_FACE on a plane with TWO FACE_OUTER_BOUND entries enclosing "
        "disjoint rectangular regions; STEP requires exactly one outer bound per face; "
        "two outer wires ARE wired into face topology; strict receivers must split or reject"
    ),
)

# ── Plane at z=0, normal (0,0,1) ─────────────────────────────────────────────
origin = f.cartesian_point((0.0, 0.0, 0.0))
ax = f.axis2_placement_3d(origin, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
pl = f.plane(ax)

# ── Outer loop 1: unit square [0..1] x [0..1] at z=0 ──────────────────────
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)

def mk_edge(va, vb, px, dx, dy):
    d = f.direction((dx, dy, 0.0))
    vec = f.vector(d, 1.0)
    ln = f.line(px, vec)
    return f.edge_curve(va, vb, ln)

e1_0 = mk_edge(v00, v10, p00,  1.0,  0.0)
e1_1 = mk_edge(v10, v11, p10,  0.0,  1.0)
e1_2 = mk_edge(v11, v01, p11, -1.0,  0.0)
e1_3 = mk_edge(v01, v00, p01,  0.0, -1.0)
lp1 = f.edge_loop([
    f.oriented_edge(e1_0, True), f.oriented_edge(e1_1, True),
    f.oriented_edge(e1_2, True), f.oriented_edge(e1_3, True),
])
fob1 = f.face_outer_bound(lp1)

# ── Outer loop 2: unit square [3..4] x [0..1] at z=0 (disjoint from loop 1) ─
p30 = f.cartesian_point((3.0, 0.0, 0.0))
p40 = f.cartesian_point((4.0, 0.0, 0.0))
p41 = f.cartesian_point((4.0, 1.0, 0.0))
p31 = f.cartesian_point((3.0, 1.0, 0.0))
v30 = f.vertex_point(p30); v40 = f.vertex_point(p40)
v41 = f.vertex_point(p41); v31 = f.vertex_point(p31)

e2_0 = mk_edge(v30, v40, p30,  1.0,  0.0)
e2_1 = mk_edge(v40, v41, p40,  0.0,  1.0)
e2_2 = mk_edge(v41, v31, p41, -1.0,  0.0)
e2_3 = mk_edge(v31, v30, p31,  0.0, -1.0)
lp2 = f.edge_loop([
    f.oriented_edge(e2_0, True), f.oriented_edge(e2_1, True),
    f.oriented_edge(e2_2, True), f.oriented_edge(e2_3, True),
])
fob2 = f.face_outer_bound(lp2)

# ── DEFECT: single ADVANCED_FACE with TWO FACE_OUTER_BOUNDs ──────────────────
# The spec requires exactly one outer bound; having two on one face IS the mechanism
# wired into the face topology. OCCT silently accepts; strict receivers must split.
face = f.advanced_face([fob1, fob2], pl, same_sense=True)

open_sh = f.open_shell([face])
sbsm = f.shell_based_surface_model([open_sh])
f.add_product_chain(sbsm)
