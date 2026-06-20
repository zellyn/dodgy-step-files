"""Tsh053 — Merging coplanar adjacent faces fails with construction error on
shape with empty edge loop.

Catalog claim: A shape on which adjacent same-surface faces are being merged
has a face whose wire references zero edges (empty edge list inside EDGE_LOOP).
The merge algorithm hits an internal precondition that requires at least one
edge per loop and raises a construction error, aborting the entire merge.

Mechanism IS the shell structure: an OPEN_SHELL contains one ADVANCED_FACE
whose FACE_OUTER_BOUND references an EDGE_LOOP with an empty edge list
(EDGE_LOOP('',())). The empty EDGE_LOOP IS directly wired into the face's
boundary topology. A merge step that does not validate input topology before
running will hit a construction-error precondition when it attempts to walk
the edges of this loop.

Byte assertions:
  - matches(rb'EDGE_LOOP\\s*\\(\\s*\\'[^\\']*\\'\\s*,\\s*\\(\\s*\\)\\s*\\)')
  - count_entity_def(b'ADVANCED_FACE') == 1

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh053",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with empty edge list EDGE_LOOP('',()); "
        "empty EDGE_LOOP IS wired into face boundary topology; "
        "merge step must validate input before running; "
        "construction error raised when merge walker finds zero edges to iterate"
    ),
)

# ── Plane geometry ────────────────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Empty EDGE_LOOP: IS the mechanism (construction-error trigger) ─────────────
# Emit directly via _emit_raw so the loop is genuinely empty.
empty_loop = f._emit_raw("EDGE_LOOP('',())")

# FACE_OUTER_BOUND and ADVANCED_FACE referencing the empty loop
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{empty_loop.eid},.T.)")
face = f._emit_raw(
    f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)"
)

# OPEN_SHELL: empty loop IS wired into shell/face topology
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
