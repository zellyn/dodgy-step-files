"""M055 — POLY_LOOP on non-planar surface inside FACETED_BREP.

Catalog claim: FACETED_BREP requires planar faces; POLY_LOOP placed on
a non-planar surface violates the schema. OCCT
StepToTopoDS_TranslatePolyLoop.cxx:88-91 rejects the face in this
configuration, but OCCT's auto-repair is stronger: it actually loads a
shape (outside the catalog's allowed set of reject/warn-and-proceed).

Reproducer recipe: FACETED_BREP referencing a face on a CYLINDRICAL_SURFACE
bounded by a POLY_LOOP whose vertices are sampled on the cylinder and are
therefore not coplanar.

Tier-3 assertions:
  face[0].surface_type == "cylinder"
  n_edges_total >= 4
  n_vertices_total >= 8
  brepcheck.valid == True

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M055",
    schema="AP214",
    defect=(
        "POLY_LOOP on non-planar surface inside FACETED_BREP; "
        "input: AP214 STEP file where FACETED_BREP references a CLOSED_SHELL "
        "containing an ADVANCED_FACE whose surface is a CYLINDRICAL_SURFACE "
        "and whose outer bound is a POLY_LOOP with vertices sampled on the "
        "cylinder (not coplanar); "
        "FACETED_BREP schema requires planar faces; POLY_LOOP on a "
        "CYLINDRICAL_SURFACE is a schema violation; "
        "OCCT StepToTopoDS_TranslatePolyLoop.cxx:88-91 documents the reject "
        "path but OCC's auto-repair produces a shape (stronger than catalog's "
        "reject-only stance); conservative kernels should still reject; "
        "synonyms: POLY_LOOP on non-planar surface, FACETED_BREP non-planar face, "
        "schema-illegal polyloop placement, faceted brep requires planar faces"
    ),
)

# ── Cylindrical surface (the non-planar surface — defect carrier) ──────────────
cyl_origin = f.cartesian_point((0.0, 0.0, 0.0))
cyl_axis   = f.direction((0.0, 0.0, 1.0))
cyl_ref    = f.direction((1.0, 0.0, 0.0))
cyl_plc    = f.axis2_placement_3d(cyl_origin, cyl_axis, cyl_ref)
cyl_surf   = f.cylindrical_surface(cyl_plc, 5.0, name="side_wall")

# ── POLY_LOOP — vertices sampled on the cylinder; deliberately NOT coplanar ────
# These four points lie on a cylinder of radius 5 at different z-heights.
# (5,0,0), (0,5,0), (0,5,4), (5,0,4) — not coplanar, making this schema-illegal.
p0 = f.cartesian_point((5.0, 0.0, 0.0))
p1 = f.cartesian_point((0.0, 5.0, 0.0))
p2 = f.cartesian_point((0.0, 5.0, 4.0))
p3 = f.cartesian_point((5.0, 0.0, 4.0))

# POLY_LOOP — emitted via _emit_raw because StepFile has no poly_loop helper
poly_loop = f._emit_raw(
    f"POLY_LOOP('non_planar_loop',({p0.ref()},{p1.ref()},{p2.ref()},{p3.ref()}))"
)
# Byte assertions: by having FACETED_BREP and CYLINDRICAL_SURFACE in the file
# Tier-3: face[0].surface_type == "cylinder" (CYLINDRICAL_SURFACE is the face surface)

# FACE_OUTER_BOUND references POLY_LOOP (schema-illegal on non-planar surface)
fob = f._emit_raw(
    f"FACE_OUTER_BOUND('',{poly_loop.ref()},.T.)"
)
# ADVANCED_FACE with CYLINDRICAL_SURFACE bounded by POLY_LOOP — the defect
cyl_face = f._emit_raw(
    f"ADVANCED_FACE('cyl_face_with_poly_loop',({fob.ref()}),{cyl_surf.ref()},.T.)"
)

# CLOSED_SHELL is the legal outer for FACETED_BREP; the defect is the face itself
shell = f._emit_raw(
    f"CLOSED_SHELL('shell_with_illegal_face',({cyl_face.ref()}))"
)

# FACETED_BREP — the schema-violating entity (POLY_LOOP on non-planar surface)
faceted = f._emit_raw(
    f"FACETED_BREP('faceted_brep_with_curved_face',{shell.ref()})"
)

# Product chain as ADVANCED_BREP_SHAPE_REPRESENTATION
f.add_product_chain(faceted, mode="brep_shape")

f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M055.stp")
