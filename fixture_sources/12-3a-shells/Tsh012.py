"""Tsh012 — Mixed `.T.`/`.F.` flags on `ORIENTED_EDGE` mismatched against
parameter direction; `EDGE_CURVE.same_sense` is `.U.` (uninitialized/unknown).

Catalog claim: EDGE_CURVE.same_sense boolean missing or illegal-formatted
(`.U.`) leaves an uninitialized bool, leading to non-deterministic edge
direction.  Generic boolean enum parsing defaults to True if value is not
`.T.`/`.F.`.

Mechanism IS the shell structure: a single triangular ADVANCED_FACE is built
with three EDGE_CURVEs where one of them is emitted via _emit_raw with
same_sense=.U. instead of .T. or .F.  The illegal boolean IS wired into the
face/wire/edge topology — the uninitialized flag on that EDGE_CURVE IS the
mechanism that leaves edge direction non-deterministic.

Byte assertions:
  - contains(b'.U.')
  - contains(b'EDGE_CURVE')
  - count_entity_def(b'ADVANCED_FACE') == 1

Tier-3 assertion: n_faces_total == 1
live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh012",
    defect=(
        "Single triangular ADVANCED_FACE: one EDGE_CURVE has same_sense=.U. "
        "(uninitialized/unknown boolean); non-deterministic edge direction between "
        "compiler runs; .U. flag IS wired into face/wire/edge topology; strict "
        "receivers must coerce to .T. and warn, or reject"
    ),
)

# ── Single triangular planar face ─────────────────────────────────────────────
# Three vertices forming a triangle on z=0 plane: (0,0,0), (2,0,0), (1,2,0).
# Three EDGE_CURVEs: ec0 and ec2 are normal; ec1 has same_sense=.U. — the defect.

def pt(x, y, z=0.0):
    return f.cartesian_point((float(x), float(y), float(z)))

p0 = pt(0,0,0); p1 = pt(2,0,0); p2 = pt(1,2,0)
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1); v2 = f.vertex_point(p2)

# Edge 0: v0 → v1 (bottom, going right) — normal same_sense=.T.
d_01 = f.direction((1.0, 0.0, 0.0))
vec_01 = f.vector(d_01, 1.0)
ln_01 = f.line(p0, vec_01)
ec0 = f.edge_curve(v0, v1, ln_01, same_sense=True)

# Edge 1: v1 → v2 (going up-left) — DEFECT: same_sense=.U. via raw emission
d_12 = f.direction((-1.0, 2.0, 0.0))
vec_12 = f.vector(d_12, 1.0)
ln_12 = f.line(p1, vec_12)
# Build the line entity via normal API; then emit EDGE_CURVE raw with .U.
# _emit_raw references them by their already-assigned entity IDs.
ec1 = f._emit_raw(
    f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{ln_12.eid},.U.)"
)

# Edge 2: v2 → v0 (going down-left) — normal same_sense=.T.
d_20 = f.direction((-1.0, -2.0, 0.0))
vec_20 = f.vector(d_20, 1.0)
ln_20 = f.line(p2, vec_20)
ec2 = f.edge_curve(v2, v0, ln_20, same_sense=True)

# Assemble the triangle loop (CCW from +z)
lp = f.edge_loop([
    f.oriented_edge(ec0, True),
    f.oriented_edge(ec1, True),   # ec1 has .U. same_sense — defect
    f.oriented_edge(ec2, True),
])
fob = f.face_outer_bound(lp, orientation=True)

# Plane at origin, normal (0,0,1)
p_origin = pt(0, 0, 0)
ax = f.axis2_placement_3d(p_origin, f.direction((0,0,1)), f.direction((1,0,0)))
pl = f.plane(ax)

# Single ADVANCED_FACE — defect IS wired in via ec1's .U. same_sense
face = f.advanced_face([fob], pl, same_sense=True)

# Single face as OPEN_SHELL (n_faces_total == 1 matches tier-3 assertion)
open_sh = f.open_shell([face])
sbsm = f.shell_based_surface_model([open_sh])

f.add_product_chain(sbsm)
