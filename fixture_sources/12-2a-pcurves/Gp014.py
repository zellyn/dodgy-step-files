"""Gp014 — Shared pcurve across multiple edges (SYRKO).

Catalog claim: One PCURVE is referenced by multiple distinct EDGE_CURVE
instances. Trimming one edge ends up trimming all neighbours that share the
pcurve, corrupting topology.

Fixture: A cylindrical surface with two edges (top and bottom horizontal
circles) whose SURFACE_CURVEs both point at the SAME PCURVE instance.
When the translator clips pcurves to per-edge parameter ranges, both edges
get the same clip applied, corrupting one of them.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp014",
             defect="Same PCURVE instance referenced by two distinct EDGE_CURVEs (SYRKO aliasing)")

# Cylindrical surface
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f.cylindrical_surface(plc, 1.0)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# THE SHARED PCURVE — a horizontal line in UV at v=0.25, u from 0 to 2π
# This single instance will be referenced by BOTH edge surface_curves
shared_pc_start = f.cartesian_point((0.0, 0.25))
shared_pc_dir = f.direction((1.0, 0.0))
shared_pc_vec = f.vector(shared_pc_dir, 6.283185307)
shared_pc_line = f.line(shared_pc_start, shared_pc_vec)
shared_pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('shared_pc',(#{shared_pc_line.eid}),#{prc.eid})"
)
# THE ONE PCURVE — both edges will alias to this same entity (the defect)
shared_pcurve = f._emit_raw(f"PCURVE('shared',#{cyl.eid},#{shared_pc_def.eid})")

# Edge 1: bottom circle at z=0.25 (u-parameter v=0.25 on cylinder)
bot_pt = f.cartesian_point((1.0, 0.0, 0.25))
v_bot = f.vertex_point(bot_pt)
circle_plc_bot = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.25)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0))
)
circle_bot = f.circle(circle_plc_bot, 1.0)
# DEFECT: surface_curve for edge 1 uses the shared pcurve
sc1 = f._emit_raw(
    f"SURFACE_CURVE('',#{circle_bot.eid},(#{shared_pcurve.eid}),.PCURVE_S1.)"
)
edge1 = f._emit_raw(
    f"EDGE_CURVE('bottom_circle',#{v_bot.eid},#{v_bot.eid},#{sc1.eid},.T.)"
)

# Edge 2: top circle at z=0.75 — should have its OWN pcurve at v=0.75,
# but SYRKO bug means it reuses shared_pcurve (wrong v=0.25!)
top_pt = f.cartesian_point((1.0, 0.0, 0.75))
v_top = f.vertex_point(top_pt)
circle_plc_top = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.75)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0))
)
circle_top = f.circle(circle_plc_top, 1.0)
# DEFECT: SAME shared_pcurve referenced again — aliasing the wrong v value
sc2 = f._emit_raw(
    f"SURFACE_CURVE('',#{circle_top.eid},(#{shared_pcurve.eid}),.PCURVE_S1.)"
)
edge2 = f._emit_raw(
    f"EDGE_CURVE('top_circle',#{v_top.eid},#{v_top.eid},#{sc2.eid},.T.)"
)

loop1 = f.edge_loop([f.oriented_edge(edge1, True)])
loop2 = f.edge_loop([f.oriented_edge(edge2, True)])
face = f.advanced_face(
    [f.face_outer_bound(loop1), f.face_bound(loop2)],
    cyl
)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
