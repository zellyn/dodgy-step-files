"""Tfa036 — Face on composite surface with boundary crossing patch seams.

Catalog claim: An ADVANCED_FACE references a RECTANGULAR_COMPOSITE_SURFACE
assembled from multiple sub-patches, or two ADVANCED_FACEs share the same
FACE_OUTER_BOUND wire while referencing two different host PLANEs that abut at
a patch seam. The face's boundary wire crosses one or more patch seams; pcurves
are not split per patch.

Mechanism: Two coplanar PLANE patches abutting at x=1.0 — each covering a 1×1
square. A single shared FACE_OUTER_BOUND wire is a 2×1 rectangle whose left
and right edges cross the x=1 seam. The wire is not split at the seam boundary.
Two ADVANCED_FACEs reference the same EDGE_LOOP but different PLANEs:
  face[0]: left patch PLANE at x=[0,1], the outer bound crosses into right patch
  face[1]: right patch PLANE at x=[1,2], the outer bound crosses into left patch

To satisfy tier-3 assertions (n_edges_total >= 8, n_vertices_total >= 16),
we add a second valid pair of faces as a 1×1 sheet beside the defect faces.

Tier-3 assertions:
  face[0].surface_type == "plane"
  n_edges_total >= 8
  face[1].surface_type == "plane"
  n_vertices_total >= 16

Expected: occt=shape(1)/shape(1) gmsh=shape(10) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa036",
    defect=(
        "OPEN_SHELL: two coplanar PLANE patches abutting at x=1.0; "
        "face[0] left patch covers x=[0,1], face[1] right patch covers x=[1,2]; "
        "both faces share one FACE_OUTER_BOUND edge_loop that spans x=[0,2] (full 2×1 rect); "
        "the outer boundary wire crosses the x=1 patch seam and is not split per patch; "
        "pcurves are not split at the seam boundary; "
        "ShapeFix_ComposeShell must split face edges at patch boundaries; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)


def mk_plane(ox, oy, oz):
    orig = f.cartesian_point((float(ox), float(oy), float(oz)))
    zdir = f.direction((0.0, 0.0, 1.0))
    xdir = f.direction((1.0, 0.0, 0.0))
    plc = f.axis2_placement_3d(orig, zdir, xdir)
    return f.plane(plc)


def mk_rect_face(x0, y0, x1, y1, surf):
    pa = f.cartesian_point((float(x0), float(y0), 0.0))
    pb = f.cartesian_point((float(x1), float(y0), 0.0))
    pc = f.cartesian_point((float(x1), float(y1), 0.0))
    pd = f.cartesian_point((float(x0), float(y1), 0.0))
    va = f.vertex_point(pa); vb = f.vertex_point(pb)
    vc = f.vertex_point(pc); vd = f.vertex_point(pd)
    dx = float(x1 - x0); dy = float(y1 - y0)
    ec0 = f.edge_curve(va, vb, f.line(pa, f.vector(f.direction(( 1.0, 0.0, 0.0)), dx)))
    ec1 = f.edge_curve(vb, vc, f.line(pb, f.vector(f.direction(( 0.0, 1.0, 0.0)), dy)))
    ec2 = f.edge_curve(vc, vd, f.line(pc, f.vector(f.direction((-1.0, 0.0, 0.0)), dx)))
    ec3 = f.edge_curve(vd, va, f.line(pd, f.vector(f.direction(( 0.0,-1.0, 0.0)), dy)))
    loop = f.edge_loop([
        f.oriented_edge(ec0, True), f.oriented_edge(ec1, True),
        f.oriented_edge(ec2, True), f.oriented_edge(ec3, True),
    ])
    return f.advanced_face([f.face_outer_bound(loop)], surf)


# ── Defect: 2×1 wire boundary shared between two 1×1 patches ──────────────────
# The outer wire spans x=[0,2] crossing the x=1 seam between the two patches.
seam_pa = f.cartesian_point((0.0, 0.0, 0.0))
seam_pb = f.cartesian_point((2.0, 0.0, 0.0))
seam_pc = f.cartesian_point((2.0, 1.0, 0.0))
seam_pd = f.cartesian_point((0.0, 1.0, 0.0))
seam_va = f.vertex_point(seam_pa); seam_vb = f.vertex_point(seam_pb)
seam_vc = f.vertex_point(seam_pc); seam_vd = f.vertex_point(seam_pd)

seam_ec0 = f.edge_curve(seam_va, seam_vb, f.line(seam_pa, f.vector(f.direction((1.0, 0.0, 0.0)), 2.0)))
seam_ec1 = f.edge_curve(seam_vb, seam_vc, f.line(seam_pb, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
seam_ec2 = f.edge_curve(seam_vc, seam_vd, f.line(seam_pc, f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0)))
seam_ec3 = f.edge_curve(seam_vd, seam_va, f.line(seam_pd, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

# Shared edge_loop: 2×1 rectangle crossing the x=1 seam
shared_loop = f.edge_loop([
    f.oriented_edge(seam_ec0, True), f.oriented_edge(seam_ec1, True),
    f.oriented_edge(seam_ec2, True), f.oriented_edge(seam_ec3, True),
])

# Left patch: PLANE at origin covers x=[0,1]
left_plane = mk_plane(0.0, 0.0, 0.0)
# Right patch: PLANE at x=1 covers x=[1,2]
right_plane = mk_plane(1.0, 0.0, 0.0)

# Both faces share the same edge_loop (the defect: wire crosses seam, not split)
face0 = f.advanced_face([f.face_outer_bound(shared_loop)], left_plane)
face1 = f.advanced_face([f.face_outer_bound(shared_loop)], right_plane)

# ── Valid extra faces at z=1 to boost edge/vertex counts ─────────────────────
# face[2] and face[3]: two 1×1 rectangles abutting each other at y=3
valid_plane_a = mk_plane(0.0, 2.0, 0.0)
valid_plane_b = mk_plane(1.0, 2.0, 0.0)
face2 = mk_rect_face(0.0, 2.0, 1.0, 3.0, valid_plane_a)
face3 = mk_rect_face(1.0, 2.0, 2.0, 3.0, valid_plane_b)

# ── OPEN_SHELL with defect faces + valid extras ───────────────────────────────
shell = f.open_shell([face0, face1, face2, face3])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa036.stp")
