"""Tfa024 — Glue Faces (coincident faces).

Catalog claim: Two ADVANCED_FACEs are geometrically coincident — duplicate
layers on the same underlying surface, often from botched Booleans. Both
attached to the same shell. Downstream sewing leaves free bounds or duplicate
edges; the resulting shell is open instead of closed.

Mechanism: CLOSED_SHELL with THREE ADVANCED_FACEs: two coincident faces on
the same PLANE at z=0 (same geometry, fresh entity IDs — the "glue" defect)
plus one distinct face on a second plane at z=1 so the shell has enough
topology for OCC to produce shape(1). The two coincident bottom faces are
the defect: same underlying PLANE surface, same EDGE_LOOP geometry (identical
x/y extents), but stored under different entity IDs.

Tier-3 assertions:
  n_edges_total >= 8
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(14) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa024",
    defect=(
        "CLOSED_SHELL: two geometrically coincident ADVANCED_FACEs on the same PLANE at z=0 "
        "(same coords, different entity IDs — duplicate face layers from a botched Boolean); "
        "face[0] and face[1] both reference the same PLANE entity with identical 10×10 EDGE_LOOPs; "
        "face[2] is a distinct valid face at z=1 so OCC loads shape(1); "
        "defect IS on live CLOSED_SHELL traversal path: both coincident faces are wired into shell; "
        "heal — keep one face, drop duplicate; merge results into non-manifold-clean compound"
    ),
)

# ── Shared PLANE: z=0 — both coincident faces reference this ─────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, -1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane_bot = f.plane(pl_plc)

# ── face[0]: first copy of the 10×10 square at z=0 ──────────────────────────
p0a = f.cartesian_point(( 0.0,  0.0, 0.0))
p1a = f.cartesian_point((10.0,  0.0, 0.0))
p2a = f.cartesian_point((10.0, 10.0, 0.0))
p3a = f.cartesian_point(( 0.0, 10.0, 0.0))

v0a = f.vertex_point(p0a)
v1a = f.vertex_point(p1a)
v2a = f.vertex_point(p2a)
v3a = f.vertex_point(p3a)

ec_a0 = f.edge_curve(v0a, v1a, f.line(p0a, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec_a1 = f.edge_curve(v1a, v2a, f.line(p1a, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_a2 = f.edge_curve(v2a, v3a, f.line(p2a, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec_a3 = f.edge_curve(v3a, v0a, f.line(p3a, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

loop_a = f.edge_loop([
    f.oriented_edge(ec_a0, True),
    f.oriented_edge(ec_a1, True),
    f.oriented_edge(ec_a2, True),
    f.oriented_edge(ec_a3, True),
])
face_a = f.advanced_face([f.face_outer_bound(loop_a)], plane_bot)

# ── face[1]: DUPLICATE 10×10 square at z=0 — same PLANE, fresh entity IDs ───
# This is the "glue face" defect: geometrically coincident with face[0]
# but stored as a distinct ADVANCED_FACE in the same shell.
p0b = f.cartesian_point(( 0.0,  0.0, 0.0))
p1b = f.cartesian_point((10.0,  0.0, 0.0))
p2b = f.cartesian_point((10.0, 10.0, 0.0))
p3b = f.cartesian_point(( 0.0, 10.0, 0.0))

v0b = f.vertex_point(p0b)
v1b = f.vertex_point(p1b)
v2b = f.vertex_point(p2b)
v3b = f.vertex_point(p3b)

ec_b0 = f.edge_curve(v0b, v1b, f.line(p0b, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec_b1 = f.edge_curve(v1b, v2b, f.line(p1b, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_b2 = f.edge_curve(v2b, v3b, f.line(p2b, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec_b3 = f.edge_curve(v3b, v0b, f.line(p3b, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

loop_b = f.edge_loop([
    f.oriented_edge(ec_b0, True),
    f.oriented_edge(ec_b1, True),
    f.oriented_edge(ec_b2, True),
    f.oriented_edge(ec_b3, True),
])
# Same plane_bot entity — the coincident face shares the same supporting surface
face_b = f.advanced_face([f.face_outer_bound(loop_b)], plane_bot)

# ── face[2]: distinct face at z=1 — gives OCC enough to load shape(1) ─────
p0c = f.cartesian_point(( 0.0,  0.0, 1.0))
p1c = f.cartesian_point((10.0,  0.0, 1.0))
p2c = f.cartesian_point((10.0, 10.0, 1.0))
p3c = f.cartesian_point(( 0.0, 10.0, 1.0))

v0c = f.vertex_point(p0c)
v1c = f.vertex_point(p1c)
v2c = f.vertex_point(p2c)
v3c = f.vertex_point(p3c)

ec_c0 = f.edge_curve(v0c, v1c, f.line(p0c, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec_c1 = f.edge_curve(v1c, v2c, f.line(p1c, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_c2 = f.edge_curve(v2c, v3c, f.line(p2c, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec_c3 = f.edge_curve(v3c, v0c, f.line(p3c, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

loop_c = f.edge_loop([
    f.oriented_edge(ec_c0, True),
    f.oriented_edge(ec_c1, True),
    f.oriented_edge(ec_c2, True),
    f.oriented_edge(ec_c3, True),
])
pl_top_orig = f.cartesian_point((0.0, 0.0, 1.0))
pl_top_zdir = f.direction((0.0, 0.0, 1.0))
pl_top_xdir = f.direction((1.0, 0.0, 0.0))
pl_top_plc  = f.axis2_placement_3d(pl_top_orig, pl_top_zdir, pl_top_xdir)
plane_top   = f.plane(pl_top_plc)
face_c = f.advanced_face([f.face_outer_bound(loop_c)], plane_top)

# ── CLOSED_SHELL: all three faces — defect IS in the shell ─────────────────
closed_sh = f.closed_shell([face_a, face_b, face_c])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa024.stp")
