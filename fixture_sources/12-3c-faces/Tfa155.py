"""Tfa155 — ShapeFix_Face.FixOrientation seam-vertex-shared.

Catalog claim: Face on cylinder where two wires both start at the seam vertex.
FixOrientation's winding test gets confused by the shared seam; both loops anchor
to identical XYZ coordinate.

Mechanism: CLOSED_SHELL consisting of a cylinder (r=5, h=10) split at mid-height.
  face[0]: upper cylindrical half (V=[5..10]) — OUTER loop starts at seam_top,
    uses seam_upper .T., top_circle .T., seam_upper .F.
  face[1]: lower cylindrical half (V=[0..5]) — OUTER loop starts at seam_bot,
    uses seam_lower .T., mid_circle .T., seam_lower .F.
Both seam wires start at seam_mid = (R, 0, 5). FixOrientation must compute the
winding sense of each wire independently; the shared vertex at (R, 0, 5) anchors
both loops to the same XYZ point, and the algorithm's winding test can assign
the same anchor to both wires, producing an ambiguous orientation comparison that
results in both wires being labeled as outer or both as inner.
Defect IS on live CLOSED_SHELL traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'CYLINDRICAL_SURFACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa155",
    defect=(
        "CLOSED_SHELL: cylinder r=5, h=10, split at mid-height z=5; "
        "face[0]: upper cyl half (V=[5..10]): seam_upper .T., top_circle .T., seam_upper .F.; "
        "face[1]: lower cyl half (V=[0..5]): seam_lower .T., mid_circle .T., seam_lower .F.; "
        "both face wires share the seam_mid vertex at (5,0,5); "
        "FixOrientation winding test anchors both loops to identical XYZ; "
        "ambiguous orientation comparison causes both wires labeled outer or both inner; "
        "face[2]: top disc cap; face[3]: bottom disc cap; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

R = 5.0
H = 10.0
H2 = H / 2.0  # = 5.0

# ── Key 3D points ─────────────────────────────────────────────────────────────
pt_seam_bot = f.cartesian_point((R, 0.0, 0.0))
pt_seam_mid = f.cartesian_point((R, 0.0, H2))   # THE SHARED VERTEX — both wires anchor here
pt_seam_top = f.cartesian_point((R, 0.0, H))

v_seam_bot = f.vertex_point(pt_seam_bot)
v_seam_mid = f.vertex_point(pt_seam_mid)
v_seam_top = f.vertex_point(pt_seam_top)

# ── Seam edges (vertical line segments) ──────────────────────────────────────
seam_lower_line = f.line(pt_seam_bot, f.vector(f.direction((0.0, 0.0, 1.0)), H2))
seam_lower_ec   = f.edge_curve(v_seam_bot, v_seam_mid, seam_lower_line)

seam_upper_line = f.line(pt_seam_mid, f.vector(f.direction((0.0, 0.0, 1.0)), H2))
seam_upper_ec   = f.edge_curve(v_seam_mid, v_seam_top, seam_upper_line)

# ── Circles (closed edges) ────────────────────────────────────────────────────
bot_ctr = f.cartesian_point((0.0, 0.0, 0.0))
bot_circ_ec = f.edge_curve(
    v_seam_bot, v_seam_bot,
    f.circle(
        f.axis2_placement_3d(bot_ctr, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0))),
        R
    )
)

mid_ctr = f.cartesian_point((0.0, 0.0, H2))
mid_circ_ec = f.edge_curve(
    v_seam_mid, v_seam_mid,
    f.circle(
        f.axis2_placement_3d(mid_ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
        R
    )
)

top_ctr = f.cartesian_point((0.0, 0.0, H))
top_circ_ec = f.edge_curve(
    v_seam_top, v_seam_top,
    f.circle(
        f.axis2_placement_3d(top_ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
        R
    )
)

# ── CYLINDRICAL_SURFACE ────────────────────────────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_surf = f.cylindrical_surface(
    f.axis2_placement_3d(cyl_orig, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
    R
)

# ── face[0]: upper cylindrical half — wire anchors at seam_mid — THE DEFECT ──
# Wire: seam_upper .T. (mid→top), top_circle .T. (full rev), seam_upper .F. (top→mid)
# This wire starts AND ends at v_seam_mid = (R,0,H2)
upper_loop = f.edge_loop([
    f.oriented_edge(seam_upper_ec, True),   # mid → top
    f.oriented_edge(top_circ_ec,   True),   # full revolution at top
    f.oriented_edge(seam_upper_ec, False),  # top → mid
])
face0 = f.advanced_face([f.face_outer_bound(upper_loop)], cyl_surf)

# ── face[1]: lower cylindrical half — wire also anchors at seam_mid — THE DEFECT
# Wire: seam_lower .T. (bot→mid), mid_circle .T. (full rev), seam_lower .F. (mid→bot)
# This wire also terminates at v_seam_mid = (R,0,H2)
lower_loop = f.edge_loop([
    f.oriented_edge(seam_lower_ec, True),   # bot → mid
    f.oriented_edge(mid_circ_ec,   True),   # full revolution at mid
    f.oriented_edge(seam_lower_ec, False),  # mid → bot
])
face1 = f.advanced_face([f.face_outer_bound(lower_loop)], cyl_surf)

# ── face[2]: top disc cap ──────────────────────────────────────────────────────
top_plane = f.plane(
    f.axis2_placement_3d(top_ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
)
face2 = f.advanced_face(
    [f.face_outer_bound(f.edge_loop([f.oriented_edge(top_circ_ec, True)]))],
    top_plane
)

# ── face[3]: bottom disc cap ────────────────────────────────────────────────────
bot_plane = f.plane(
    f.axis2_placement_3d(bot_ctr, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
)
face3 = f.advanced_face(
    [f.face_outer_bound(f.edge_loop([f.oriented_edge(bot_circ_ec, True)]))],
    bot_plane
)

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face0, face1, face2, face3])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa155.stp")
