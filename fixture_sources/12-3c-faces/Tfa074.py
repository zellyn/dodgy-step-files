"""Tfa074 — ShapeFix_Face.FixWiresTwoCoincEdges orientation detection.

Catalog claim: Face with two identical edges [E, E] at FORWARD orientation in
single 2-edge wire. Orientation mismatch detection (line 2876) fails to
recognize that both edges are identical at same orientation, allowing coincident-
edge pattern to pass unmerged.

Mechanism: CLOSED_SHELL with two faces. face[0] is a PLANE with a 2-edge wire
where the same EDGE_CURVE appears twice with orientation .T. — the FixWiresTwoCoincEdges
defect. face[1] is a second valid plane face to give OCC shape(1). OCC heals
the coincident wire to produce a valid shell with 2 faces.

The outer wire of face[0] reuses edge E twice with .T. (FORWARD), representing
the case that orientation detection at line 2876 fails to catch.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 2

Expected: occt=shape(1)/shape(1) gmsh=shape(12) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa074",
    defect=(
        "CLOSED_SHELL with two faces; "
        "face[0]: PLANE at z=0, 2-edge wire using same EDGE_CURVE E twice with .T. (FORWARD); "
        "E runs V_left=(0,0,0)→V_right=(10,0,0); wire is [E .T., E .T.] — coincident same-orient loop; "
        "FixWiresTwoCoincEdges: orientation check at line 2876 fails to detect matching .T./.T. pair; "
        "merge should produce single 1-edge closed wire but is skipped; "
        "face[1]: valid 10×10 PLANE at z=1 — ensures OCC loads shape(1); "
        "OCC heals both faces — n_faces_total == 2; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# ── Shared vertices and shared edge E for the coincident-wire face ─────────────
p_left  = f.cartesian_point((0.0, 0.0, 0.0))
p_right = f.cartesian_point((10.0, 0.0, 0.0))
v_left  = f.vertex_point(p_left)
v_right = f.vertex_point(p_right)

# E: the single edge used twice (FORWARD both times)
ec_E = f.edge_curve(
    v_left, v_right,
    f.line(p_left, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
)

# ── face[0]: 2-edge wire with E used twice (THE DEFECT) ──────────────────────
# Wire: E .T. then E .T. — both identical and both FORWARD
defect_loop = f.edge_loop([
    f.oriented_edge(ec_E, True),
    f.oriented_edge(ec_E, True),
])
ax0 = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
face0 = f.advanced_face([f.face_outer_bound(defect_loop)], f.plane(ax0))

# ── face[1]: valid 10×10 PLANE at z=1 — companion face ────────────────────────
p00 = f.cartesian_point(( 0.0,  0.0, 1.0))
p10 = f.cartesian_point((10.0,  0.0, 1.0))
p11 = f.cartesian_point((10.0, 10.0, 1.0))
p01 = f.cartesian_point(( 0.0, 10.0, 1.0))

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)

ec0 = f.edge_curve(v00, v10, f.line(p00, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec1 = f.edge_curve(v10, v11, f.line(p10, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec2 = f.edge_curve(v11, v01, f.line(p11, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec3 = f.edge_curve(v01, v00, f.line(p01, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

good_loop = f.edge_loop([
    f.oriented_edge(ec0, True), f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True), f.oriented_edge(ec3, True),
])
ax1 = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 1.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
face1 = f.advanced_face([f.face_outer_bound(good_loop)], f.plane(ax1))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face0, face1])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa074.stp")
