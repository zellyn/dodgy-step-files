"""Tsh268 — Manifold solid whose outer slot holds an empty aggregate while its shell sits unreferenced.

Catalog claim: the solid is written as
`MANIFOLD_SOLID_BREP('solid_outer_empty',())` — an empty aggregate in the
outer slot where a closed-shell reference belongs — while the complete
watertight CLOSED_SHELL over all six cube faces is present in the file,
referenced by nothing. The wrong-type sibling of this fixture (a face in
the slot) exists separately; here the slot holds NOTHING, and the repair
is the same single re-pointed reference.

Canonical claimant for the manifold-solid row of the nonempty-aggregate
table (structural-linter v4).

Geometry: a complete 6x6x6 cube; shell `tsh268_unlisted_shell` lists all
six faces but is unreachable; the solid with the empty outer slot is what
the shape representation carries.

Byte assertions:
  - contains(b"MANIFOLD_SOLID_BREP('solid_outer_empty',())")
  - count_entity_def(b'CLOSED_SHELL') == 1

Structural assertion: struct == EMPTY_AGGREGATE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh268",
    defect=(
        "MANIFOLD_SOLID_BREP('solid_outer_empty') whose outer slot holds an "
        "empty aggregate while the complete watertight "
        "CLOSED_SHELL('tsh268_unlisted_shell') over all six cube faces sits "
        "in the same file referenced by nothing; repair = re-point one "
        "reference to the shell already present"
    ),
)

S = 6.0
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


def face(spec, centre, z, x, name=""):
    lp = f.edge_loop([f.oriented_edge(edges[e], fwd) for e, fwd in spec])
    pl = f.plane(f.axis2_placement_3d(
        f.cartesian_point(centre), f.direction(z), f.direction(x)))
    return f.advanced_face([f.face_outer_bound(lp)], pl, name=name)


h = S / 2.0
faces = [
    face([(3, False), (2, False), (1, False), (0, False)], (h, h, 0.0), (0, 0, -1), (1, 0, 0), "tsh268_bot"),
    face([(4, True), (5, True), (6, True), (7, True)], (h, h, S), (0, 0, 1), (1, 0, 0), "tsh268_top"),
    face([(0, True), (9, True), (4, False), (8, False)], (h, 0.0, h), (0, -1, 0), (1, 0, 0), "tsh268_front"),
    face([(11, True), (6, False), (10, False), (2, True)], (h, S, h), (0, 1, 0), (1, 0, 0), "tsh268_back"),
    face([(8, True), (7, False), (11, False), (3, True)], (0.0, h, h), (-1, 0, 0), (0, 0, 1), "tsh268_left"),
    face([(1, True), (10, True), (5, False), (9, False)], (S, h, h), (1, 0, 0), (0, 0, 1), "tsh268_right"),
]

# The complete shell is PRESENT but referenced by nothing — the repair target.
shell = f.closed_shell(faces, name="tsh268_unlisted_shell")

# THE DEFECT: empty aggregate where the closed-shell reference belongs.
msb = f._emit_raw("MANIFOLD_SOLID_BREP('solid_outer_empty',())")
f.add_product_chain(msb, mode="brep_shape")
