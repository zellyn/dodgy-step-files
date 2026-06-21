"""M046 — PRESENTATION_LAYER_ASSIGNMENT carrying material/group names dropped.

Catalog claim: CST Microwave Studio encodes physical-group / material
semantics in PRESENTATION_LAYER_ASSIGNMENT rather than STYLED_ITEM.
OCC's XCAF only honors layer for visibility, not as named groups, so the
data is silently lost.

Reproducer recipe: STEP file with two SHELL_BASED_SURFACE_MODEL quads
each referenced by a PRESENTATION_LAYER_ASSIGNMENT whose name encodes
material semantics ('Copper', 'FR4') rather than visibility-only layers.

Tier-3 assertions:
  face[0].surface_type == "plane"
  n_edges_total >= 3

Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M046",
    schema="AP214",
    defect=(
        "PRESENTATION_LAYER_ASSIGNMENT carrying material/group names dropped; "
        "input: AP214 STEP file (CST Microwave Studio pattern) where "
        "PRESENTATION_LAYER_ASSIGNMENT('Copper','meshable',(#42,#43)) and "
        "PRESENTATION_LAYER_ASSIGNMENT('FR4','dielectric',(#44,#45)) "
        "encode physical-group and material semantics by pointing at "
        "SHELL_BASED_SURFACE_MODEL shells; "
        "OCC XCAF only honors PRESENTATION_LAYER_ASSIGNMENT for visibility; "
        "material names and physical group assignments are silently dropped; "
        "kernel must heal: surface PRESENTATION_LAYER_ASSIGNMENT names as "
        "queryable group attributes; "
        "synonyms: layer carrying material name dropped, physical group encoded as layer, "
        "PRESENTATION_LAYER_ASSIGNMENT semantic loss, layer-as-group not honored"
    ),
)

# ── Two planar quad shells: 'Copper' and 'FR4' material assignments ──────────
def _quad_face(p0, p1, p2, p3, name=""):
    v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
    v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
    dx01 = p1.args[1][0] - p0.args[1][0]; dy01 = p1.args[1][1] - p0.args[1][1]
    l01 = (dx01**2 + dy01**2) ** 0.5
    d01 = f.direction((dx01/l01, dy01/l01, 0.0)); vec01 = f.vector(d01, l01)
    line01 = f.line(p0, vec01); e01 = f.edge_curve(v0, v1, line01)
    dx12 = p2.args[1][0] - p1.args[1][0]; dy12 = p2.args[1][1] - p1.args[1][1]
    l12 = (dx12**2 + dy12**2) ** 0.5
    d12 = f.direction((dx12/l12, dy12/l12, 0.0)); vec12 = f.vector(d12, l12)
    line12 = f.line(p1, vec12); e12 = f.edge_curve(v1, v2, line12)
    dx23 = p3.args[1][0] - p2.args[1][0]; dy23 = p3.args[1][1] - p2.args[1][1]
    l23 = (dx23**2 + dy23**2) ** 0.5
    d23 = f.direction((dx23/l23, dy23/l23, 0.0)); vec23 = f.vector(d23, l23)
    line23 = f.line(p2, vec23); e23 = f.edge_curve(v2, v3, line23)
    dx30 = p0.args[1][0] - p3.args[1][0]; dy30 = p0.args[1][1] - p3.args[1][1]
    l30 = (dx30**2 + dy30**2) ** 0.5
    d30 = f.direction((dx30/l30, dy30/l30, 0.0)); vec30 = f.vector(d30, l30)
    line30 = f.line(p3, vec30); e30 = f.edge_curve(v3, v0, line30)
    loop = f.edge_loop([
        f.oriented_edge(e01, True), f.oriented_edge(e12, True),
        f.oriented_edge(e23, True), f.oriented_edge(e30, True),
    ])
    zdir = f.direction((0.0, 0.0, 1.0)); xdir = f.direction((1.0, 0.0, 0.0))
    plc = f.axis2_placement_3d(p0, zdir, xdir)
    plane = f.plane(plc)
    return f.advanced_face([f.face_outer_bound(loop)], plane, name=name)


# Copper trace: 2 mm x 1 mm patch at z=0
q0a = f.cartesian_point((0.0, 0.0, 0.0))
q1a = f.cartesian_point((2.0, 0.0, 0.0))
q2a = f.cartesian_point((2.0, 1.0, 0.0))
q3a = f.cartesian_point((0.0, 1.0, 0.0))
face_cu = _quad_face(q0a, q1a, q2a, q3a, name="copper_trace")
shell_cu = f.open_shell([face_cu], name="shell_copper")
sbsm_cu = f.shell_based_surface_model([shell_cu], name="sbsm_copper")

# FR4 substrate: 2 mm x 1 mm patch at z=-0.2 (below the copper)
q0b = f.cartesian_point((0.0, 0.0, -0.2))
q1b = f.cartesian_point((2.0, 0.0, -0.2))
q2b = f.cartesian_point((2.0, 1.0, -0.2))
q3b = f.cartesian_point((0.0, 1.0, -0.2))
face_fr4 = _quad_face(q0b, q1b, q2b, q3b, name="fr4_substrate")
shell_fr4 = f.open_shell([face_fr4], name="shell_fr4")
sbsm_fr4 = f.shell_based_surface_model([shell_fr4], name="sbsm_fr4")

# Wrap both SBSMs in a compound SBSM for the product chain
sbsm_all = f.shell_based_surface_model([shell_cu, shell_fr4], name="sbsm_all")
f.add_product_chain(sbsm_all)

# ── Defect: PRESENTATION_LAYER_ASSIGNMENT with material/group name semantics ──
# CST Microwave Studio encodes material assignments this way.
# OCC XCAF only uses layers for visibility — the material names are silently lost.
pla_copper = f._emit_raw(
    f"PRESENTATION_LAYER_ASSIGNMENT('Copper','meshable',"
    f"(#{sbsm_cu.eid},#{face_cu.eid}))"
)
pla_fr4 = f._emit_raw(
    f"PRESENTATION_LAYER_ASSIGNMENT('FR4','dielectric',"
    f"(#{sbsm_fr4.eid},#{face_fr4.eid}))"
)
# A third PLA encoding a physical group (e.g., for mesh boundary conditions)
pla_bc = f._emit_raw(
    f"PRESENTATION_LAYER_ASSIGNMENT('PortBoundary','excitation boundary',"
    f"(#{face_cu.eid}))"
)
