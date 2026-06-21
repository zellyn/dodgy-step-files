"""P014 — PCURVE start point shifted in V from 3D EDGE_CURVE lift (UV drift).

Catalog claim: faces emitted after a complex Boolean cut carry SURFACE_CURVE
whose PCURVE lies off the surface domain — beyond geometric tolerance.
Signature: a planar ADVANCED_FACE whose 3D edge runs from the origin along +X
but whose pcurve seed 2D point starts at (u=0.0, v=0.5), a 0.5 mm drift in V.
The source shape validates clean inside the producing kernel, but on STEP
re-import every face/edge is flagged "invalid curve on surface" — the
round-trip introduced UV drift the source did not have.

Byte assertions:
  count_entity_def(b'PCURVE') >= 1
  contains(b'SURFACE_CURVE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P014",
    defect=(
        "MANIFOLD_SOLID_BREP where ADVANCED_FACE carries SURFACE_CURVE with PCURVE "
        "whose 2D start point has v=0.5 drift from the 3D edge lift on the plane; "
        "PCURVE seed (0.0, 0.5) disagrees with 3D edge at (0.0, 0.0) by 0.5 mm; "
        "round-trip introduces UV drift beyond tolerance; "
        "importer flags every face/edge as 'invalid curve on surface'; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Minimal geometry payload: GEOMETRIC_CURVE_SET so shape is empty ───────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── The defect: SURFACE_CURVE with a drifted PCURVE ──────────────────────────
# Underlying planar surface: Z=0 plane.
surf_origin = f._emit_raw("CARTESIAN_POINT('surf_origin',(0.0,0.0,0.0))")
surf_z = f._emit_raw("DIRECTION('surf_z',(0.0,0.0,1.0))")
surf_x = f._emit_raw("DIRECTION('surf_x',(1.0,0.0,0.0))")
surf_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('surf_plc',#{surf_origin.eid},#{surf_z.eid},#{surf_x.eid})"
)
plane = f._emit_raw(f"PLANE('xy_plane',#{surf_plc.eid})")

# 3D edge: runs from (0,0,0) to (1,0,0) along +X.
e3d_dir = f._emit_raw("DIRECTION('e3d_dir',(1.0,0.0,0.0))")
e3d_vec = f._emit_raw(f"VECTOR('',#{e3d_dir.eid},1.0)")
e3d_start = f._emit_raw("CARTESIAN_POINT('e3d_start',(0.0,0.0,0.0))")
line_3d = f._emit_raw(f"LINE('edge_line',#{e3d_start.eid},#{e3d_vec.eid})")

# 2D PCURVE: same direction as 3D edge but starting at (u=0.0, v=0.5).
# This 0.5 mm drift in V is the defect.
pcurve_start_drifted = f._emit_raw(
    "CARTESIAN_POINT('pcurve_start_drifted',(0.0,0.5))"
)
pcurve_dir = f._emit_raw("DIRECTION('pcurve_dir',(1.0,0.0))")
pcurve_vec = f._emit_raw(f"VECTOR('',#{pcurve_dir.eid},1.0)")
pcurve_line = f._emit_raw(
    f"LINE('pcurve_line',#{pcurve_start_drifted.eid},#{pcurve_vec.eid})"
)

# DEFINITIONAL_REPRESENTATION for the PCURVE.
def_rep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{pcurve_line.eid}),#9010)"
)

# PCURVE: binds the 2D line (with drift) to the plane surface.
pcurve = f._emit_raw(f"PCURVE('',#{plane.eid},#{def_rep.eid})")

# SURFACE_CURVE: associates 3D line with the drifted PCURVE.
# This is the entity OCCT loads and will flag as "invalid curve on surface".
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# Wrap the surface_curve in a GEOMETRIC_CURVE_SET for the §12.6 geometry
# representation (separate from add_product_chain's gcs above).
defect_gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('defect_curves',(#{surface_curve.eid}))"
)

# ── NAUO scaffolding for §12.6 assembly-presence lint ─────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('PCurveDrift','PCurveDrift','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9003)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','pcurve_drift_instance','',#9004,#{sub_pdef.eid},$)"
)
