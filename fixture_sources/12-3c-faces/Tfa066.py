"""Tfa066 — Pipe-like face with seam edge wrongly removed as "small".

Catalog claim: A long thin pipe face (length >> width, e.g., 100 × 0.1 mm)
has a seam edge from the closed surface. A "small face" detector classifies
it as small because its bounding-box width is below threshold and removes
it; losing a structurally significant part of the shell.

Mechanism: CLOSED_SHELL with a cylindrical pipe face and two end-cap discs.
  face[0]: ADVANCED_FACE on CYLINDRICAL_SURFACE, length=100mm, radius=0.05mm
    (so bounding-box width ≈ 0.1mm). The full-revolution seam edge is present
    as two ORIENTED_EDGEs in the EDGE_LOOP (seam .T. and seam .F.).
    Small-face detector with width threshold 0.5mm flags it for removal
    because 0.1mm < 0.5mm — even though the face has area = 2π*0.05*100 ≈ 31mm².
    The seam edge is structurally significant for the closed shell.
  face[1]: bottom disc cap (z=0)
  face[2]: top disc cap (z=L)

Tier-3 assertions:
  face[0].surface_type == "cylinder"
  n_edges_total >= 5
  n_vertices_total >= 8
  brepcheck.valid == True

Expected: occt=shape(1)/shape(1) gmsh=shape(8) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa066",
    defect=(
        "CLOSED_SHELL: cylindrical pipe face length=100mm, radius=0.05mm; "
        "bounding-box width ≈ 0.1mm < small-face width threshold 0.5mm; "
        "small-face detector classifies as 'small' by bbox width instead of area; "
        "seam EDGE_CURVE used .T. and .F. in same EDGE_LOOP (full revolution); "
        "face area ≈ 2pi*0.05*100 ≈ 31mm² — NOT small by area; "
        "ShapeFix_FixSmallFace must use area not bbox minor dimension; "
        "face[1,2] are valid bottom/top disc caps; "
        "defect IS on live cylindrical face traversal path"
    ),
)

R = 0.05   # radius — tiny, bbox width ≈ 0.1mm < 0.5mm threshold
L = 100.0  # length — very long, area ≈ 31mm²

# ── Vertices: seam at (R, 0, z) ───────────────────────────────────────────────
pt_seam_bot = f.cartesian_point((R, 0.0, 0.0))
pt_seam_top = f.cartesian_point((R, 0.0, L))

v_seam_bot = f.vertex_point(pt_seam_bot)
v_seam_top = f.vertex_point(pt_seam_top)

# ── Seam edge: vertical line v_seam_bot → v_seam_top ──────────────────────────
seam_line = f.line(pt_seam_bot, f.vector(f.direction((0.0, 0.0, 1.0)), L))
seam_ec   = f.edge_curve(v_seam_bot, v_seam_top, seam_line)

# ── Bottom circle: closed at v_seam_bot ───────────────────────────────────────
bot_ctr = f.cartesian_point((0.0, 0.0, 0.0))
bot_circ_ec = f.edge_curve(
    v_seam_bot, v_seam_bot,
    f.circle(f.axis2_placement_3d(
        bot_ctr, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0))
    ), R)
)

# ── Top circle: closed at v_seam_top ──────────────────────────────────────────
top_ctr = f.cartesian_point((0.0, 0.0, L))
top_circ_ec = f.edge_curve(
    v_seam_top, v_seam_top,
    f.circle(f.axis2_placement_3d(
        top_ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))
    ), R)
)

# ── CYLINDRICAL_SURFACE: axis +Z, radius R ────────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_surf = f.cylindrical_surface(
    f.axis2_placement_3d(cyl_orig, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
    R
)

# ── face[0]: full-revolution cylindrical face (THE DEFECT — long thin pipe) ───
# Wire: seam .T. (bot→top), top_circle .T. (closed), seam .F. (top→bot), bot_circle .F.
cyl_loop = f.edge_loop([
    f.oriented_edge(seam_ec,      True),   # bot→top seam going up
    f.oriented_edge(top_circ_ec,  True),   # top circle (full revolution)
    f.oriented_edge(seam_ec,      False),  # top→bot seam going down
    f.oriented_edge(bot_circ_ec,  False),  # bottom circle (reversed)
])
face0 = f.advanced_face([f.face_outer_bound(cyl_loop)], cyl_surf)

# ── face[1]: bottom disc cap ───────────────────────────────────────────────────
face1 = f.advanced_face(
    [f.face_outer_bound(f.edge_loop([f.oriented_edge(bot_circ_ec, True)]))],
    f.plane(f.axis2_placement_3d(
        f.cartesian_point((0.0, 0.0, 0.0)),
        f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0))
    ))
)

# ── face[2]: top disc cap ──────────────────────────────────────────────────────
face2 = f.advanced_face(
    [f.face_outer_bound(f.edge_loop([f.oriented_edge(top_circ_ec, True)]))],
    f.plane(f.axis2_placement_3d(
        f.cartesian_point((0.0, 0.0, L)),
        f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))
    ))
)

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face0, face1, face2])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa066.stp")
