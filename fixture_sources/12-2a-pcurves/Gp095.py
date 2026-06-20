"""Gp095 — ShapeFix_Edge.FixVertexTolerance face-vertex-conflict.

Catalog claim: Vertex shared by two faces with conflicting tolerance
requirements; FixVertexTolerance picks first face's requirement, ignoring
second. Fixture has vertex #31 on two PLANE faces with independent
BRep_Tool::Tolerance() values.

STEP mechanism (literal):
  - Two adjacent PLANE faces sharing a common edge (and thus sharing two
    vertices). One of these shared vertices (v_shared) is placed slightly off
    the mathematical intersection of the two planes by DELTA (within the
    UNCERTAINTY tolerance).
  - Face 1: PLANE at Z=0 (the XY plane). Face 2: PLANE at X=0 (the YZ plane).
    The shared edge runs along the Y-axis from (0,0,0) to (0,1,0).
  - v_shared (the vertex at the origin) is displaced to (DELTA, 0, DELTA) in
    3D — it lies on neither plane exactly. Its tolerance requirement on Face 1
    is DELTA (distance to Z=0 plane), and on Face 2 is also DELTA (distance to
    X=0 plane).
  - THE CATALOG MECHANISM: FixVertexTolerance escalates v_shared's tolerance
    to DELTA to satisfy Face 1's requirement. It then checks Face 2 using the
    first face's tolerance value, not re-computing for Face 2's metric.
    OCC heals by absorbing the mismatch within the escalated tolerance.
  - Global UNCERTAINTY is the builder default (1.0E-7); DELTA=0.005 sits
    ~50000x above tolerance — OCC's healer must escalate v_shared's
    tolerance substantially. The catalog Expected (shape(1)/shape(1))
    confirms OCC heals it; the catalog mechanism is the silent escalation
    plus the first-face-wins ordering bug, not a strict-tolerance failure.

NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).
"""
from step_corpus.step_builder import StepFile

DELTA = 0.005   # displacement well above default UNCERTAINTY=1e-7;
                # OCC's healer escalates tolerance to absorb it

f = StepFile(
    catalog_id="Gp095",
    defect=(
        f"Two adjacent PLANE faces (Z=0, X=0) sharing edge along Y-axis; "
        f"shared vertex at origin displaced to (DELTA,0,DELTA) where DELTA={DELTA} "
        f"(well above default UNCERTAINTY=1e-7); FixVertexTolerance escalates the "
        f"vertex tolerance to absorb the mismatch but uses the first-face metric "
        f"without re-checking the second face; OCC heals to shape(1)/shape(1)"
    ),
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face 1: PLANE at Z=0 (XY-plane) ──────────────────────────────────────────
orig1 = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
ydir  = f.direction((0.0, 1.0, 0.0))
plc1  = f.axis2_placement_3d(orig1, zdir, xdir)
surf1 = f.plane(plc1)

# ── Face 2: PLANE at X=0 (YZ-plane) ──────────────────────────────────────────
orig2 = f.cartesian_point((0.0, 0.0, 0.0))
nx    = f.direction((1.0, 0.0, 0.0))   # normal to YZ plane
plc2  = f.axis2_placement_3d(orig2, nx, ydir)
surf2 = f.plane(plc2)

# ── Vertices ──────────────────────────────────────────────────────────────────
# v_shared: the origin vertex, displaced by DELTA to create the conflict.
# Exact intersection of both planes is (0,0,0); we place it at (DELTA,0,DELTA).
# Distance to Z=0 plane: DELTA (z-component).
# Distance to X=0 plane: DELTA (x-component).
p_shared_off = f.cartesian_point((DELTA, 0.0, DELTA))   # THE DISPLACED VERTEX
v_shared     = f.vertex_point(p_shared_off)

# Other shared vertex: exact top of shared edge (0,1,0)
p_top_shared = f.cartesian_point((0.0, 1.0, 0.0))
v_top_shared = f.vertex_point(p_top_shared)

# Face 1 only vertices: (1,0,0) and (1,1,0)
p_f1_br = f.cartesian_point((1.0, 0.0, 0.0))
p_f1_tr = f.cartesian_point((1.0, 1.0, 0.0))
v_f1_br = f.vertex_point(p_f1_br)
v_f1_tr = f.vertex_point(p_f1_tr)

# Face 2 only vertices: (0,0,-1) and (0,1,-1)
p_f2_bl = f.cartesian_point((0.0, 0.0, -1.0))
p_f2_tl = f.cartesian_point((0.0, 1.0, -1.0))
v_f2_bl = f.vertex_point(p_f2_bl)
v_f2_tl = f.vertex_point(p_f2_tl)

# ── Helper: build SURFACE_CURVE edge with pcurve ──────────────────────────────
def mk_edge_with_pc(vs, ve, surf, p3, d3t, len3, p2t, d2t):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# ── Face 1 edges (XY-plane Z=0 rectangle): shared_off→f1_br→f1_tr→top_shared→shared_off
# THE CATALOG MECHANISM: v_shared is displaced by DELTA in Z — off the Z=0 plane.
# On Face 1, FixVertexTolerance must escalate tolerance to DELTA to accommodate it.

# Bottom of face 1: shared_off -> f1_br  (approx along X at z~0)
e1_bot = mk_edge_with_pc(
    v_shared, v_f1_br,
    surf1,
    (DELTA, 0.0, DELTA), (1., 0., 0.), 1.0 - DELTA,  # approx x-direction
    (0.0, 0.0), (1., 0.),
)

# Right of face 1: f1_br -> f1_tr  (along Y)
e1_right = mk_edge_with_pc(
    v_f1_br, v_f1_tr,
    surf1,
    (1.0, 0.0, 0.0), (0., 1., 0.), 1.0,
    (1.0, 0.0), (0., 1.),
)

# Top of face 1: f1_tr -> top_shared  (along -X)
e1_top = mk_edge_with_pc(
    v_f1_tr, v_top_shared,
    surf1,
    (1.0, 1.0, 0.0), (-1., 0., 0.), 1.0,
    (1.0, 1.0), (-1., 0.),
)

# Shared edge (left of face 1): top_shared -> shared_off  (along -Y)
# This edge is shared with Face 2; placed on Face 1 side here.
e_shared = mk_edge_with_pc(
    v_top_shared, v_shared,
    surf1,
    (0.0, 1.0, 0.0), (0., -1., 0.), 1.0,
    (0.0, 1.0), (0., -1.),
)

loop1 = f.edge_loop([
    f.oriented_edge(e1_bot,    True),
    f.oriented_edge(e1_right,  True),
    f.oriented_edge(e1_top,    True),
    f.oriented_edge(e_shared,  True),
])
face1 = f.advanced_face([f.face_outer_bound(loop1)], surf1)

# ── Face 2 edges (YZ-plane X=0 rectangle): shared_off→top_shared→f2_tl→f2_bl→shared_off
# v_shared is also off the X=0 plane by DELTA (x-component).
# FixVertexTolerance should re-evaluate tolerance for Face 2; the bug is it uses
# Face 1's tolerance without recomputing for Face 2's metric.

# Shared edge reused (with reversed orientation on Face 2)
# Bottom of face 2 (along Z from z=-1 to z=0): f2_bl -> shared_off
e2_bot = mk_edge_with_pc(
    v_f2_bl, v_shared,
    surf2,
    (0.0, 0.0, -1.0), (0., 0., 1.), 1.0,
    (0.0, -1.0), (0., 1.),
)

# Left of face 2: f2_tl -> f2_bl  (along -Z)
e2_left = mk_edge_with_pc(
    v_f2_tl, v_f2_bl,
    surf2,
    (0.0, 1.0, -1.0), (0., -1., 0.), 1.0,
    (1.0, -1.0), (-1., 0.),
)

# Top of face 2: top_shared -> f2_tl  (along -Z from z=0 to z=-1)
e2_top = mk_edge_with_pc(
    v_top_shared, v_f2_tl,
    surf2,
    (0.0, 1.0, 0.0), (0., 0., -1.), 1.0,
    (1.0, 1.0), (0., -1.),
)

loop2 = f.edge_loop([
    f.oriented_edge(e_shared,  False),   # shared edge reversed
    f.oriented_edge(e2_top,    True),
    f.oriented_edge(e2_left,   True),
    f.oriented_edge(e2_bot,    True),
])
face2 = f.advanced_face([f.face_outer_bound(loop2)], surf2)

shell = f.open_shell([face1, face2])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
