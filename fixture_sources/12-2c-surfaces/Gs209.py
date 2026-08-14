"""Gs209 — RECTANGULAR_TRIMMED_SURFACE with u1==u2 violates WR1; OCCT silently drops the face (empty shell).

Catalog claim (input pattern): ISO 10303-42 constrains
`rectangular_trimmed_surface WR1: u1 <> u2` (and WR2: v1 <> v2) — a rectangular
trim must have a non-zero extent in each parametric direction. Here the face's
`face_geometry` is `RECTANGULAR_TRIMMED_SURFACE('zerowidth',#cone,0.0,0.0,0.0,1.0,.T.,.T.)`
— `u1 = u2 = 0.0`, a zero-width trim in u, violating WR1. OCCT accepts the file
(`part21_strict` accepts; the structural linter is silent — a value constraint,
not a slot-type/count/emptiness one) but the zero-width trimmed surface collapses:
the ADVANCED_FACE built on it is silently dropped, so OCCT returns a shell with
ZERO faces (`shape(1)` whose only sub-shape is an empty shell). gmsh returns
nothing at all — a cross-oracle divergence on the same bytes.

Distinct from Gp191 (a 2D *pcurve* trim collapse, w1==w2): this is a zero-width
*surface* rectangular trim (u1==u2), a different construct and a different
WHERE-rule. Spec-driven — mined from the AP242 MIM `rectangular_trimmed_surface`
WHERE-rules.

Byte assertions:
  contains(b"RECTANGULAR_TRIMMED_SURFACE('zerowidth',")
  matches(rb"RECTANGULAR_TRIMMED_SURFACE\('zerowidth',#\d+,0\.0,0\.0,")

Tier-3: shape_null == False (OCCT returns a non-null but empty shell)
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs209",
    defect=(
        "the ADVANCED_FACE's face_geometry is a RECTANGULAR_TRIMMED_SURFACE "
        "trimming the cone with u1 = u2 = 0.0 (zero angular width), violating "
        "ISO 10303-42 rectangular_trimmed_surface WR1 (u1 <> u2); OCCT accepts "
        "the file (part21 accepts, structural silent — a value constraint) but "
        "the zero-width trimmed surface collapses: the face is silently dropped "
        "and OCCT returns a shell with ZERO faces, while gmsh returns nothing "
        "at all (cross-oracle divergence); distinct from Gp191 (a 2D pcurve "
        "trim collapse w1==w2) — this is a zero-width surface rectangular trim; "
        "spec-driven, mined from the AP242 MIM rectangular_trimmed_surface "
        "WHERE-rules; expected strict behavior: reject a rectangular trim whose "
        "u1 equals u2 (or v1 equals v2); synonyms: zero-width RECTANGULAR_"
        "TRIMMED_SURFACE, u1 equals u2 trim, zero-extent rectangular trim, "
        "collapsed trimmed surface drops face; the zero-width trimmed surface "
        "is the defect carrier"
    ),
)

semi_angle, base_r, h_face = 0.4, 1.0, 1.0
apex_r = base_r - h_face * _math.tan(semi_angle)
cone_surf = f.conical_surface(
    f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)),
                         f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
    base_r, semi_angle)
# DEFECT: face_geometry trims the cone to zero u-width (u1 == u2 == 0.0), violating WR1.
rts = f._emit_raw(f"RECTANGULAR_TRIMMED_SURFACE('zerowidth',#{cone_surf.eid},0.0,0.0,0.0,1.0,.T.,.T.)")
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
    f.oriented_edge(seam_edge, False), f.oriented_edge(base_edge, False)]))], rts)
f.add_product_chain(f.manifold_solid_brep(f.closed_shell([face])), mode="brep_shape")
