"""Hea007 — Transferring parameter values between 3D curve and pcurve when
EDGE_CURVE has B_SPLINE_CURVE_WITH_KNOTS in 3D and a LINE pcurve with non-affine reparam.

Catalog claim: An EDGE_CURVE whose 3D curve is a non-uniform B_SPLINE_CURVE_WITH_KNOTS
and whose pcurve is a uniform LINE. The parameter ranges differ by a non-affine
reparameterization; naive linear remapping from one to the other produces wrong
sample points. ShapeAnalysis_TransferParameters::Perform must apply the actual
reparameterization map (via numerical inversion), rejecting if ill-conditioned.

OCC behavior: silently accepts (no diagnostic); spec-compliant kernels must reject.

Byte assertions:
  - contains(b'non_uniform_3d')
  - contains(b'uniform_pcurve')
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS(')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea007",
    defect=(
        "EDGE_CURVE with non-uniform B_SPLINE_CURVE_WITH_KNOTS 3D (4 ctrl pts, degree 2, "
        "non-uniform knots biased toward x=0) and uniform LINE pcurve (U=0..10); "
        "named 'non_uniform_3d' and 'uniform_pcurve'; "
        "3D arc-length and pcurve U-distance follow different monotone functions; "
        "ShapeAnalysis_TransferParameters::Perform must use numerical inversion, not linear remap; "
        "OCC silently accepts; spec-compliant kernel must reject"
    ),
)

# ── Plane for context ─────────────────────────────────────────────────────────
host_orig = f.cartesian_point((0.0, 0.0, 0.0))
host_zdir = f.direction((0.0, 0.0, 1.0))
host_xdir = f.direction((1.0, 0.0, 0.0))
host_plc  = f.axis2_placement_3d(host_orig, host_zdir, host_xdir)
host_plane = f.plane(host_plc, name="host")

# ── 3D curve: non-uniform B_SPLINE_CURVE_WITH_KNOTS (degree 2, 4 ctrl pts) ───
# Control points heavily biased toward the start: 0, 1, 7, 10
# Non-uniform knots: multiplicity (3,1,3), knot values (0.0, 0.2, 1.0)
# Arc-length advances non-linearly with parameter.
cp0 = f.cartesian_point((0.0, 0.0, 0.0), name="cp0")
cp1 = f.cartesian_point((1.0, 0.0, 0.0), name="cp1")
cp2 = f.cartesian_point((7.0, 0.0, 0.0), name="cp2")
cp3 = f.cartesian_point((10.0, 0.0, 0.0), name="cp3")

bspline_3d = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[cp0, cp1, cp2, cp3],
    knot_multiplicities=[3, 1, 3],
    knots=[0.0, 0.2, 1.0],
    name="non_uniform_3d",
)

# ── Edge vertices ─────────────────────────────────────────────────────────────
v_start = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0), name="start_pt"), name="Vstart")
v_end   = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0), name="end_pt"), name="Vend")

# ── Pcurve: uniform LINE U=0..10 ──────────────────────────────────────────────
# 2D points must use _emit_raw (cartesian_point always emits 3 coords)
uv_start = f._emit_raw("CARTESIAN_POINT('uv_start',(0.0,0.0))")
uv_dir   = f._emit_raw("DIRECTION('',(1.0,0.0))")
uv_vec   = f._emit_raw(f"VECTOR('',#{uv_dir.eid},10.0)")
uv_line  = f._emit_raw(f"LINE('uniform_pcurve',#{uv_start.eid},#{uv_vec.eid})")
geom_ctx_2d = f._emit_raw("GEOMETRIC_REPRESENTATION_CONTEXT(2)")
def_repr = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',( #{uv_line.eid}),#{geom_ctx_2d.eid})"
)
pcurve   = f._emit_raw(f"PCURVE('uniform_pcurve_in_repr',#{host_plane.eid},#{def_repr.eid})")
surf_curve = f._emit_raw(
    f"SURFACE_CURVE('non_affine_reparam',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# ── EDGE_CURVE and wire ───────────────────────────────────────────────────────
edge = f.edge_curve(v_start, v_end, surf_curve, name="non_uniform_3d_uniform_pcurve")
oe   = f.oriented_edge(edge, True)
loop = f.edge_loop([oe], name="single_non_affine_edge")

# No PRODUCT chain: EDGE_LOOP + SURFACE_CURVE is opaque to TransferRoots → empty shape
# Wrap in GEOMETRIC_CURVE_SET so the entity is referenced but OCC yields empty
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{loop.eid}))")
f.add_product_chain(gcs)

f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea007.stp")
