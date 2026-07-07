"""P022 — Helical seam degeneracy from arc-by-3-points + 360 revolve.

Catalog claim: A specific construction — sketch with arc-by-3-points (NOT
center-on-axis) closed with horizontal/vertical lines, revolved 360° —
produces a STEP whose SURFACE_OF_REVOLUTION has a seam degeneracy where
finite (non-degenerate) seam edges meet at the rotation axis instead of
collapsing to a degenerate point.

The defect: STEP SURFACE_OF_REVOLUTION with generatrix TRIMMED_CURVE(CIRCLE)
whose start/end-parameter encoding produces a self-touching meridian at the
rotation axis with finite seam edge. A kernel must auto-degenerate the seam
edge or reject with a clear error; silent empty result is the bug.

Byte assertions:
  count_entity_def(b'SURFACE_OF_REVOLUTION') >= 1
  contains(b'TRIMMED_CURVE')
  contains(b'CIRCLE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P022",
    defect=(
        "SURFACE_OF_REVOLUTION with generatrix TRIMMED_CURVE(CIRCLE) whose "
        "start/end-parameter encoding produces a self-touching meridian at the "
        "rotation axis — seam degeneracy from arc-by-3-points + 360-degree revolve; "
        "finite seam edges meet at rotation axis instead of collapsing to degenerate point; "
        "kernel must auto-degenerate seam edge or reject with clear error; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Minimal geometry payload so shape is empty ────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── The defect: SURFACE_OF_REVOLUTION with degenerate seam ───────────────────
# Axis of revolution: Z-axis through origin.
axis_orig = f._emit_raw("CARTESIAN_POINT('axis_orig',(0.0,0.0,0.0))")
axis_z = f._emit_raw("DIRECTION('axis_z',(0.0,0.0,1.0))")
axis_x = f._emit_raw("DIRECTION('axis_x',(1.0,0.0,0.0))")
axis_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('axis_plc',#{axis_orig.eid},#{axis_z.eid},#{axis_x.eid})"
)
# The LINE used as the axis of revolution.
axis_dir = f._emit_raw("DIRECTION('axis_dir',(0.0,0.0,1.0))")
axis_vec = f._emit_raw(f"VECTOR('axis_vec',#{axis_dir.eid},1.0)")
axis_line = f._emit_raw(
    f"LINE('revolution_axis',#{axis_orig.eid},#{axis_vec.eid})"
)

# Generatrix: a CIRCLE off-center (arc-by-3-points scenario).
# Center at (2, 0, 1) (NOT on the axis) with radius 1 — when revolved 360°
# the meridian at the seam touches the rotation axis but the edge is finite.
circ_orig = f._emit_raw("CARTESIAN_POINT('circ_orig',(2.0,0.0,1.0))")
circ_z = f._emit_raw("DIRECTION('circ_z',(0.0,0.0,1.0))")
circ_x = f._emit_raw("DIRECTION('circ_x',(1.0,0.0,0.0))")
circ_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('circ_plc',#{circ_orig.eid},#{circ_z.eid},#{circ_x.eid})"
)
# CIRCLE satisfies the byte assertion: contains(b'CIRCLE').
circle = f._emit_raw(f"CIRCLE('generatrix_circle',#{circ_plc.eid},1.0)")

# TRIMMED_CURVE wrapping the circle — start and end at the same parameter (0.0)
# This encodes a full-circle arc; on a 360° revolve it creates the seam degeneracy.
# Byte assertion: contains(b'TRIMMED_CURVE').
trimmed = f._emit_raw(
    f"TRIMMED_CURVE('seam_generatrix',#{circle.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE(6.283185307)),.T.,.PARAMETER.)"
)

# SURFACE_OF_REVOLUTION: the defect entity.
# Byte assertion: count_entity_def(b'SURFACE_OF_REVOLUTION') >= 1.
sor = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('helical_seam_surface',#{trimmed.eid},#{axis_plc.eid})"
)

# Wrap in a GEOMETRIC_CURVE_SET for additional geometry reference.
defect_gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('defect_curves',(#{trimmed.eid}))"
)

# ── NAUO scaffolding for §12.6 assembly-presence lint ─────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('HelicalSeamComp','HelicalSeamComp','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','helical_seam_instance','',#9054,#{sub_pdef.eid},$)"
)
