"""Gs208 — TRIMMED_CURVE trim specified with two PARAMETER_VALUE selectors violates trimmed_curve WR1; OCCT accepts silently.

Catalog claim (input pattern): ISO 10303-42 constrains
`trimmed_curve WR1: (HIINDEX(trim_1) = 1) OR (TYPEOF(trim_1[1]) <> TYPEOF(trim_1[2]))`
(and WR2 for trim_2) — a trim endpoint given by TWO selectors must give them as
two DIFFERENT types (a CARTESIAN_POINT and a PARAMETER_VALUE), never two of the
same type. Here the seam edge's 3D curve is
`TRIMMED_CURVE('samesel',#line,(PARAMETER_VALUE(0.0),PARAMETER_VALUE(0.0)),
(PARAMETER_VALUE(L),PARAMETER_VALUE(L)),.T.,.PARAMETER.)` — each trim gives two
PARAMETER_VALUE selectors, violating WR1/WR2. OCCT accepts the file and builds
the cone solid (shape(1)) with no diagnostic; part21 accepts (the bytes are
syntactically valid); the structural linter is silent. Every oracle tolerates
the redundant same-type trim.

A producer commits this by emitting the trim parameter twice (or wiring two
parameter builders into one trim) instead of one point + one parameter. Distinct
from the corpus's trim-RANGE defects (w1/w2 order, out-of-bounds, pcurve trim
mismatch): this is a structural selector-type violation, not a range error.
Spec-driven — mined from the AP242 MIM `trimmed_curve` WHERE-rules.

Byte assertions:
  contains(b"TRIMMED_CURVE('samesel',")
  matches(rb"\(PARAMETER_VALUE\([^)]*\),PARAMETER_VALUE")

Tier-3: shape_null == False (OCCT builds the cone despite the WR1 violation)
Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs208",
    defect=(
        "the seam edge's 3D curve is a TRIMMED_CURVE whose trim_1 and trim_2 "
        "each give TWO PARAMETER_VALUE selectors "
        "(PARAMETER_VALUE(0.0),PARAMETER_VALUE(0.0)), violating ISO 10303-42 "
        "trimmed_curve WR1/WR2 (the two selectors of a trim must be of "
        "different types — a point and a parameter, not two parameters); OCCT "
        "accepts and builds the cone solid shape(1) with no diagnostic, part21 "
        "accepts (syntactically valid) and the structural linter is silent, so "
        "every oracle tolerates the redundant same-type trim; distinct from the "
        "trim-range defects (w1/w2 order, out-of-bounds, pcurve trim mismatch) "
        "— this is a structural selector-type violation; spec-driven, mined "
        "from the AP242 MIM trimmed_curve WHERE-rules; expected strict "
        "behavior: reject a trim whose two selectors are the same type; "
        "synonyms: TRIMMED_CURVE two same-type trim, redundant parameter trim "
        "selector, two PARAMETER_VALUE in one trim, trimmed_curve WR1 "
        "violation; the same-type TRIMMED_CURVE trims are the defect carrier"
    ),
)

semi_angle, base_r, h_face = 0.4, 1.0, 1.0
apex_r = base_r - h_face * _math.tan(semi_angle)
cone_surf = f.conical_surface(
    f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)),
                         f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
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
# DEFECT: TRIMMED_CURVE trims each carry two PARAMETER_VALUE selectors (violate WR1/WR2).
trimmed = f._emit_raw(
    f"TRIMMED_CURVE('samesel',#{seam_line.eid},"
    f"(PARAMETER_VALUE(0.0),PARAMETER_VALUE(0.0)),"
    f"(PARAMETER_VALUE({seam_len}),PARAMETER_VALUE({seam_len})),.T.,.PARAMETER.)")
seam_edge = f.edge_curve(v_base, v_apex, trimmed)
face = f.advanced_face([f.face_outer_bound(f.edge_loop([
    f.oriented_edge(seam_edge, True), f.oriented_edge(apex_edge, True),
    f.oriented_edge(seam_edge, False), f.oriented_edge(base_edge, False)]))], cone_surf)
f.add_product_chain(f.manifold_solid_brep(f.closed_shell([face])), mode="brep_shape")
