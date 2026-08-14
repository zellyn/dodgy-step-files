"""Gs210 — CONICAL_SURFACE with negative radius violates conical_surface WR1; OCCT silently drops the face.

Catalog claim (input pattern): ISO 10303-42 constrains
`conical_surface WR1: radius >= 0.0` — a cone's reference (base) radius must be
non-negative. Here the face's `face_geometry` is
`CONICAL_SURFACE('',#plc,-1.0,0.4)` — a strictly NEGATIVE radius, violating WR1.
OCCT accepts the file (`part21_strict` accepts — a negative real is valid
syntax; the structural linter is silent — a value constraint) but the
negative-radius cone's face collapses: the ADVANCED_FACE is silently dropped,
so OCCT returns a shell with ZERO faces (`shape(1)` whose only sub-shape is an
empty shell), and gmsh returns nothing — a cross-oracle divergence.

Distinct from Gs036 (zero-magnitude/all-zero DIRECTION and colinear axes — a
direction/vector/placement degeneracy, not a surface radius sign) and from
Gs206 (negative VECTOR *magnitude*, which loads a full shape rather than
dropping a face). Spec-driven — mined from the AP242 MIM `conical_surface`
WHERE-rule; the value-sign class applied to a surface radius, producing silent
geometry loss.

Byte assertions:
  contains(b'CONICAL_SURFACE')
  matches(rb"CONICAL_SURFACE\('',#\d+,-")

Tier-3: shape_null == False (OCCT returns a non-null but empty shell)
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs210",
    defect=(
        "the ADVANCED_FACE's face_geometry is a CONICAL_SURFACE with a strictly "
        "NEGATIVE reference radius (CONICAL_SURFACE('',#plc,-1.0,0.4)), violating "
        "ISO 10303-42 conical_surface WR1 (radius >= 0.0); OCCT accepts the file "
        "(part21 accepts, structural silent — a value constraint) but the "
        "negative-radius cone's face collapses: it is silently dropped and OCCT "
        "returns a shell with ZERO faces while gmsh returns nothing (cross-"
        "oracle divergence); distinct from Gs036 (direction/vector/axis "
        "degeneracy, not surface radius) and Gs206 (negative VECTOR magnitude, "
        "which loads a full shape); spec-driven, mined from the AP242 MIM "
        "conical_surface WHERE-rule; expected strict behavior: reject a cone "
        "whose radius is negative per WR1; synonyms: negative cone radius, "
        "CONICAL_SURFACE radius below zero, conical_surface WR1 violation, "
        "negative-radius cone drops face; the negative-radius CONICAL_SURFACE "
        "is the defect carrier"
    ),
)

semi_angle, base_r, h_face = 0.4, 1.0, 1.0
apex_r = base_r - h_face * _math.tan(semi_angle)
cone_plc = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)),
                                f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
# DEFECT: CONICAL_SURFACE reference radius is negative (violates WR1). Rest of the geometry is valid.
cone_surf = f._emit_raw(f"CONICAL_SURFACE('',#{cone_plc.eid},-{base_r},{semi_angle})")
pt_base = f.cartesian_point((base_r, 0.0, 0.0))
pt_apex = f.cartesian_point((apex_r, 0.0, h_face))
v_base, v_apex = f.vertex_point(pt_base), f.vertex_point(pt_apex)
base_edge = f.edge_curve(v_base, v_base, f.circle(
    f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)),
                         f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0))), base_r))
apex_edge = f.edge_curve(v_apex, v_apex, f.circle(
    f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, h_face)),
                         f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))), apex_r))
dx, dz = apex_r - base_r, h_face
seam_len = _math.sqrt(dx * dx + dz * dz)
seam_line = f._emit_raw(f"LINE('',#{pt_base.eid},#{f.vector(f.direction((dx/seam_len,0.0,dz/seam_len)),seam_len).eid})")
seam_edge = f.edge_curve(v_base, v_apex, seam_line)
face = f.advanced_face([f.face_outer_bound(f.edge_loop([
    f.oriented_edge(seam_edge, True), f.oriented_edge(apex_edge, True),
    f.oriented_edge(seam_edge, False), f.oriented_edge(base_edge, False)]))], cone_surf)
f.add_product_chain(f.manifold_solid_brep(f.closed_shell([face])), mode="brep_shape")
