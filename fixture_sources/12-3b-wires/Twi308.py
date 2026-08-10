"""Twi308 — Line written with a fourth, extra argument after the vector.

Catalog claim: a writer appends a stray fourth argument to a LINE —
`LINE('',#pnt,#vec,.T.)` — where ISO 10303-42 declares exactly three
(name, point, direction vector). The reference slots all hold the right
types, so a purely type-based reference check passes; only counting the
arguments against the schema's declared arity catches it. The pattern
matches a writer emitting a sibling entity's trailing flag one row early.

Canonical claimant for the line row of the fixed-arity table
(structural-linter v4).

Geometry: a 10x10 square face at z=0; the bottom edge's LINE carries the
extra argument, the rest of the file is correct, and the malformed line is
wired into the wire via its edge.

Byte assertions:
  - count_entity_def(b'LINE') == 4
  - matches(rb"=LINE\\('',#\\d+,#\\d+,\\.T\\.\\)")

Structural assertion: struct == ARG_COUNT
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi308",
    defect=(
        "the bottom edge's LINE written with a stray fourth argument "
        "(a boolean flag after the vector) where the schema declares "
        "exactly three; every reference slot holds the correct type, so "
        "only an argument-count check against the schema catches it. "
        "Wired into the wire via its edge"
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

vec0 = f.vector(dx, S)
# THE DEFECT: four args where the schema declares three.
ln0 = f._emit_raw(f"LINE('',#{p0.eid},#{vec0.eid},.T.)")
e0 = f.edge_curve(v0, v1, ln0)
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(dy, S)))
e2 = f.edge_curve(v2, v3, f.line(p2, f.vector(dnx, S)))
e3 = f.edge_curve(v3, v0, f.line(p3, f.vector(dny, S)))

loop = f.edge_loop([f.oriented_edge(e, True) for e in (e0, e1, e2, e3)])
plane = f.plane(f.axis2_placement_3d(p0, f.direction((0.0, 0.0, 1.0)), dx))
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="twi308_square")
sbsm = f.shell_based_surface_model([f.open_shell([face])])
f.add_product_chain(sbsm)
