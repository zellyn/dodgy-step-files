"""Gp122 — ShapeFix_Edge.FixAddPCurve B-spline-on-trimmed-surface.

Catalog claim: Edge on RECTANGULAR_TRIMMED_SURFACE wrapping a PLANE.
FixAddPCurve constructs pcurve in base-surface coords, missing trim
translation — the UV coords are in the base-surface space rather than
the trimmed-surface local space.

STEP mechanism (literal):
  - Host surface: RECTANGULAR_TRIMMED_SURFACE wrapping a PLANE (Z=0).
    The trim is u∈[1,3], v∈[0.5,2.5] — i.e. the base surface has a
    larger domain but the face lives on the trimmed surface.
  - Defect edge: SURFACE_CURVE; pcurve references the
    RECTANGULAR_TRIMMED_SURFACE entity directly. The pcurve UV coords
    are expressed in base-surface coordinates (not trimmed-surface local
    offset), which triggers the FixAddPCurve trim-offset bug.
  - THE CATALOG MECHANISM: FixAddPCurve builds the pcurve in base-surface
    UV, not in the trimmed-surface's local UV frame. For a
    RECTANGULAR_TRIMMED_SURFACE the local UV origin is (u1,v1) in the
    base; FixAddPCurve misses this translation. OCC heals silently.
  - 3D curve: clean LINE. Geometry is valid and loadable.
  - NO C-1 break (Archetype B: OCC silently heals; shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: pcurve references RECTANGULAR_TRIMMED_SURFACE;
    UV coords in base-surface frame; FixAddPCurve misses trim translation.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp122",
    defect=(
        "PLANE Z=0 base; host: RECTANGULAR_TRIMMED_SURFACE u∈[1,3] v∈[0.5,2.5]; "
        "defect edge: SURFACE_CURVE; 3D LINE (1,0.5,0)→(3,0.5,0); "
        "PCurve LINE in UV (1.0,0.5)→(3.0,0.5) references RECTANGULAR_TRIMMED_SURFACE "
        "directly — UV coords in base-surface frame, not trimmed-surface local frame; "
        "FixAddPCurve constructs pcurve in base-surface coords, missing trim "
        "translation from (u1,v1)=(1,0.5); OCC heals silently; shape(1)/shape(1)"
    ),
)

# Base surface: PLANE Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
base_plane = f.plane(plc)

# Host surface: RECTANGULAR_TRIMMED_SURFACE u∈[1,3], v∈[0.5,2.5]
# This is the surface the ADVANCED_FACE references.
trimmed_surf = f.rectangular_trimmed_surface(base_plane, 1.0, 3.0, 0.5, 2.5)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners in 3D — corners of the trimmed rectangle:
# (1,0.5,0), (3,0.5,0), (3,2.5,0), (1,2.5,0)
p_a = f.cartesian_point((1.0, 0.5, 0.0))
p_b = f.cartesian_point((3.0, 0.5, 0.0))
p_c = f.cartesian_point((3.0, 2.5, 0.0))
p_d = f.cartesian_point((1.0, 2.5, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) with proper pcurves.
# UV coords are in the BASE surface frame (u∈[1,3], v∈[0.5,2.5]).
def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve on trimmed_surf."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{trimmed_surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge_with_pc(v_b, v_c, (3.0, 0.5, 0.0), (0., 1., 0.), 2.0, (3.0, 0.5), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (3.0, 2.5, 0.0), (-1., 0., 0.), 2.0, (3.0, 2.5), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (1.0, 2.5, 0.0), (0., -1., 0.), 2.0, (1.0, 2.5), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
# THE CATALOG MECHANISM: pcurve UV uses BASE-surface coordinates.
# The base-surface bottom edge of the trim runs along v=0.5 (base v), u from 1 to 3.
# This is the "missing trim translation" defect: the UV coords (1.0,0.5) to (3.0,0.5)
# are in the base-surface frame. FixAddPCurve would compute pcurve in base coords
# rather than the trimmed-surface local offset; OCC heals.

# 3D curve: LINE from (1,0.5,0) to (3,0.5,0)
line_p  = f.cartesian_point((1.0, 0.5, 0.0))
line_d  = f.direction((1.0, 0.0, 0.0))
line_v  = f.vector(line_d, 2.0)
line_3d = f.line(line_p, line_v)

# PCurve: LINE in UV using BASE-surface coordinates (u from 1 to 3, v=0.5)
# — these are base-surface UV, not trimmed-surface local UV (which would be 0..2 x 0..2).
pc_start = f.cartesian_point((1.0, 0.5))
pc_dir   = f.direction((1.0, 0.0))
pc_vec   = f.vector(pc_dir, 2.0)
pc_line  = f.line(pc_start, pc_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('trim_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('trim_base_pc',#{trimmed_surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('trim_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('trim_base_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], trimmed_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
