"""Tsh011 — `FACE_OUTER_BOUND` orientation flag inconsistent with required winding.

Catalog claim: An EDGE_LOOP's ORIENTED_EDGE.orientation flags are inconsistent
with the geometric winding required by the face's outward normal; the outer
wire winds the wrong way (one ORIENTED_EDGE has .F. when geometrically .T. is
required for outward winding).

Mechanism IS the shell structure: a single planar ADVANCED_FACE has a square
outer wire (FACE_OUTER_BOUND) and a small square hole (FACE_BOUND).  One
ORIENTED_EDGE in the outer loop has orientation=False (.F.) when the correct
outward winding for the face normal requires True (.T.) — this breaks the CCW
winding for the outer boundary.  The flag inconsistency IS wired directly into
the face/wire/edge topology.

Byte assertions:
  - contains(b'FACE_OUTER_BOUND')
  - contains(b'FACE_BOUND')
  - count_entity_def(b'ADVANCED_FACE') == 1

Tier-3 assertion: n_faces_total == 1
live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh011",
    defect=(
        "Single ADVANCED_FACE (planar, with hole): one ORIENTED_EDGE in FACE_OUTER_BOUND "
        "loop has orientation=False (.F.) when outward winding requires True (.T.); "
        "outer wire winds the wrong way; inconsistency IS wired into face/wire/edge "
        "topology; strict receivers must propagate from face normal or reject"
    ),
)

# ── Single planar face: 3x3 square outer boundary, 1x1 hole ───────────────────
# Outer wire: vertices at (0,0), (3,0), (3,3), (0,3) — CCW from +z normal
# but DEFECT: one ORIENTED_EDGE flipped to orientation=False breaks the winding.
# Hole wire: vertices at (1,1), (2,1), (2,2), (1,2) — CW (inward) as expected.

def pt2(x, y):
    return f.cartesian_point((float(x), float(y), 0.0))

def line_edge(va, vb, pstart, dx, dy, dz=0.0):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# Outer boundary vertices — 3x3 square on z=0 plane
po00 = pt2(0,0); po30 = pt2(3,0); po33 = pt2(3,3); po03 = pt2(0,3)
vo00 = f.vertex_point(po00); vo30 = f.vertex_point(po30)
vo33 = f.vertex_point(po33); vo03 = f.vertex_point(po03)

# Outer wire edges: 00→30→33→03→00 (CCW from +z)
eo0 = line_edge(vo00, vo30, po00,  1, 0)   # bottom edge going right
eo1 = line_edge(vo30, vo33, po30,  0, 1)   # right edge going up
eo2 = line_edge(vo33, vo03, po33, -1, 0)   # top edge going left
eo3 = line_edge(vo03, vo00, po03,  0,-1)   # left edge going down

# DEFECT: eo1 (right edge, vo30→vo33) uses orientation=False — flips this edge
# direction from its underlying edge_curve parameter direction.
# Correct winding needs all True; the False here IS the inconsistency.
lp_outer = f.edge_loop([
    f.oriented_edge(eo0, True),    # correct: bottom goes right (CCW)
    f.oriented_edge(eo1, False),   # DEFECT: .F. breaks the CCW winding requirement
    f.oriented_edge(eo2, True),    # correct: top goes left
    f.oriented_edge(eo3, True),    # correct: left goes down
])
fob = f.face_outer_bound(lp_outer, orientation=True)

# Inner hole vertices — 1x1 square (CW from +z for hole, as required by spec)
ph11 = pt2(1,1); ph21 = pt2(2,1); ph22 = pt2(2,2); ph12 = pt2(1,2)
vh11 = f.vertex_point(ph11); vh21 = f.vertex_point(ph21)
vh22 = f.vertex_point(ph22); vh12 = f.vertex_point(ph12)

# Hole wire: 11→12→22→21→11 (CW from +z = correct for inner bound)
eh0 = line_edge(vh11, vh12, ph11,  0, 1)   # going up
eh1 = line_edge(vh12, vh22, ph12,  1, 0)   # going right
eh2 = line_edge(vh22, vh21, ph22,  0,-1)   # going down
eh3 = line_edge(vh21, vh11, ph21, -1, 0)   # going left
lp_hole = f.edge_loop([
    f.oriented_edge(eh0, True),
    f.oriented_edge(eh1, True),
    f.oriented_edge(eh2, True),
    f.oriented_edge(eh3, True),
])
fb = f.face_bound(lp_hole, orientation=True)

# Plane on z=0 with outward normal (0,0,+1)
p_origin = pt2(0, 0)
ax = f.axis2_placement_3d(p_origin, f.direction((0,0,1)), f.direction((1,0,0)))
pl = f.plane(ax)

# Single ADVANCED_FACE with outer bound + hole
# DEFECT IS in lp_outer: eo1 orientation=False breaks required CCW winding
face = f.advanced_face([fob, fb], pl, same_sense=True)

# Wrap in OPEN_SHELL (single face, not a solid — matches catalog: n_faces_total==1)
open_sh = f.open_shell([face])
sbsm = f.shell_based_surface_model([open_sh])

f.add_product_chain(sbsm)
