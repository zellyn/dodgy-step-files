"""Tfa032 — Same-domain face merge introduces overlap / self-intersection
on boolean result.

Catalog claim: Merging adjacent same-domain faces on a boolean result
introduces new defects (overlapping faces, self-intersections) that were not
present in the raw boolean output. The merge unions topology that should
remain separate, e.g. a tapered-shape-sharing-edge case or a wedge-wedge-
boundary case.

Mechanism: OPEN_SHELL with THREE coplanar ADVANCED_FACEs all on the same PLANE
(z=0). A large 20×10 base face plus a small 5×5 overlay face that overlaps the
right half of the base — simulating the kind of topology that a same-domain
merge would incorrectly unify. The overlay face shares some boundary geometry
with the base face but also extends into the same region, creating an overlap
defect. The third face is a 10×10 square abutting the base on the right.

Shell layout (z=0):
  face[0]: 20×10 base rectangle (x:0–20, y:0–10) — underlying large face
  face[1]: 5×5 overlay patch (x:10–15, y:2–7) — OVERLAPS interior of face[0]
  face[2]: valid 10×10 face (x:21–31, y:0–10) — separate, ensures n_edges>=9

All three faces on the same PLANE entity — the same-domain merge condition.
When the merge pass tries to unify face[0] and face[2] (which are same-domain
but not adjacent), it incorrectly includes face[1] and creates a self-
intersecting boundary.

Tier-3 assertions:
  n_edges_total >= 9
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(17) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa032",
    defect=(
        "OPEN_SHELL: three coplanar ADVANCED_FACEs on one shared PLANE at z=0; "
        "face[0]: 20×10 base (x:0–20, y:0–10); "
        "face[1]: 5×5 overlay (x:10–15, y:2–7) — overlaps interior of face[0]; "
        "face[2]: 10×10 adjacent (x:21–31, y:0–10) — separate, valid; "
        "same-domain merge of face[0]+face[1]+face[2] introduces self-intersection "
        "because face[1] overlaps face[0] interior; "
        "same-domain face merge pass must detect overlap and skip or roll back; "
        "defect IS on live OPEN_SHELL traversal path: all three faces in shell"
    ),
)

# Shared PLANE: z=0, standard orientation
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)


def make_rect_face(x0, y0, x1, y1, surf):
    """Build a rectangular ADVANCED_FACE at z=0."""
    pa = f.cartesian_point((x0, y0, 0.0))
    pb = f.cartesian_point((x1, y0, 0.0))
    pc = f.cartesian_point((x1, y1, 0.0))
    pd = f.cartesian_point((x0, y1, 0.0))
    va = f.vertex_point(pa)
    vb = f.vertex_point(pb)
    vc = f.vertex_point(pc)
    vd = f.vertex_point(pd)
    dx = x1 - x0
    dy = y1 - y0
    ec0 = f.edge_curve(va, vb, f.line(pa, f.vector(f.direction(( 1.0, 0.0, 0.0)), dx)))
    ec1 = f.edge_curve(vb, vc, f.line(pb, f.vector(f.direction(( 0.0, 1.0, 0.0)), dy)))
    ec2 = f.edge_curve(vc, vd, f.line(pc, f.vector(f.direction((-1.0, 0.0, 0.0)), dx)))
    ec3 = f.edge_curve(vd, va, f.line(pd, f.vector(f.direction(( 0.0,-1.0, 0.0)), dy)))
    loop = f.edge_loop([
        f.oriented_edge(ec0, True),
        f.oriented_edge(ec1, True),
        f.oriented_edge(ec2, True),
        f.oriented_edge(ec3, True),
    ])
    return f.advanced_face([f.face_outer_bound(loop)], surf)


# ── face[0]: 20×10 base — the large underlying face ─────────────────────────
face0 = make_rect_face(0.0, 0.0, 20.0, 10.0, plane)

# ── face[1]: 5×5 overlay overlapping face[0] interior ────────────────────────
# Sits entirely inside face[0]'s x-range [10,15] y-range [2,7]
face1 = make_rect_face(10.0, 2.0, 15.0, 7.0, plane)

# ── face[2]: separate 10×10 face (same-domain, abutting gap at x=20..21) ────
# Not touching face[0] at x=20 — separated by 1-unit gap to avoid any
# accidental legal topology sharing. The same-domain merge sees face[0] and
# face[2] as same-domain candidates but incorrectly sweeps in face[1].
face2 = make_rect_face(21.0, 0.0, 31.0, 10.0, plane)

# ── OPEN_SHELL with all three same-domain coplanar faces ─────────────────────
shell = f.open_shell([face0, face1, face2])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa032.stp")
