"""Tsh265 — Closed shell whose face list holds a bare edge loop where its sixth face should be.

Catalog claim: a writer flattening its topology tree by one level emits the
top face's EDGE_LOOP directly into the CLOSED_SHELL's face list instead of
wrapping it in FACE_OUTER_BOUND + ADVANCED_FACE. The shell declares six
members but only five are faces; the sixth is a loop — a wrong-type
reference in a slot ISO 10303-42 declares as a set of faces.

This is the canonical claimant for the shell-face-list row of the wrong-type
slot table (structural-linter v3): before this fixture, every corpus carrier
of a wrong-typed aggregate exercised OPEN_SHELL, never CLOSED_SHELL.

Geometry: a complete 10x10x10 cube; bottom/front/back/left/right are real
ADVANCED_FACEs, the top face's boundary exists only as the EDGE_LOOP
`top_loop_listed_as_face`, listed sixth in the shell. Every entity is
reachable from the shape root; nothing is an orphan.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 5
  - count_entity_def(b'CLOSED_SHELL') == 1
  - contains(b'top_loop_listed_as_face')

Structural assertion: struct == SLOT_TYPE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh265",
    defect=(
        "CLOSED_SHELL('tsh265_shell') listing five ADVANCED_FACEs plus the "
        "EDGE_LOOP 'top_loop_listed_as_face' as its sixth member: the writer "
        "emitted the top face's loop one level too high, so a set-of-faces "
        "slot holds a loop entity. The cube is otherwise complete and every "
        "entity is reachable from the shape representation"
    ),
)

S = 10.0
COORDS = [(0.0, 0.0, 0.0), (S, 0.0, 0.0), (S, S, 0.0), (0.0, S, 0.0),
          (0.0, 0.0, S),   (S, 0.0, S),   (S, S, S),   (0.0, S, S)]
pts = [f.cartesian_point(c) for c in COORDS]
vts = [f.vertex_point(p) for p in pts]

EDGE_SPECS = [(0, 1), (1, 2), (2, 3), (3, 0),
              (4, 5), (5, 6), (6, 7), (7, 4),
              (0, 4), (1, 5), (2, 6), (3, 7)]


def edge(a, b):
    dx, dy, dz = (COORDS[b][0]-COORDS[a][0], COORDS[b][1]-COORDS[a][1],
                  COORDS[b][2]-COORDS[a][2])
    mag = (dx*dx + dy*dy + dz*dz) ** 0.5
    d = f.direction((dx/mag, dy/mag, dz/mag))
    return f.edge_curve(vts[a], vts[b], f.line(pts[a], f.vector(d, mag)))


edges = [edge(a, b) for a, b in EDGE_SPECS]


def loop(spec, name=""):
    return f.edge_loop([f.oriented_edge(edges[e], fwd) for e, fwd in spec],
                       name=name)


def plane(centre, z, x):
    return f.plane(f.axis2_placement_3d(
        f.cartesian_point(centre), f.direction(z), f.direction(x)))


def face(spec, centre, z, x, name=""):
    return f.advanced_face([f.face_outer_bound(loop(spec))],
                           plane(centre, z, x), name=name)


h = S / 2.0
f_bot   = face([(3, False), (2, False), (1, False), (0, False)],
               (h, h, 0.0), (0, 0, -1), (1, 0, 0), name="tsh265_bot")
f_front = face([(0, True), (9, True), (4, False), (8, False)],
               (h, 0.0, h), (0, -1, 0), (1, 0, 0), name="tsh265_front")
f_back  = face([(11, True), (6, False), (10, False), (2, True)],
               (h, S, h), (0, 1, 0), (1, 0, 0), name="tsh265_back")
f_left  = face([(8, True), (7, False), (11, False), (3, True)],
               (0.0, h, h), (-1, 0, 0), (0, 0, 1), name="tsh265_left")
f_right = face([(1, True), (10, True), (5, False), (9, False)],
               (S, h, h), (1, 0, 0), (0, 0, 1), name="tsh265_right")

# THE DEFECT: the top boundary exists only as this loop, and the shell lists
# it where its sixth ADVANCED_FACE belongs.
top_loop = loop([(4, True), (5, True), (6, True), (7, True)],
                name="top_loop_listed_as_face")

shell = f.closed_shell([f_bot, f_front, f_back, f_left, f_right, top_loop],
                       name="tsh265_shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
