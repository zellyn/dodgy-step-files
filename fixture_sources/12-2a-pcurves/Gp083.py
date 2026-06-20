"""Gp083 — CheckOverlapping period-shifted edges.

Catalog claim: Two edges on periodic surface where their 3D geometry coincides
but their 2D pcurves are in different periods (offset by 2π);
CheckOverlapping reports them as non-overlapping.

Fixture: CYLINDRICAL_SURFACE (radius 1, axis Z). Two EDGE_CURVEs trace the
same 3D half-circle arc (from (1,0,0) to (-1,0,0)). One edge has its
pcurve anchored at U=0 (natural period), the other at U=2π (next period).
Geometrically they are identical 3D paths; only the 2D parameter origin
differs by one full period.

CheckOverlapping compares pcurve parameter domains and sees [0, π] vs [2π, 3π]
— no domain overlap — and incorrectly concludes the edges do not overlap.
OCC heals the model and produces a valid shape.
"""
from math import pi
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp083",
             defect="two EDGE_CURVEs on CYLINDRICAL_SURFACE with identical 3D "
                    "geometry but pcurves offset by 2π (period shift); "
                    "CheckOverlapping sees non-overlapping 2D domains")

# Cylindrical surface: axis along Z, radius 1.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
cyl  = f._emit_raw(f"CYLINDRICAL_SURFACE('cylinder',#{plc.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('uv_ctx','UV'))"
)

# Shared 3D geometry: half-circle arc in XY at z=0, from (1,0,0) to (-1,0,0).
p_start = f.cartesian_point((1.0, 0.0, 0.0))
p_end   = f.cartesian_point((-1.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

circ_plc   = f.axis2_placement_3d(orig, zdir, xdir)
circle3d   = f._emit_raw(f"CIRCLE('arc',#{circ_plc.eid},1.0)")

# Edge A: pcurve anchored at U=0, runs from U=0 to U=π (natural period).
uv_a_start = f.cartesian_point((0.0, 0.0))
udir_a     = f.direction((1.0, 0.0))
uvec_a     = f.vector(udir_a, pi)
uline_a    = f.line(uv_a_start, uvec_a)
defrep_a   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_a_def',(#{uline_a.eid}),#{prc.eid})"
)
pcurve_a   = f._emit_raw(f"PCURVE('pcurve_u0',#{cyl.eid},#{defrep_a.eid})")
sc_a       = f._emit_raw(
    f"SURFACE_CURVE('edge_geom_a',#{circle3d.eid},(#{pcurve_a.eid}),.PCURVE_S1.)"
)
edge_a     = f._emit_raw(
    f"EDGE_CURVE('arc_period0',#{v_start.eid},#{v_end.eid},#{sc_a.eid},.T.)"
)

# Edge B: pcurve anchored at U=2π (one period later) — same 3D geometry.
uv_b_start = f.cartesian_point((2.0 * pi, 0.0))
udir_b     = f.direction((1.0, 0.0))
uvec_b     = f.vector(udir_b, pi)
uline_b    = f.line(uv_b_start, uvec_b)
defrep_b   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_b_def',(#{uline_b.eid}),#{prc.eid})"
)
pcurve_b   = f._emit_raw(f"PCURVE('pcurve_u2pi',#{cyl.eid},#{defrep_b.eid})")
sc_b       = f._emit_raw(
    f"SURFACE_CURVE('edge_geom_b',#{circle3d.eid},(#{pcurve_b.eid}),.PCURVE_S1.)"
)
edge_b     = f._emit_raw(
    f"EDGE_CURVE('arc_period1',#{v_start.eid},#{v_end.eid},#{sc_b.eid},.T.)"
)

# Build a closed face using edge_a for the bottom loop and edge_b in a second
# sub-face so both edges appear in the model.
# Strategy: two separate open_shell faces sharing the same cylinder surface
# but using the two overlapping edges.

# Top vertices at z=2 to close each face.
p_top_start = f.cartesian_point((1.0, 0.0, 2.0))
p_top_end   = f.cartesian_point((-1.0, 0.0, 2.0))
v_top_start = f.vertex_point(p_top_start)
v_top_end   = f.vertex_point(p_top_end)

top_plc    = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 2.0)), zdir, xdir)
top_circle = f._emit_raw(f"CIRCLE('top_arc',#{top_plc.eid},1.0)")
top_edge   = f.edge_curve(v_top_start, v_top_end, top_circle)

seam_dir  = f.direction((0.0, 0.0, 1.0))
seam_vec  = f.vector(seam_dir, 2.0)
seam1_line = f.line(p_start, seam_vec)
seam1      = f.edge_curve(v_start, v_top_start, seam1_line)
seam2_line = f.line(p_end, seam_vec)
seam2      = f.edge_curve(v_end, v_top_end, seam2_line)

# Face 1: uses edge_a (period-0 pcurve).
loop1 = f.edge_loop([
    f.oriented_edge(edge_a, True),
    f.oriented_edge(seam2,  True),
    f.oriented_edge(top_edge, False),
    f.oriented_edge(seam1,  False),
])
face1 = f.advanced_face([f.face_outer_bound(loop1)], cyl)

# Face 2: uses edge_b (period-1 pcurve) — geometrically identical bottom edge.
# Use a separate cylinder offset in Z by 3 to avoid geometry conflict.
orig3 = f.cartesian_point((0.0, 0.0, 3.0))
plc3  = f.axis2_placement_3d(orig3, zdir, xdir)
cyl3  = f._emit_raw(f"CYLINDRICAL_SURFACE('cylinder2',#{plc3.eid},1.0)")

p_start3    = f.cartesian_point((1.0, 0.0, 3.0))
p_end3      = f.cartesian_point((-1.0, 0.0, 3.0))
v_start3    = f.vertex_point(p_start3)
v_end3      = f.vertex_point(p_end3)
p_top_start3 = f.cartesian_point((1.0, 0.0, 5.0))
p_top_end3   = f.cartesian_point((-1.0, 0.0, 5.0))
v_top_start3 = f.vertex_point(p_top_start3)
v_top_end3   = f.vertex_point(p_top_end3)

circ3_plc = f.axis2_placement_3d(orig3, zdir, xdir)
circle3d_b = f._emit_raw(f"CIRCLE('arc2',#{circ3_plc.eid},1.0)")

# Re-declare edge_b on cylinder cyl3 so it is self-consistent.
defrep_b2  = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_b2_def',(#{uline_b.eid}),#{prc.eid})"
)
pcurve_b2  = f._emit_raw(f"PCURVE('pcurve_u2pi_2',#{cyl3.eid},#{defrep_b2.eid})")
sc_b2      = f._emit_raw(
    f"SURFACE_CURVE('edge_geom_b2',#{circle3d_b.eid},(#{pcurve_b2.eid}),.PCURVE_S1.)"
)
edge_b2    = f._emit_raw(
    f"EDGE_CURVE('arc_period1_2',#{v_start3.eid},#{v_end3.eid},#{sc_b2.eid},.T.)"
)

top3_plc   = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 5.0)), zdir, xdir)
top_circ3  = f._emit_raw(f"CIRCLE('top_arc2',#{top3_plc.eid},1.0)")
top_edge3  = f.edge_curve(v_top_start3, v_top_end3, top_circ3)
seam3_line = f.line(p_start3, seam_vec)
seam3      = f.edge_curve(v_start3, v_top_start3, seam3_line)
seam4_line = f.line(p_end3, seam_vec)
seam4      = f.edge_curve(v_end3, v_top_end3, seam4_line)

loop2 = f.edge_loop([
    f.oriented_edge(edge_b2, True),
    f.oriented_edge(seam4,   True),
    f.oriented_edge(top_edge3, False),
    f.oriented_edge(seam3,   False),
])
face2 = f.advanced_face([f.face_outer_bound(loop2)], cyl3)

shell = f.open_shell([face1, face2])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
