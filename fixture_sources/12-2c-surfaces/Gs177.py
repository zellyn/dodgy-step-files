"""Gs177 — CONICAL_SURFACE apex singularity undetected by ComputeSingularities.

Catalog claim: cone apex is a degenerate point (zero radius) where surface
normal is undefined; ComputeSingularities should detect it and emit a
DEGENERATED_PCURVE / singularity marker. Without detection, healers can't
correct cone-collapse degeneracy.

Previous fixture had TWO FACE_OUTER_BOUND entries on the same face (invalid
BRep — only one outer bound per face is allowed). Regen: one outer bound
(the apex VERTEX_LOOP at z=0) on the conical surface trimmed to a small
v-window around the apex.
"""
from math import pi
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs177",
             defect="conical surface apex singularity, VERTEX_LOOP at apex")

# Conical surface, axis along Z, semi-angle π/4, reference radius 1.0.
# The apex sits at z=0 where the cone collapses to a point.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cone = f._emit_raw(f"CONICAL_SURFACE('cone',#{plc.eid},0.785398163,1.0)")

# VERTEX_LOOP at the apex point (0, 0, 0).
apex_pt = f.cartesian_point((0.0, 0.0, 0.0))
apex_vp = f.vertex_point(apex_pt)
apex_loop = f._emit_raw(f"VERTEX_LOOP('apex_loop',#{apex_vp.eid})")
apex_bound = f._emit_raw(f"FACE_OUTER_BOUND('',#{apex_loop.eid},.T.)")

# Trim the cone surface so the apex is the relevant boundary.
trimmed = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('apex_window',#{cone.eid},"
    f"0.0,{2 * pi},0.0,1.0,.T.,.T.)"
)

face = f._emit_raw(
    f"ADVANCED_FACE('apex_face',(#{apex_bound.eid}),#{trimmed.eid},.T.)"
)
shell = f._emit_raw(f"OPEN_SHELL('apex_shell',(#{face.eid}))")
sbsm = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)
