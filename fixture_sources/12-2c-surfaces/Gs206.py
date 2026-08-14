"""Gs206 — VECTOR with negative magnitude violates ISO 10303-42 `vector` WR1; OCCT accepts silently.

Catalog claim (input pattern): ISO 10303-42 constrains `vector` with
`WR1: magnitude >= 0.0`. This file's seam-edge `LINE` takes its direction from
`VECTOR('neg_mag',#dir,-L)` — a valid DIRECTION but a NEGATIVE magnitude, which
violates WR1. OCCT (and gmsh) accept the file and build the solid (shape(1))
without any diagnostic; part21 accepts too (a negative real is valid Part-21
syntax); the non-kernel structural linter is silent. So this is a spec
WHERE-rule violation that every oracle here silently tolerates.

Distinct from Gs036 (zero-magnitude / negative-radius): magnitude 0 is PERMITTED
by WR1 (`>= 0`); only a strictly-negative magnitude violates it. Spec-driven:
mined from the AP242 MIM `vector` WHERE-rule, not from a reader failure — the
class of formal constraints OCCT does not enforce. A strict kernel should reject
(or normalise) a negative vector magnitude per WR1.

Byte assertions:
  contains(b"VECTOR('neg_mag',")
  matches(rb"VECTOR\('neg_mag',#\d+,-")

Tier-3: shape_null == False (OCCT builds the solid despite the WR1 violation)
Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs206",
    defect=(
        "a VECTOR supplies a valid DIRECTION but a NEGATIVE magnitude "
        "(VECTOR('neg_mag',#dir,-L)) as the direction of the seam-edge LINE, "
        "violating ISO 10303-42 vector WR1 (magnitude >= 0.0); OCCT and gmsh "
        "accept the file and build the solid shape(1) with no diagnostic, "
        "part21 accepts (a negative real is valid syntax) and the structural "
        "linter is silent, so every oracle tolerates the WHERE-rule violation; "
        "distinct from Gs036 (zero-magnitude, which WR1 permits) — only a "
        "strictly-negative magnitude violates WR1; spec-driven, mined from the "
        "AP242 MIM vector WHERE-rule; expected strict behavior: reject or "
        "normalise a negative vector magnitude per WR1; synonyms: negative "
        "VECTOR magnitude, vector magnitude below zero, ISO 10303-42 vector "
        "WR1 violation, negative-magnitude direction vector; the negative-"
        "magnitude VECTOR is the defect carrier"
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
seam_dir = f.direction((dx / seam_len, 0.0, dz / seam_len))
# DEFECT: negative magnitude in the seam VECTOR (violates vector WR1: magnitude >= 0.0).
neg_vec = f._emit_raw(f"VECTOR('neg_mag',#{seam_dir.eid},-{seam_len})")
seam_line = f._emit_raw(f"LINE('',#{pt_base.eid},#{neg_vec.eid})")
seam_edge = f.edge_curve(v_base, v_apex, seam_line)
face = f.advanced_face([f.face_outer_bound(f.edge_loop([
    f.oriented_edge(seam_edge, True), f.oriented_edge(apex_edge, True),
    f.oriented_edge(seam_edge, False), f.oriented_edge(base_edge, False)]))], cone_surf)
f.add_product_chain(f.manifold_solid_brep(f.closed_shell([face])), mode="brep_shape")
