"""Tsh054 — Merging adjacent same-surface faces crashes when input has chained
placements.

Catalog claim: A compound built from a sub-shape via location chain (e.g.,
assembly child positioned via MAPPED_ITEM) is fed to a same-surface face
merge. The algorithm tries to modify a sub-shape that is shared across
instances, raising "shape is modified and removed simultaneously" in debug
builds and segfaulting in release.

Mechanism IS the shell structure: two MAPPED_ITEMs reference the SAME
REPRESENTATION_MAP (wrapping the same MANIFOLD_SOLID_BREP / OPEN_SHELL /
ADVANCED_FACE). Both instances share the same underlying topology pointers.
The chained placement chain IS wired into the shell/face topology via the
MAPPED_ITEM → REPRESENTATION_MAP → face references. A face unifier that
mutates sub-shapes in-place will corrupt both instances simultaneously.

Byte assertions:
  - contains(b'MAPPED_ITEM')
  - count_entity_def(b'ADVANCED_FACE') == 1

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh054",
    defect=(
        "REPRESENTATION_MAP wrapping one ADVANCED_FACE (unit square, z=0, normal +Z); "
        "two MAPPED_ITEMs both reference the SAME rep_map at different placements; "
        "MAPPED_ITEM 1 at identity (0,0,0); MAPPED_ITEM 2 at translation (3,0,0); "
        "shared underlying topology pointers ARE wired into both placement chains; "
        "face merge must deep-copy before mutating; "
        "mutating shared sub-shape causes 'modified and removed simultaneously' crash"
    ),
)

# ── Canonical face: unit square in XY at z=0, normal +Z ──────────────────────
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

def line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(v0, v1, p0,  1, 0, 0)
e1 = line_edge(v1, v2, p1,  0, 1, 0)
e2 = line_edge(v2, v3, p2, -1, 0, 0)
e3 = line_edge(v3, v0, p3,  0,-1, 0)

lp = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax_face = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(ax_face)

# The single ADVANCED_FACE — satisfies count_entity_def(b'ADVANCED_FACE') == 1
canonical_face = f.advanced_face([f.face_outer_bound(lp)], plane)

# ── REPRESENTATION_MAP: shared source topology ────────────────────────────────
src_shell = f.open_shell([canonical_face])

orig_pt = f.cartesian_point((0.0, 0.0, 0.0))
ax_map_origin = f.axis2_placement_3d(orig_pt, zdir, xdir)

inner_sbsm = f._emit_raw(
    f"SHELL_BASED_SURFACE_MODEL('tsh054_src',(#{src_shell.eid}))"
)
rep_map = f._emit_raw(
    f"REPRESENTATION_MAP(#{ax_map_origin.eid},#{inner_sbsm.eid})"
)

# Two MAPPED_ITEMs referencing the SAME rep_map — shared topology IS the trigger.
# Instance 1: identity placement at (0,0,0)
ax_inst1 = f.axis2_placement_3d(orig_pt, zdir, xdir)
mi1 = f._emit_raw(
    f"MAPPED_ITEM('instance_1',#{rep_map.eid},#{ax_inst1.eid})"
)

# Instance 2: translated placement at (3,0,0)
pt2 = f.cartesian_point((3.0, 0.0, 0.0))
ax_inst2 = f.axis2_placement_3d(pt2, zdir, xdir)
mi2 = f._emit_raw(
    f"MAPPED_ITEM('instance_2',#{rep_map.eid},#{ax_inst2.eid})"
)

# Compound shell: both MAPPED_ITEMs reference the same underlying topology
outer_shell = f._emit_raw(
    f"OPEN_SHELL('tsh054_outer',(#{mi1.eid},#{mi2.eid}))"
)
sbsm = f.shell_based_surface_model([outer_shell])
f.add_product_chain(sbsm)
