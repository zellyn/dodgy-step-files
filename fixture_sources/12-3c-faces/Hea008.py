"""Hea008 — Transfer parameters using projection (not affine remapping).

Catalog claim: An edge on a B_SPLINE_SURFACE_WITH_KNOTS whose control net has
very high curvature on one side (control points clustered) — the surface metric
varies by ~10× across the edge length. Affine UV remapping produces wrong sample
points; projection-based transfer (ShapeAnalysis_TransferParametersProj::Perform)
is required: for each sample, project the 3D-curve point onto the surface and
recover the UV parameter from the projection.

OCC behavior: silently accepts (no diagnostic); spec-compliant kernels must
heal or reject.

Byte assertions:
  - contains(b'non_uniform_metric')
  - contains(b'B_SPLINE_SURFACE_WITH_KNOTS(')
  - contains(b'cluster_lo_a')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea008",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS named 'non_uniform_metric' with 4x4 control grid: "
        "left side (U=0) clustered in x=[0,1] (control points 'cluster_lo_a'...'cluster_lo_d'), "
        "right side (U=1) spread to x=[20,20] -- surface metric varies ~10x along U; "
        "edge spans full U range with uniform UV pcurve (U=0..1, V=0.5); "
        "affine remapping gives wrong 3D samples; projection-based transfer required; "
        "wrapped in GEOMETRIC_CURVE_SET; OCC silently accepts; spec-kernel must heal/reject"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS with 4×4 control points ──────────────────────
# Left columns (U~0): x in [0,1] (clustered) → high metric
# Right columns (U~1): x in [10,20] (spread) → high metric variation
# V direction: y in [0,3] (uniform)
# degree 3, knot vectors uniform [0,1]

# 4 columns (U direction) × 4 rows (V direction)
# Control points named to include 'cluster_lo_a' etc. for byte assertions
cp = {}
col_data = [
    # (col_idx, x, prefix)
    (0, 0.0,  "cluster_lo"),
    (1, 1.0,  "cluster_mid"),
    (2, 10.0, "spread_mid"),
    (3, 20.0, "spread_hi"),
]
v_ys = [0.0, 1.0, 2.0, 3.0]
row_labels = ['a', 'b', 'c', 'd']

grid_entities = []
for col_idx, x, prefix in col_data:
    row_ents = []
    for row_idx, y in enumerate(v_ys):
        label = row_labels[row_idx]
        name = f"{prefix}_{label}"
        pt = f.cartesian_point((x, y, 0.0), name=name)
        row_ents.append(pt)
    grid_entities.append(row_ents)

# grid_entities[col][row] — outer=U, inner=V
surf = f.b_spline_surface_with_knots(
    u_degree=3,
    v_degree=3,
    control_points_grid=grid_entities,
    u_multiplicities=[4, 4],
    v_multiplicities=[4, 4],
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 1.0],
    name="non_uniform_metric",
)

# ── Edge: spans full U range at V=0.5 ────────────────────────────────────────
# 3D start: (0, 1.5, 0), end: (20, 1.5, 0) — linear in 3D
p_start = f.cartesian_point((0.0, 1.5, 0.0), name="e_start")
p_end   = f.cartesian_point((20.0, 1.5, 0.0), name="e_end")
v_start = f.vertex_point(p_start, name="Vstart")
v_end   = f.vertex_point(p_end, name="Vend")
d3_dir  = f.direction((1.0, 0.0, 0.0))
d3_line = f.line(p_start, f.vector(d3_dir, 1.0), name="e_3d")

# ── Pcurve: linear U=0..1, V=0.5 in UV ───────────────────────────────────────
uv_s  = f._emit_raw("CARTESIAN_POINT('uv_start',(0.0,0.5))")
uv_d  = f._emit_raw("DIRECTION('',(1.0,0.0))")
uv_v  = f._emit_raw(f"VECTOR('',#{uv_d.eid},1.0)")
uv_ln = f._emit_raw(f"LINE('e_pcurve',#{uv_s.eid},#{uv_v.eid})")

host_z   = f.direction((0.0, 0.0, 1.0), name="host_z")
host_ax  = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('host_repr',#{grid_entities[0][0].eid},#{host_z.eid},#{d3_dir.eid})"
)
geom_2d  = f._emit_raw("GEOMETRIC_REPRESENTATION_CONTEXT(2)")
def_repr = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',( #{uv_ln.eid}),#{geom_2d.eid})"
)
pcurve   = f._emit_raw(f"PCURVE('e_pcurve_uv_lin',#{surf.eid},#{def_repr.eid})")
sc       = f._emit_raw(
    f"SURFACE_CURVE('proj_required',#{d3_line.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

edge = f.edge_curve(v_start, v_end, sc, name="e_on_nonuniform_metric_surface")
oe   = f.oriented_edge(edge, True)
loop = f.edge_loop([oe], name="proj_transfer_required_edge")

# Wrap in GEOMETRIC_CURVE_SET → TransferRoots returns empty (no PRODUCT chain)
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{loop.eid}))")
f.add_product_chain(gcs)

f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea008.stp")
