"""Pmi091 — ROUND_HOLE internal_diameter exceeds host face's bounded extent.

Catalog claim: AP242 ROUND_HOLE feature whose stated diameter (50 mm) is
larger than the host face's smallest extent (30 mm). A 30×30 mm planar
ADVANCED_FACE hosts a ROUND_HOLE whose internal_diameter is 50 mm — the
hole definition cannot fit on the face. Receivers must reject or warn
deterministically; silent acceptance leaves a malformed feature.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 899 and < 901

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi091",
    defect=(
        "ROUND_HOLE SHAPE_ASPECT with internal_diameter DIMENSIONAL_SIZE 50.0 mm "
        "on a 30x30 mm host ADVANCED_FACE — hole bigger than face; "
        "receiver must reject or warn"
    ),
)

# ── 30×30 mm planar face (the host) ──────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((30.0, 0.0, 0.0))
p2 = f.cartesian_point((30.0, 30.0, 0.0))
p3 = f.cartesian_point((0.0, 30.0, 0.0))

loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="host_face")
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# ── DEFECT: ROUND_HOLE feature whose diameter (50 mm) exceeds face (30 mm) ───
# ROUND_HOLE is an AP242 feature-definition SHAPE_ASPECT.
# Attach it to the PRODUCT_DEFINITION_SHAPE (#9055) and link to the face.
host_asp = f._emit_raw(
    f"SHAPE_ASPECT('host_face','',#9055,.T.)"
)
hole_asp = f._emit_raw(
    f"SHAPE_ASPECT('round_hole','',#9055,.T.)"
)
# DIMENSIONAL_SIZE carries the internal_diameter = 50 mm (exceeds 30 mm face).
f._emit_raw(
    f"DIMENSIONAL_SIZE(#{hole_asp.eid},'internal_diameter')"
)
# A companion MEASURE with the defective 50 mm value.
diam_mri = f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM"
    f"('internal_diameter',LENGTH_MEASURE(50.0),#9056)"
)
# SHAPE_ASPECT_RELATIONSHIP links hole feature to its host face aspect.
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('round_hole_on_face','hole on face',"
    f"#{host_asp.eid},#{hole_asp.eid})"
)
# GEOMETRIC_ITEM_SPECIFIC_USAGE ties the hole aspect to the face geometry.
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('hole_gisu',$,#{hole_asp.eid},#9061,#{face.eid})"
)
