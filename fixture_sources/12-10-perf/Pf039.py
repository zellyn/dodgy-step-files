"""Pf039 — pattern-mined fixture (see catalog for source).

B4 wave-2 issue-tracker mining. LGPL-clean: synthesized from the defect
*pattern*, no upstream bytes copied.

DRIFT audit 2026-07-12: verified the self-referencing NAUO
(`#9054,#9054`) is the whole point of this fixture (cascadio's
traversal never terminates because parent==child). Live-checked locally
(macOS OCP/OCCT 7.8.1): OCCT's STEPControl_Reader treats the
self-referenced product as "used" and silently drops it from
TransferRoots() -- occt=empty/gmsh=empty, no diagnostic. That silent
drop *is* the kernel-bug witness ("no cycle detection" manifests as the
kernel silently discarding the cyclic product rather than rejecting
it with a diagnostic, per this entry's own "Expected kernel behavior").
Catalog's `occt=shape(1) gmsh=shape(9)` was a mirrored-template value,
never actually verified against this construction — corrected to the
live-observed empty/empty. Also removed a stray `_emit_raw` call that
emitted a bare comment as a malformed Part-21 instance (`#9064=/* ... */;`)
-- purely cosmetic, verified it did not affect the shape count.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pf039",
             defect='cascadio#19: STEP→GLB infinite-loop on assembly traversal')

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Self-referencing NAUO loop — cascadio's traversal doesn't detect cycles.
# (OCCT's own reader silently drops the cyclic product instead of
# reporting it -- see module docstring.)
f._emit_raw(
    "NEXT_ASSEMBLY_USAGE_OCCURRENCE('self_loop','infinite traversal',"
    "'',#9054,#9054,$)"
)
