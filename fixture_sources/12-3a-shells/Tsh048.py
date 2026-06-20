"""Tsh048 — Same-domain face unification corrupts shape with mirrored sub-instance.

Catalog claim: A solid carries a non-identity location (mirror or scale).
When face unification is invoked, the algorithm operates in the local
coordinate frame but neglects to propagate the transform when checking
surface coincidence; same-domain detection produces false positives between
faces that are coincident only after transform but not in object-local
coordinates.

Mechanism IS the shell structure: a MAPPED_ITEM instances a single square
ADVANCED_FACE (via REPRESENTATION_MAP) with two AXIS2_PLACEMENT_3D
placements — one identity, one a mirror through the YZ plane (X → -X).
Both instances share the same underlying PLANE, so a face unifier that
compares surface geometry without propagating the placement transform will
incorrectly judge them as coincident and merge them, corrupting the shape.

Byte assertions:
  - contains(b'MAPPED_ITEM')
  - count_entity_def(b'ADVANCED_FACE') == 1

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh048",
    defect=(
        "MAPPED_ITEM instancing one ADVANCED_FACE twice via REPRESENTATION_MAP; "
        "identity placement + YZ-mirror placement (ref_direction=(-1,0,0)); "
        "same PLANE geometry means naive same-domain checker sees false coincidence "
        "and incorrectly merges the instances; "
        "mirrored placement IS wired into shell/face topology via MAPPED_ITEM; "
        "unifier must propagate transforms before coincidence test"
    ),
)

# ── Canonical face: unit square in XY at z=0, normal +Z ──────────────────────
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

def sed(va, vb, pst, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0); ln = f.line(pst, vec)
    return f.edge_curve(va, vb, ln)

e0 = sed(v0, v1, p0,  1, 0, 0)
e1 = sed(v1, v2, p1,  0, 1, 0)
e2 = sed(v2, v3, p2, -1, 0, 0)
e3 = sed(v3, v0, p3,  0,-1, 0)

lp = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])

zdir = f.direction((0.0, 0.0, 1.0))
xdir_pos = f.direction((1.0, 0.0, 0.0))
ax_face = f.axis2_placement_3d(p0, zdir, xdir_pos)
plane = f.plane(ax_face)

# The single ADVANCED_FACE — satisfies count_entity_def(b'ADVANCED_FACE') == 1
canonical_face = f.advanced_face([f.face_outer_bound(lp)], plane)

# ── REPRESENTATION_MAP source: OPEN_SHELL containing the one canonical face ──
src_shell = f.open_shell([canonical_face])

# Map origin: identity placement at origin
orig_pt = f.cartesian_point((0.0, 0.0, 0.0))
ax_id = f.axis2_placement_3d(orig_pt, zdir, xdir_pos)

# Mirror placement: ref_direction = (-1,0,0) encodes YZ-plane mirror (X→-X)
xdir_neg = f.direction((-1.0, 0.0, 0.0))
orig_mir = f.cartesian_point((0.0, 0.0, 0.0))
ax_mir = f.axis2_placement_3d(orig_mir, zdir, xdir_neg)

# Emit REPRESENTATION_MAP wrapping the source shell
# REPRESENTATION_MAP(map_origin, mapped_representation)
# mapped_representation is the inner SHELL_BASED_SURFACE_MODEL entity
inner_sbsm = f._emit_raw(
    f"SHELL_BASED_SURFACE_MODEL('tsh048_src',(#{src_shell.eid}))"
)
rep_map = f._emit_raw(
    f"REPRESENTATION_MAP(#{ax_id.eid},#{inner_sbsm.eid})"
)

# Two MAPPED_ITEMs: identity and mirror.
# MAPPED_ITEM(name, mapping_source, mapping_target)
# satisfies byte assertion: contains(b'MAPPED_ITEM')
mi_id = f._emit_raw(
    f"MAPPED_ITEM('identity',#{rep_map.eid},#{ax_id.eid})"
)
mi_mir = f._emit_raw(
    f"MAPPED_ITEM('mirror_yz',#{rep_map.eid},#{ax_mir.eid})"
)

# Wrap both MAPPED_ITEMs in an OPEN_SHELL → SHELL_BASED_SURFACE_MODEL for the
# product chain. We use the shell_based_surface_model helper and add the two
# mapped items directly — the builder lists entities via eid references.
outer_shell = f._emit_raw(
    f"OPEN_SHELL('tsh048_outer',(#{mi_id.eid},#{mi_mir.eid}))"
)
sbsm = f.shell_based_surface_model([outer_shell])
f.add_product_chain(sbsm)
