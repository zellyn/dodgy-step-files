"""M013 — Saved-view supplemental geometry split across multiple CGRs.

Catalog claim: A part may have many supplemental elements but only some belong
in a particular Saved View. Recommended pattern is one global CGR with all
elements PLUS additional shape_representation instances tagged with
description_attribute = 'supplemental geometry subset'.

Reproducer recipe: Two saved views; ten supplemental planes total; views 1 and 2
each show a different subset of three planes via two shape_representations tagged
with the magic description.

Byte assertions:
  contains(b'CONSTRUCTIVE_GEOMETRY_REPRESENTATION')
  contains(b'supplemental geometry subset')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M013",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing CONSTRUCTIVE_GEOMETRY_REPRESENTATION with 10 planes, "
        "plus two SHAPE_REPRESENTATIONs tagged with DESCRIPTION_ATTRIBUTE "
        "'supplemental geometry subset' for two saved views; "
        "each view subset holds 3 of the 10 planes; "
        "split across multiple CGRs without the recommended global-CGR-plus-subset pattern; "
        "kernel must read the magic description and treat those shape_representations as "
        "supplemental subsets, not as part geometry; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: saved view supplemental split, CGR scattered across views, "
        "supplemental geometry in multiple representations, saved-view subset CGR"
    ),
)

# ── Unit context for supplemental representations ─────────────────────────────
length_unit = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
angle_unit  = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
solid_unit  = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc_ent     = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),"
    f"#{length_unit.eid},'distance_accuracy_value','')"
)
geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_ent.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{length_unit.eid},#{angle_unit.eid},#{solid_unit.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

# ── Ten supplemental planes at different Z heights ────────────────────────────
planes = []
for i in range(10):
    orig = f.cartesian_point((0.0, 0.0, float(i) * 10.0))
    zdir = f.direction((0.0, 0.0, 1.0))
    xdir = f.direction((1.0, 0.0, 0.0))
    plc  = f.axis2_placement_3d(orig, zdir, xdir)
    pl   = f._emit_raw(f"PLANE('datum_plane_{i}',#{plc.eid})")
    planes.append(pl)

# ── Global CGR: all 10 planes ─────────────────────────────────────────────────
all_refs = ",".join(f"#{p.eid}" for p in planes)
global_cgr = f._emit_raw(
    f"CONSTRUCTIVE_GEOMETRY_REPRESENTATION('all_supplemental_planes',"
    f"({all_refs}),#{geom_ctx.eid})"
)

# ── View 1 subset: planes 0, 1, 2 ────────────────────────────────────────────
view1_refs = ",".join(f"#{planes[i].eid}" for i in range(3))
view1_rep = f._emit_raw(
    f"SHAPE_REPRESENTATION('view1_subset',({view1_refs}),#{geom_ctx.eid})"
)
# DESCRIPTION_ATTRIBUTE marks this as a 'supplemental geometry subset' for a saved view
# Byte assertion: contains(b'supplemental geometry subset')
view1_desc = f._emit_raw(
    f"DESCRIPTION_ATTRIBUTE('supplemental geometry subset',#{view1_rep.eid})"
)

# ── View 2 subset: planes 5, 6, 7 ────────────────────────────────────────────
view2_refs = ",".join(f"#{planes[i].eid}" for i in [5, 6, 7])
view2_rep = f._emit_raw(
    f"SHAPE_REPRESENTATION('view2_subset',({view2_refs}),#{geom_ctx.eid})"
)
view2_desc = f._emit_raw(
    f"DESCRIPTION_ATTRIBUTE('supplemental geometry subset',#{view2_rep.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('saved-view-supplemental-split',"
    f"({all_refs},#{global_cgr.eid},#{view1_rep.eid},#{view2_rep.eid},"
    f"#{view1_desc.eid},#{view2_desc.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M013.stp")
