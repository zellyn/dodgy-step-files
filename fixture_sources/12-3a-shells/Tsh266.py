"""Tsh266 — Manifold solid whose outer slot holds a single face where a closed shell is declared.

Catalog claim: a writer emits the solid's outer boundary one level too deep —
MANIFOLD_SOLID_BREP's `outer` attribute references the cube's bottom
ADVANCED_FACE instead of the CLOSED_SHELL that contains it. The shell entity
itself is present and complete in the file, so a receiver can repair the
solid by re-pointing one reference; but as written, a slot ISO 10303-42
declares as CLOSED_SHELL holds a face.

This is the canonical claimant for the solid-outer row of the wrong-type
slot table (structural-linter v3): no prior corpus fixture mis-types
MANIFOLD_SOLID_BREP's outer.

Geometry: a complete watertight 8x8x8 cube. The CLOSED_SHELL
`tsh266_orphaned_shell` lists all six faces but is referenced by nothing;
the MANIFOLD_SOLID_BREP `solid_outer_is_face` (reachable from the shape
representation) points at the bottom face instead. The DEFECT CARRIER — the
wrong-typed reference — is on the reachable solid.

Byte assertions:
  - count_entity_def(b'MANIFOLD_SOLID_BREP') == 1
  - count_entity_def(b'CLOSED_SHELL') == 1
  - contains(b'solid_outer_is_face')

Structural assertion: struct == SLOT_TYPE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh266",
    defect=(
        "MANIFOLD_SOLID_BREP('solid_outer_is_face') whose outer slot "
        "references the cube's bottom ADVANCED_FACE instead of the complete "
        "CLOSED_SHELL('tsh266_orphaned_shell') that is defined in the same "
        "file: the writer descended one level too far. Repair = re-point one "
        "reference to the shell already present"
    ),
)

S = 8.0
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
f_bot   = face([(3, False), (2, False), (1, False), (0, False)],
               (h, h, 0.0), (0, 0, -1), (1, 0, 0), name="tsh266_bot")
f_top   = face([(4, True), (5, True), (6, True), (7, True)],
               (h, h, S), (0, 0, 1), (1, 0, 0), name="tsh266_top")
f_front = face([(0, True), (9, True), (4, False), (8, False)],
               (h, 0.0, h), (0, -1, 0), (1, 0, 0), name="tsh266_front")
f_back  = face([(11, True), (6, False), (10, False), (2, True)],
               (h, S, h), (0, 1, 0), (1, 0, 0), name="tsh266_back")
f_left  = face([(8, True), (7, False), (11, False), (3, True)],
               (0.0, h, h), (-1, 0, 0), (0, 0, 1), name="tsh266_left")
f_right = face([(1, True), (10, True), (5, False), (9, False)],
               (S, h, h), (1, 0, 0), (0, 0, 1), name="tsh266_right")

# The complete shell is PRESENT but referenced by nothing — the repair target.
shell = f.closed_shell([f_bot, f_top, f_front, f_back, f_left, f_right],
                       name="tsh266_orphaned_shell")

# THE DEFECT: outer holds the bottom face where the closed shell is declared.
msb = f.manifold_solid_brep(f_bot, name="solid_outer_is_face")
f.add_product_chain(msb, mode="brep_shape")
