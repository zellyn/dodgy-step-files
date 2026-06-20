"""Tfa236 — ShapeFix_Face.FixOrientation

Wire-sense correction via face-surface normal evaluation; manifold
compatibility validation on planar outer boundary.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a PLANE. The face has a
rectangular EDGE_LOOP (4 line edges) forming a closed outer boundary. The wire
edges are wound in clockwise order (CW) when viewed from the outward normal of
the plane (i.e., the winding is opposite the expected CCW convention for an
outward-facing surface normal). Additionally, the FACE_OUTER_BOUND is given
orientation=False, which disagrees with the surface normal direction.

ShapeFix_Face::FixOrientation() evaluates the face normal at the surface
location, computes the wire winding, detects the sense mismatch, and flips
the edge orientations so that the wire becomes CCW — consistent with the
outward surface normal. This exercises the wire-sense correction path and the
manifold compatibility check on a planar outer boundary.

Byte assertions:
  - contains(b'PLANE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa236",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on PLANE; "
        "normal=(0,0,1) at z=0; "
        "4-edge EDGE_LOOP: CW winding (bl→tl→tr→br→bl) opposed to surface normal; "
        "FACE_OUTER_BOUND orientation=False: disagrees with normal direction; "
        "ShapeFix_Face::FixOrientation(): detects wire-sense mismatch via normal eval; "
        "flips edge orientations to CCW for manifold compatibility; "
        "wire-sense correction + manifold compatibility check path exercised; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE: z=0, normal=(0,0,1) ────────────────────────────────────────────────
pl_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
plane = f.plane(pl_plc)

# ── Corner points for a 2×1 rectangle ────────────────────────────────────────
p_bl = f.cartesian_point((0.0, 0.0, 0.0))  # bottom-left
p_tl = f.cartesian_point((0.0, 1.0, 0.0))  # top-left
p_tr = f.cartesian_point((2.0, 1.0, 0.0))  # top-right
p_br = f.cartesian_point((2.0, 0.0, 0.0))  # bottom-right

v_bl = f.vertex_point(p_bl)
v_tl = f.vertex_point(p_tl)
v_tr = f.vertex_point(p_tr)
v_br = f.vertex_point(p_br)

# ── Edges in CW order (bl→tl→tr→br→bl): wrong winding vs. normal ─────────────
# CW when viewed from +Z: this mismatches the outward-face normal convention.
e_left  = f.edge_curve(v_bl, v_tl, f.line(p_bl, f.vector(f.direction((0.0,  1.0, 0.0)), 1.0)))
e_top   = f.edge_curve(v_tl, v_tr, f.line(p_tl, f.vector(f.direction((1.0,  0.0, 0.0)), 2.0)))
e_right = f.edge_curve(v_tr, v_br, f.line(p_tr, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))
e_bot   = f.edge_curve(v_br, v_bl, f.line(p_br, f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0)))

# CW-wound loop: bl→tl→tr→br→bl
face_loop = f.edge_loop([
    f.oriented_edge(e_left,  True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_bot,   True),
])
# FACE_OUTER_BOUND orientation=False: further sense mismatch triggers FixOrientation
face_ob = f.face_outer_bound(face_loop, orientation=False)
face = f.advanced_face([face_ob], plane)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa236.stp")
