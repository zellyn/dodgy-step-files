"""N106 — ShapeFix_Edge.FixVertexTolerance vertex-on-singular-surface

Vertex tolerance evaluation on cone apex (singular surface point).
FixVertexTolerance evaluates surface curvature at apex, producing unbounded
tolerance due to infinite curvature. Edge from apex to base point on cone
surface with parametric tolerance inference. Tests geometry curvature
singularity handling.

Byte assertions:
  contains(b'apex')
  contains(b'base')
  contains(b'edge_on_cone')
  contains(b'cone_face')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N106",
    defect=(
        "CLOSED_SHELL shell with cone_face containing edge_on_cone from apex to base; "
        "FixVertexTolerance evaluates curvature at apex (singular point) producing "
        "unbounded tolerance — infinite curvature at cone tip not handled"
    ),
)

# Cone geometry via raw emission
# Apex at origin, base point along x-axis
p_apex = f.cartesian_point((0.0, 0.0, 0.0))
p_base = f.cartesian_point((5.0, 0.0, 0.0))

v_apex = f.vertex_point(p_apex, name="apex")
v_base = f.vertex_point(p_base, name="base")

# Line from apex to base
d_x = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 1.0)
l_edge = f.line(p_apex, vec_x)
e_cone = f.edge_curve(v_apex, v_base, l_edge, name="edge_on_cone")

# Cone surface: axis placement at origin, z-axis up, x-axis forward
# CONE: semi-angle 0.5 radians (~28.6 deg), distance along axis 10
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p_apex, zdir, xdir)
cone_surf = f._emit_raw(f"CONE('cone_surf',#{plc.eid},10.0,0.5)")

loop = f.edge_loop([
    f.oriented_edge(e_cone, True),
])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], cone_surf, name="cone_face")

shell = f.closed_shell([face], name="shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N106.stp")
