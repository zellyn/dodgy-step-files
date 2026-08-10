"""Twi309 — Edge curve written with a sixth, duplicated sense flag.

Catalog claim: a writer emits an edge as
`EDGE_CURVE('',#v1,#v2,#curve,.T.,.T.)` — the trailing same-sense flag
duplicated, six arguments where ISO 10303-42 declares five. All reference
slots hold their declared types, so only counting the arguments against the
schema catches the deviation. The duplicate-flag shape matches a writer
that emits one column per attribute of its WIDEST edge table row for every
edge.

Canonical claimant for the edge row of the fixed-arity table
(structural-linter v4).

Geometry: a 10x10 square face at z=0; the bottom edge carries the extra
flag, the rest is correct, and the malformed edge is wired into the wire.

Byte assertions:
  - count_entity_def(b'EDGE_CURVE') == 4
  - matches(rb"=EDGE_CURVE\\('',#\\d+,#\\d+,#\\d+,\\.T\\.,\\.T\\.\\)")

Structural assertion: struct == ARG_COUNT
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi309",
    defect=(
        "the bottom edge written with its same-sense flag duplicated — six "
        "arguments where the schema declares five; every reference slot "
        "holds the correct type, so only an argument-count check catches "
        "it. Wired into the wire via the face's loop"
    ),
)

S = 10.0
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((S, 0.0, 0.0))
p2 = f.cartesian_point((S, S, 0.0))
p3 = f.cartesian_point((0.0, S, 0.0))
v0, v1, v2, v3 = (f.vertex_point(p) for p in (p0, p1, p2, p3))

dx = f.direction((1.0, 0.0, 0.0))
dy = f.direction((0.0, 1.0, 0.0))
dnx = f.direction((-1.0, 0.0, 0.0))
dny = f.direction((0.0, -1.0, 0.0))

ln0 = f.line(p0, f.vector(dx, S))
# THE DEFECT: six args where the schema declares five.
e0 = f._emit_raw(f"EDGE_CURVE('',#{v0.eid},#{v1.eid},#{ln0.eid},.T.,.T.)")
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(dy, S)))
e2 = f.edge_curve(v2, v3, f.line(p2, f.vector(dnx, S)))
e3 = f.edge_curve(v3, v0, f.line(p3, f.vector(dny, S)))

loop = f.edge_loop([f.oriented_edge(e, True) for e in (e0, e1, e2, e3)])
plane = f.plane(f.axis2_placement_3d(p0, f.direction((0.0, 0.0, 1.0)), dx))
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="twi309_square")
sbsm = f.shell_based_surface_model([f.open_shell([face])])
f.add_product_chain(sbsm)
