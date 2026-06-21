"""Pmi092 — COUNTERBORE_HOLE feature with counterbore_diameter smaller than thru-hole diameter.

Catalog claim: A COUNTERBORE_HOLE feature's geometric invariant requires
counterbore_diameter > thru_hole_diameter. This fixture emits
internal_diameter 12 mm (thru-hole) and counterbore_diameter 8 mm
(smaller — invalid). The contradiction is the defect; receivers must reject
and name the violated attribute relationship.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi092",
    defect=(
        "COUNTERBORE_HOLE feature: internal_diameter 12 mm (thru-hole) and "
        "counterbore_diameter 8 mm (smaller — invalid); "
        "counterbore_diameter must be > internal_diameter"
    ),
)

# ── 50×50 mm planar face (the host, area 2500 mm²) ───────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((50.0, 0.0, 0.0))
p2 = f.cartesian_point((50.0, 50.0, 0.0))
p3 = f.cartesian_point((0.0, 50.0, 0.0))

loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="host_face")
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# ── DEFECT: COUNTERBORE_HOLE with inverted diameters ─────────────────────────
# Attach feature SHAPE_ASPECTs to PRODUCT_DEFINITION_SHAPE (#9055).
host_asp = f._emit_raw(
    "SHAPE_ASPECT('host_face','',#9055,.T.)"
)
cbore_asp = f._emit_raw(
    "SHAPE_ASPECT('counterbore_hole','',#9055,.T.)"
)
# thru-hole diameter: 12 mm (internal_diameter)
f._emit_raw(
    f"DIMENSIONAL_SIZE(#{cbore_asp.eid},'internal_diameter')"
)
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM"
    f"('internal_diameter',LENGTH_MEASURE(12.0),#9056)"
)
# counterbore diameter: 8 mm — SMALLER than thru-hole (defect)
f._emit_raw(
    f"DIMENSIONAL_SIZE(#{cbore_asp.eid},'counterbore_diameter')"
)
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM"
    f"('counterbore_diameter',LENGTH_MEASURE(8.0),#9056)"
)
# Link hole feature to host face aspect.
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('counterbore_on_face','counterbore on face',"
    f"#{host_asp.eid},#{cbore_asp.eid})"
)
# GEOMETRIC_ITEM_SPECIFIC_USAGE ties the hole aspect to the face geometry.
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('cbore_gisu',$,#{cbore_asp.eid},#9061,#{face.eid})"
)
