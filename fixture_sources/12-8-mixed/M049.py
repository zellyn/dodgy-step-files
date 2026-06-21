"""M049 — Schema migration: 53 retired kinematics entities (AP242 Ed.1).

Catalog claim: AP242 Ed.1 retired ~53 AP214/AP203 entities; an archived AP214
file containing them cannot be re-validated against the AP242 schema.

Reproducer recipe: An AP214 Part 21 file using kinematic_link_representation_relation
re-headered as AP242.

Byte assertions:
  contains(b'KINEMATIC_LINK_REPRESENTATION_RELATION')
  contains(b'CYLINDRICAL_PAIR_RANGE')
  contains(b'MECHANISM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M049",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing retired AP214 kinematics entities "
        "re-headered as AP242 — schema-version vs entity-vocabulary mismatch; "
        "input: AP242 STEP file (re-headered AP214) containing "
        "KINEMATIC_LINK_REPRESENTATION_RELATION, CYLINDRICAL_PAIR_RANGE, and "
        "MECHANISM — all retired in AP242 Ed.1; "
        "ISO 10303 AP242 Ed.1 (M016 / STEP Tools 'AP242 First Edition Notes'): "
        "approximately 53 AP214/AP203 kinematic entities were removed; a file "
        "using them cannot be validated against the AP242 schema; "
        "kernel must either refuse migration (schema-version mismatch) or "
        "record loss-of-fidelity and drop the retired entities; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: AP242 retired kinematics entities, schema-version vs entity-vocabulary "
        "disagreement, kinematic_structure entity gone, AP214 kinematics not in AP242 Ed.1"
    ),
)

# ── Kinematic joint geometry ───────────────────────────────────────────────────
joint_pt = f._emit_raw("CARTESIAN_POINT('joint_origin',(0.,0.,0.))")
joint_dir_z = f._emit_raw("DIRECTION('joint_axis',(0.,0.,1.))")
joint_dir_x = f._emit_raw("DIRECTION('joint_ref',(1.,0.,0.))")
joint_placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('joint_placement',"
    f"#{joint_pt.eid},#{joint_dir_z.eid},#{joint_dir_x.eid})"
)

# ── MECHANISM — retired AP214 kinematic entity ─────────────────────────────────
# Byte assertion: contains(b'MECHANISM')
mechanism = f._emit_raw(
    "MECHANISM('crank_slider_mechanism','$')"
)

# ── CYLINDRICAL_PAIR_RANGE — retired AP214 kinematic entity ───────────────────
# Byte assertion: contains(b'CYLINDRICAL_PAIR_RANGE')
cyl_pair_range = f._emit_raw(
    f"CYLINDRICAL_PAIR_RANGE('cyl_joint_limits',#{mechanism.eid},"
    f"-3.14159,3.14159,-100.,100.)"
)

# ── KINEMATIC_LINK_REPRESENTATION_RELATION — retired AP214 entity ─────────────
# Byte assertion: contains(b'KINEMATIC_LINK_REPRESENTATION_RELATION')
link_rep_rel = f._emit_raw(
    f"KINEMATIC_LINK_REPRESENTATION_RELATION('link_rep_rel',"
    f"#{mechanism.eid},#{joint_placement.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('ap242-retired-kinematics-schema-mismatch',"
    f"(#{mechanism.eid},#{cyl_pair_range.eid},#{link_rep_rel.eid},"
    f"#{joint_placement.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M049.stp")
