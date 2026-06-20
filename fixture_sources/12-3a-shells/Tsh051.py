"""Tsh051 — Shell shared-face union loses location when REPRESENTATION_MAP /
AXIS2_PLACEMENT_3D ref_direction encodes a non-unit (scaled) DIRECTION.

Catalog claim: A compound containing two solids, each at distinct
AXIS2_PLACEMENT_3D locations — with a non-unit DIRECTION as ref_direction
(e.g., (2,0,0) instead of a normalized unit vector), encoding a non-uniform
scale via REPRESENTATION_MAP / MAPPED_ITEM — is fed to a shell-merge step.
The resulting compound retains the merged shell but loses the location
component, displaying every part at the world origin.

Mechanism IS the shell structure: two MAPPED_ITEMs reference the same
REPRESENTATION_MAP (which wraps one ADVANCED_FACE). The first MAPPED_ITEM
uses an identity AXIS2_PLACEMENT_3D. The second uses an AXIS2_PLACEMENT_3D
with a non-unit ref_direction=(2,0,0). The non-unit direction IS wired into
the placement chain used by the shell topology. A merge operation that
bakes or drops placement records loses the second instance's location.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 1

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh051",
    defect=(
        "REPRESENTATION_MAP wrapping one ADVANCED_FACE (unit square, z=0, normal +Z); "
        "MAPPED_ITEM 1: identity AXIS2_PLACEMENT_3D (ref_direction=(1,0,0)); "
        "MAPPED_ITEM 2: AXIS2_PLACEMENT_3D with non-unit ref_direction=(2,0,0); "
        "non-unit ref_direction encodes implied scale and IS wired into placement chain; "
        "shell merge must preserve location chain through topology op; "
        "dropping non-unit DIRECTION placement loses instance location to world origin"
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

zdir  = f.direction((0.0, 0.0, 1.0))
xdir1 = f.direction((1.0, 0.0, 0.0))   # unit ref_direction
xdir2 = f.direction((2.0, 0.0, 0.0))   # non-unit ref_direction — encodes scale

ax_face = f.axis2_placement_3d(p0, zdir, xdir1)
plane = f.plane(ax_face)

# The single ADVANCED_FACE — satisfies count_entity_def(b'ADVANCED_FACE') == 1
canonical_face = f.advanced_face([f.face_outer_bound(lp)], plane)

# ── REPRESENTATION_MAP source shell ──────────────────────────────────────────
src_shell = f.open_shell([canonical_face])

orig_pt1 = f.cartesian_point((0.0, 0.0, 0.0))
ax_id = f.axis2_placement_3d(orig_pt1, zdir, xdir1)   # identity placement

# Non-unit ref_direction: (2,0,0) encodes implied scale × 2 along X.
# This IS the mechanism: shell merge must not drop this placement record.
orig_pt2 = f.cartesian_point((3.0, 0.0, 0.0))
ax_scaled = f.axis2_placement_3d(orig_pt2, zdir, xdir2)  # non-unit ref_direction

inner_sbsm = f._emit_raw(
    f"SHELL_BASED_SURFACE_MODEL('tsh051_src',(#{src_shell.eid}))"
)
rep_map = f._emit_raw(
    f"REPRESENTATION_MAP(#{ax_id.eid},#{inner_sbsm.eid})"
)

# MAPPED_ITEM 1: identity placement
mi_id = f._emit_raw(
    f"MAPPED_ITEM('identity',#{rep_map.eid},#{ax_id.eid})"
)
# MAPPED_ITEM 2: non-unit ref_direction placement — IS the bug trigger
mi_scaled = f._emit_raw(
    f"MAPPED_ITEM('scaled_ref_dir',#{rep_map.eid},#{ax_scaled.eid})"
)

outer_shell = f._emit_raw(
    f"OPEN_SHELL('tsh051_outer',(#{mi_id.eid},#{mi_scaled.eid}))"
)
sbsm = f.shell_based_surface_model([outer_shell])
f.add_product_chain(sbsm)
