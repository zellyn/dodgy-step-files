"""Xp046 — Valid conical ADVANCED_FACE dropped by OCCT 7.7.x BRepMesh but
present in ≤7.6.1 / desktop CAD (kernel-VERSION differential, not a bad file).

Catalog claim (cross-oracle kernel-version differential): a fully valid,
watertight MANIFOLD_SOLID_BREP conical frustum. Its lateral face is exactly
one ADVANCED_FACE on a CONICAL_SURFACE (semi-angle 20°) bounded by two
CIRCLE edges (bottom r=10, top r≈15.46, height 15); the two caps are planar.

The file is NOT defective — every OCCT version PARSES it and loads a solid.
The defect is a mesher REGRESSION: on an OCCT-7.7.x BRepMesh the conical
ADVANCED_FACE yields ZERO triangles, so the solid renders with a hole (a
missing face); OCCT-7.6.1, CAD Assistant and other CAD tessellate all
faces. Same bytes → complete in one kernel version, defective in the next.

This is ORACLE-INVISIBLE to our single-version OCCT oracle: the file loads
as a normal solid; the divergence lives between kernel *versions*, which a
single-version harness cannot exhibit. Provenance tier runtime-only.

Distinct from Gd*/Gn014 (conical-canonical INPUT-geometry defects) and
Pf021 (near-apex healing): those are bad-geometry inputs; here the geometry
is valid and the regression is in the receiver's mesher version.

Byte assertions:
  contains(b'CONICAL_SURFACE')
  count_entity_def(b'CONICAL_SURFACE') == 1
  contains(b'MANIFOLD_SOLID_BREP')

Tier-3 assertion:
  load == "ok"                       # valid solid: every version loads it
  face[0].surface_type == "cone"

Expected (any single version loads it; the drop is version-differential):
  occt=shape(1)/shape(1) gmsh=shape(5) ifc=schema_n/a  (gmsh count PROVISIONAL)
"""
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Xp046",
    defect=(
        "valid watertight MANIFOLD_SOLID_BREP conical frustum: one "
        "ADVANCED_FACE on a CONICAL_SURFACE (semi-angle 20°) bounded by two "
        "CIRCLE edges, plus two planar caps; the file loads a solid in every "
        "OCCT version, but OCCT-7.7.x BRepMesh emits zero triangles for the "
        "conical face (regression) so the solid renders with a hole while "
        "≤7.6.1 / CAD Assistant tessellate all faces — a kernel-version "
        "mesher differential, not an input defect"
    ),
)

SEMI = _math.radians(20.0)
R0 = 10.0          # bottom radius (at z=0 of the cone's local frame)
H = 15.0           # frustum height
R1 = R0 + H * _math.tan(SEMI)   # top radius

# ── CONICAL_SURFACE (axis +Z through origin, radius R0 at z=0) ────────────────
cn_orig = f.cartesian_point((0.0, 0.0, 0.0))
cn_z = f.direction((0.0, 0.0, 1.0))
cn_x = f.direction((1.0, 0.0, 0.0))
cn_plc = f.axis2_placement_3d(cn_orig, cn_z, cn_x)
cone = f.conical_surface(cn_plc, R0, SEMI)

# ── Bottom circle edge (z=0, r=R0) — shared by cone face and bottom cap ───────
b_ctr = f.cartesian_point((0.0, 0.0, 0.0))
b_z = f.direction((0.0, 0.0, 1.0))
b_x = f.direction((1.0, 0.0, 0.0))
b_plc = f.axis2_placement_3d(b_ctr, b_z, b_x)
b_circle = f.circle(b_plc, R0)
b_pt = f.cartesian_point((R0, 0.0, 0.0))
b_v = f.vertex_point(b_pt)
b_edge = f.edge_curve(b_v, b_v, b_circle)   # full closed circle (start==end)

# ── Top circle edge (z=H, r=R1) — shared by cone face and top cap ─────────────
t_ctr = f.cartesian_point((0.0, 0.0, H))
t_z = f.direction((0.0, 0.0, 1.0))
t_x = f.direction((1.0, 0.0, 0.0))
t_plc = f.axis2_placement_3d(t_ctr, t_z, t_x)
t_circle = f.circle(t_plc, R1)
t_pt = f.cartesian_point((R1, 0.0, H))
t_v = f.vertex_point(t_pt)
t_edge = f.edge_curve(t_v, t_v, t_circle)   # full closed circle (start==end)

# ── Lateral CONICAL_SURFACE face bounded by both circles ──────────────────────
cone_outer = f.face_outer_bound(f.edge_loop([f.oriented_edge(b_edge, True)]))
cone_inner = f._emit_raw(
    f"FACE_BOUND('',#{f.edge_loop([f.oriented_edge(t_edge, False)]).eid},.T.)"
)
cone_face = f.advanced_face([cone_outer, cone_inner], cone)

# ── Bottom planar cap (plane z=0, outward normal -Z) ──────────────────────────
bp_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
bplane = f.plane(bp_plc)
bcap_face = f.advanced_face(
    [f.face_outer_bound(f.edge_loop([f.oriented_edge(b_edge, False)]))], bplane
)

# ── Top planar cap (plane z=H, outward normal +Z) ─────────────────────────────
tp_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, H)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
tplane = f.plane(tp_plc)
tcap_face = f.advanced_face(
    [f.face_outer_bound(f.edge_loop([f.oriented_edge(t_edge, True)]))], tplane
)

# ── Watertight solid: cone face first so tier-3 face[0] is the cone ──────────
shell = f.closed_shell([cone_face, bcap_face, tcap_face])
brep = f.manifold_solid_brep(shell)
f.add_product_chain(brep, mode="brep_shape")
