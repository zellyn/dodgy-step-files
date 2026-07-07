"""P011 — AP242 PMI / GD&T / kinematics annotations silently discarded.

Catalog claim: AP242 files carry semantic PMI (dimensional / geometric
tolerances, datum features), graphic PMI, saved views, clipping planes,
materials, kinematic joints, design-history attributes. OCCT silently discards
these; the geometric BREP imports but assembly is dimensionally context-less.

The defect: AP242-ed2 file emitting GD&T tolerances on faces, plus kinematic
joints, plus saved camera views. OCCT silently discards all PMI entities.
A robust kernel must at minimum warn-and-accept with diagnostics listing
dropped entity types; never silently discard PMI.

OCC behavior: crashes with signal(11) on kinematic joint chain.

Byte assertions:
  contains(b'GEOMETRIC_TOLERANCE_WITH_DATUM_REFERENCE')
  contains(b'KINEMATIC_JOINT') or contains(b'MECHANISM')
  declared_schema.startswith(b'AP242')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=signal(11) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P011",
    defect=(
        "AP242-ed2 file with GEOMETRIC_TOLERANCE_WITH_DATUM_REFERENCE on faces; "
        "KINEMATIC_JOINT / MECHANISM chain for kinematic assembly; "
        "OCCT silently discards all PMI and kinematic entities — "
        "geometric BREP imports but no tolerances, no joints, no saved views; "
        "kernel must warn-and-accept with diagnostics, never silently discard; "
        "crashes with signal(11) on kinematic joint chain; "
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE scaffolding for §12.6 lint; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Minimal geometry ──────────────────────────────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── Datum feature reference ───────────────────────────────────────────────────
# DATUM entities referenced by the GD&T tolerance.
datum_origin = f.cartesian_point((0.0, 0.0, 0.0))
datum_zdir = f.direction((0.0, 0.0, 1.0))
datum_xdir = f.direction((1.0, 0.0, 0.0))
datum_plc = f.axis2_placement_3d(datum_origin, datum_zdir, datum_xdir)

datum_feat = f._emit_raw(
    f"DATUM_FEATURE('datum_A',#{datum_plc.eid})"
)
datum = f._emit_raw(
    f"DATUM('A','',#{datum_feat.eid},$)"
)
datum_ref = f._emit_raw(
    f"DATUM_REFERENCE('A_ref',1.0,#{datum.eid})"
)
datum_ref_modifier = f._emit_raw(
    f"DATUM_REFERENCE_MODIFIER_WITH_VALUE(.MAXIMUM_MATERIAL_REQUIREMENT.,#{datum_ref.eid})"
)

# ── GEOMETRIC_TOLERANCE_WITH_DATUM_REFERENCE: e.g., position tolerance ────────
# Tolerance zone definition.
tol_value = f._emit_raw(
    "LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.05),#9056)"
)
tol_zone_form = f._emit_raw(
    "TOLERANCE_ZONE_FORM('cylindrical')"
)
tol_zone_def = f._emit_raw(
    f"TOLERANCE_ZONE_DEFINITION(#{tol_zone_form.eid},$)"
)
# GEOMETRIC_TOLERANCE_WITH_DATUM_REFERENCE — key byte assertion entity.
geom_tol = f._emit_raw(
    f"GEOMETRIC_TOLERANCE_WITH_DATUM_REFERENCE("
    f"'pos_tol','',LENGTH_MEASURE(0.05),#9056,"
    f"#{datum_plc.eid},$,"
    f"(#{datum_ref.eid}))"
)

# ── KINEMATIC_JOINT / MECHANISM chain ────────────────────────────────────────
# Simple revolute kinematic joint between two sub-shapes.
# This chain causes signal(11) in OCCT's kinematic importer.
joint_origin = f.cartesian_point((0.0, 0.0, 0.0))
joint_zdir = f.direction((0.0, 0.0, 1.0))
joint_xdir = f.direction((1.0, 0.0, 0.0))
joint_plc = f.axis2_placement_3d(joint_origin, joint_zdir, joint_xdir)

kinematic_joint = f._emit_raw(
    f"KINEMATIC_JOINT('revolute_joint',#{joint_plc.eid})"
)
mechanism = f._emit_raw(
    f"MECHANISM('assembly_mech',(#{kinematic_joint.eid}))"
)
kinematic_link = f._emit_raw(
    f"KINEMATIC_LINK('link1',#{mechanism.eid},$)"
)

# ── NAUO scaffolding for §12.6 assembly-presence lint ────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('PMIAssembly','PMIAssembly','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','pmi_assy_instance','',#9054,#{sub_pdef.eid},$)"
)
