"""Twi307 — Vector written with two arguments: the name slot is omitted entirely.

Catalog claim: a writer emits `VECTOR(#dir,10.0)` — direction and magnitude
only, the leading name argument dropped. Two arguments where ISO 10303-42
declares three. This exact byte pattern is the single largest bucket of the
corpus's crash census (a name-omitted vector shifts every subsequent
argument one slot left), yet until this fixture no entry CLAIMED it as its
defect — every carrier was a fixture about something else whose scaffold
happened to contain one.

Canonical claimant for the vector row of the fixed-arity table
(structural-linter v4).

Geometry: a 10x10 square face at z=0; the bottom edge's line direction
vector `VECTOR(#dir,10.0)` carries the omission; the other three edges are
correct. The malformed vector is wired into the wire via its line and edge.

Byte assertions:
  - count_entity_def(b'VECTOR') == 4
  - matches(rb"=VECTOR\\(#\\d+,10\\.0\\)")

Structural assertion: struct == ARG_COUNT
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi307",
    defect=(
        "the bottom edge's direction vector written as VECTOR(#dir,10.0) — "
        "two arguments, the name slot omitted, where the schema declares "
        "three. The following arguments each sit one slot early. The square "
        "face is otherwise correct and the malformed vector is wired into "
        "the wire via its line and edge"
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

# THE DEFECT: two args, name omitted.
vec0 = f._emit_raw(f"VECTOR(#{dx.eid},10.0)")
e0 = f.edge_curve(v0, v1, f.line(p0, vec0))
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(dy, S)))
e2 = f.edge_curve(v2, v3, f.line(p2, f.vector(dnx, S)))
e3 = f.edge_curve(v3, v0, f.line(p3, f.vector(dny, S)))

loop = f.edge_loop([f.oriented_edge(e, True) for e in (e0, e1, e2, e3)])
plane = f.plane(f.axis2_placement_3d(p0, f.direction((0.0, 0.0, 1.0)), dx))
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="twi307_square")
sbsm = f.shell_based_surface_model([f.open_shell([face])])
f.add_product_chain(sbsm)
