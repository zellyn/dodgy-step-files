"""Gn165 — Ill-Conditioned Knot Spacing (44:1 Ratio).

Catalog claim: Clustered interior knots create numerical instability.
BRepLib::SameParameter knot anomaly detection (critratio > 10) triggers
arc-length reparametrization.

Mechanism: The B-spline surface with 44:1 knot ratio IS the face_geometry,
wired into OPEN_SHELL → SHELL_BASED_SURFACE_MODEL.

Knot vector: [0.0, 0.0, 0.0, 0.022, 0.978, 1.0, 1.0, 1.0] — interior knots at
0.022 and 0.978 create two tiny spans (0.022, 0.022) and (0.022, 0.022) flanking
a large central span (0.956). Ratio of largest to smallest interior span = 0.956/0.022 ≈ 43.5:1.

Tier-3 assertion: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn165",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS U-deg 3, V-deg 1; 5x2 poles; "
        "U-knots (0.0,0.022,0.978,1.0) mults (3,1,1,3) sum=8=5+3+1 ✓; "
        "44:1 knot ratio (0.956 / 0.022) triggers BRepLib::SameParameter "
        "critratio > 10 → arc-length reparametrization → empty; IS face_geometry"
    ),
)

# 5 U-rows × 2 V-cols; U-degree=3, V-degree=1.
# U-knots: (0.0, 0.022, 0.978, 1.0) mults (3,1,1,3) sum=8=5+3+1 ✓
# V-knots: (0.0, 1.0) mults (2,2) sum=4=2+1+1 ✓
# Interior U intervals: 0.022, 0.956, 0.022 → 44:1 max-to-min ratio
surf_pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.000, 0.0, 0.0), (0.000, 1.0, 0.0)],    # U=0
    [(0.022, 0.0, 0.05), (0.022, 1.0, 0.05)],  # U=1 (dense cluster)
    [(0.500, 0.0, 0.1),  (0.500, 1.0, 0.1)],   # U=2 (wide central)
    [(0.978, 0.0, 0.05), (0.978, 1.0, 0.05)],  # U=3 (dense cluster)
    [(1.000, 0.0, 0.0),  (1.000, 1.0, 0.0)],   # U=4
]]
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in surf_pts)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn165_ill_knot',3,1,"
    f"({grid}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,1,1,3),(2,2),"
    f"(0.0,0.022,0.978,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# Minimal edge wiring
p_s = f.cartesian_point((0.0, 0.0, 0.0))
p_e = f.cartesian_point((1.0, 0.0, 0.0))
v_s = f.vertex_point(p_s)
v_e = f.vertex_point(p_e)
d_x = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 1.0)
line3d = f.line(p_s, vec_x)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
uv_s  = f.cartesian_point((0.0, 0.0))
uv_d  = f.direction((1.0, 0.0))
uv_v  = f.vector(uv_d, 1.0)
uv_ln = f.line(uv_s, uv_v)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn165_pcdef',(#{uv_ln.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn165_uv',#{surf.eid},#{defrep.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('gn165_sc',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('gn165_edge',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
