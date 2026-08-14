"""Gs207 — 2-ratio DIRECTION used as a 3D placement's ref_direction violates axis2_placement_3d WR3; OCCT accepts silently.

Catalog claim (input pattern): ISO 10303-42 constrains
`axis2_placement_3d WR3: (NOT EXISTS(ref_direction)) OR (ref_direction.dim = 3)`
— the reference direction of a 3D placement must itself be 3-dimensional. Here
the conical surface's placement uses `DIRECTION('bad2d',(1.0,0.0))` — a 2-ratio
(dim = 2) direction — as its `ref_direction`, violating WR3. OCCT accepts the
file and builds the cone solid (shape(1)) with no diagnostic; part21 accepts (a
2-ratio DIRECTION is valid Part-21 syntax); the structural linter is silent.
Every oracle here tolerates the dimensionality mismatch.

Distinct from the pcurve dimensionality bugs (a 3D LINE wired into a 2D UV-pcurve
slot): this is the OPPOSITE mismatch (a 2D direction where 3D is required) in a
DIFFERENT slot (a surface's placement ref_direction, not a pcurve item).
Spec-driven — mined from the AP242 MIM `axis2_placement_3d` WHERE-rule, the class
of formal constraints OCCT does not enforce.

Byte assertions:
  contains(b"DIRECTION('bad2d',(1.0,0.0))")

Tier-3: shape_null == False (OCCT builds the cone despite the WR3 violation)
Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs207",
    defect=(
        "the conical surface's AXIS2_PLACEMENT_3D uses a 2-ratio (dim=2) "
        "DIRECTION('bad2d',(1.0,0.0)) as its ref_direction, violating ISO "
        "10303-42 axis2_placement_3d WR3 (ref_direction.dim = 3); OCCT accepts "
        "the file and builds the cone solid shape(1) with no diagnostic, part21 "
        "accepts (a 2-ratio DIRECTION is valid syntax) and the structural "
        "linter is silent, so every oracle tolerates the dimensionality "
        "mismatch; distinct from the pcurve dimensionality bugs (a 3D LINE in a "
        "2D UV-pcurve slot) — this is the opposite mismatch (2D where 3D "
        "required) in a different slot (surface placement ref_direction); "
        "spec-driven, mined from the AP242 MIM axis2_placement_3d WHERE-rule; "
        "expected strict behavior: reject a ref_direction whose dim is not 3; "
        "synonyms: 2D direction in 3D placement, two-ratio direction ref, "
        "axis2_placement_3d WR3 violation, wrong-dimensionality reference "
        "direction; the 2-ratio DIRECTION is the defect carrier"
    ),
)

semi_angle, base_r, h_face = 0.4, 1.0, 1.0
apex_r = base_r - h_face * _math.tan(semi_angle)
# DEFECT: ref_direction of the cone placement is a 2-ratio (dim=2) DIRECTION.
bad_ref = f._emit_raw("DIRECTION('bad2d',(1.0,0.0))")
cone_surf = f.conical_surface(
    f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)),
                         f.direction((0.0, 0.0, 1.0)), bad_ref),
    base_r, semi_angle)
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
