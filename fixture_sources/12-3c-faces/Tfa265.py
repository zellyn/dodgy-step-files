"""Tfa265 — Face outer bound whose bound slot holds an empty aggregate.

Catalog claim: a face's outer bound is written as
`FACE_OUTER_BOUND('outer_bound_empty',(),.T.)` — the bound slot holding an
empty aggregate where a loop reference belongs. The writer dropped the
entire boundary chain (no loop, edge, or curve exists in the file) and
emitted `()` in the slot. Distinct from the unbounded-face fixture in this
section (which has NO bound entity at all) and from the wrong-type bound
fixtures (whose slot holds a real entity of the wrong kind): here the
bound entity exists but points at nothing.

Canonical claimant for the face-outer-bound row of the nonempty-aggregate
table (structural-linter v4).

Byte assertions:
  - contains(b"FACE_OUTER_BOUND('outer_bound_empty',(),.T.)")
  - count_entity_def(b'EDGE_LOOP') == 0

Structural assertion: struct == EMPTY_AGGREGATE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tfa265",
    defect=(
        "ADVANCED_FACE whose FACE_OUTER_BOUND('outer_bound_empty') carries "
        "an empty aggregate in its bound slot — no loop, edge, or curve "
        "exists anywhere in the file; the writer emitted () where the "
        "boundary reference belongs. The plane and product chain are "
        "correct and the bound is reachable through the face"
    ),
)

centre = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plane = f.plane(f.axis2_placement_3d(centre, zdir, xdir))

# THE DEFECT: empty aggregate where the loop reference belongs.
bound = f._emit_raw("FACE_OUTER_BOUND('outer_bound_empty',(),.T.)")
face = f.advanced_face([bound], plane, name="tfa265_face")
sbsm = f.shell_based_surface_model([f.open_shell([face])])
f.add_product_chain(sbsm)
