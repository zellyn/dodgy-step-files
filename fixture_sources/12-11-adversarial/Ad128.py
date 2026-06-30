"""Ad128 — ORIENTED_EDGE mutual circular reference causes stack overflow.

Catalog claim: STEP file where an ORIENTED_EDGE entity references itself as
its own edge_element (`#N=ORIENTED_EDGE('',*,*,#N,.T.);`). The resolver
recurses until stack exhausted — potential denial-of-service in embedded
importers (PrusaSlicer 2.6.1, OCCT 7.x).

Source: https://github.com/prusa3d/PrusaSlicer/issues/11305

The attack payload is emitted via _emit_raw() so we can know the entity ID
before writing it (self-reference requires knowing the ID in advance).
A valid planar face provides the product chain; OCCT constructs the shape
from that and may detect/skip the self-referential oriented edge.

OCCT behavior: OCCT silently ignores the orphan self-referential ORIENTED_EDGE
(it is not referenced by any EDGE_LOOP in the valid shape), yields shape(1).

Byte assertions:
  contains(b'ORIENTED_EDGE')
  contains(b"ORIENTED_EDGE('',*,*,")
Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad128",
    defect=(
        "ORIENTED_EDGE self-referential entity: #N=ORIENTED_EDGE('',*,*,#N,.T.) "
        "where the edge_element forward-ref equals the entity's own ID; "
        "mutual circular reference causes stack overflow on import (PrusaSlicer#11305); "
        "OPEN_SHELL planar face IS model entity — OCC yields shape(1) (cycle skipped)"
    ),
)

# ── Valid planar face (1×1 square) — provides OCCT a real product chain ──────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)
e0 = line_edge(p0, (1.0,  0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0,  1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# ── ATTACK PAYLOAD: ORIENTED_EDGE self-reference ──────────────────────────────
# The defect per DEF-B: #N=ORIENTED_EDGE('',*,*,#N,.T.);
# We look up _next_id before emitting so the entity references its own ID.
# This is the exact pattern from PrusaSlicer#11305.
# Byte assertion: contains(b"ORIENTED_EDGE('',*,*,")
self_oe_id = f._next_id
f._emit_raw(
    f"ORIENTED_EDGE('',*,*,#{self_oe_id},.T.)"
)
