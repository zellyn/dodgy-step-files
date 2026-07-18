"""Gp193 — Pcurve 2D seed drifts in V from the 3D edge geometry (OCC heals by recompute).

Catalog claim: An EDGE_CURVE that bounds a real ADVANCED_FACE carries a
SURFACE_CURVE whose PCURVE 2D seed is offset in V (v=0.5) while the 3D
curve of the edge actually lies at v=0.0 on the host PLANE. The declared
2D parameter curve therefore disagrees with the 3D geometry by 0.5 in the
surface's V direction — far beyond the file's 1e-7 uncertainty — so a
strict "curve on surface" validator would reject it as an invalid pcurve.

OCC does NOT reject: STEPControl_Reader discards the grossly-disagreeing
declared pcurve and recomputes it from the 3D curve during transfer, so
the face builds cleanly with a pcurve at v=0. Verified live (2026-07-18):
the built edge's stored pcurve is (0,0)->(1,0) regardless of the declared
drift (swept v=0.5,5,50,500 — all recompute to v=0, edge tolerance stays
1e-7), and regardless of heal_on vs heal_off. There is NO tolerance
boundary: the declared 2D seed is effectively ignored in favour of the 3D
curve. Consequently the drift is shape-count-oracle-INVISIBLE — this file
builds face:1 identically to a clean face — but the heal-recompute is real
and directly verifiable by reading the built edge's curve-on-surface. The
value is documenting that OCC's STEP reader does not trust declared
pcurves at all (recomputes every one from 3D), so producer-side pcurve
errors are silently corrected on read.

Surface parameterisation: PLANE at origin, axis +Z, ref_direction +X, so
P(u,v) = (u, v, 0); U maps to X, V maps to Y. The 3D edge runs (0,0,0)->
(1,0,0) i.e. v=0; the declared pcurve is seeded at v=0.5.

Byte assertions: contains(b'SURFACE_CURVE'), contains(b'EDGE_CURVE'),
count_entity_def(b'PCURVE') >= 1
Tier-3: shape_null == False, n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp193",
             defect="pcurve 2D seed drifts in V (v=0.5) from the 3D edge geometry (v=0); OCC recomputes the pcurve from the 3D curve so the face builds cleanly")

# Planar host surface z=0: P(u,v) = (u, v, 0)
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f._emit_raw(f"PLANE('',#{plc.eid})")

# 3D edge: line on the plane from (0,0,0) to (1,0,0) -> lies at v=0
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end = f.cartesian_point((1.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)
line_dir = f.direction((1.0, 0.0, 0.0))
line_vec = f.vector(line_dir, 1.0)
line3d = f.line(p_start, line_vec)

# DEFECT: 2D pcurve seeded at v=0.5 (should be v=0), running +u.
# Lifted through the plane this traces (u, 0.5, 0) — parallel to and 0.5
# away from the real 3D edge at (u, 0, 0), well beyond the 1e-7 uncertainty.
uv_start = f.cartesian_point((0.0, 0.5))
uv_dir = f.direction((1.0, 0.0))
uv_vec = f.vector(uv_dir, 1.0)
line2d = f.line(uv_start, uv_vec)
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('','2D'))")
defrep = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{line2d.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('',#{plane.eid},#{defrep.eid})")
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)")
edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)")

# Wire the edge into a real ADVANCED_FACE so OCC actually reconciles the
# pcurve against the surface + 3D curve (ShapeFix / BRepLib::SameParameter).
loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
