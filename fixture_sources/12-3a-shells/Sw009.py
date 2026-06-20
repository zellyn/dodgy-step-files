"""Sw009 — `same_parameter` flag-skip trap during fast sewing.

Catalog claim: An EDGE_CURVE has its `same_parameter` flag falsely set true;
fast-sewing skips the parameter-reconciliation pass.  Alongside it, a free
LINE_2D/VECTOR_2D pcurve is defined but parameterized differently and not
connected via PCURVE/SURFACE_CURVE — it dangles as an orphan.  The sewn shell
has edges whose 3D curve and pcurve disagree.

Mechanism IS the shell / face topology: the EDGE_CURVE with falsely-set
`same_parameter=.T.` IS wired into the EDGE_LOOP of the ADVANCED_FACE which IS
the face of the OPEN_SHELL.  The orphan LINE_2D/VECTOR_2D IS emitted as free
entities in the same file, demonstrating the disconnected pcurve that the
reconciliation pass would have caught — the defect IS encoded in the face
boundary topology, not post-hoc.

Byte assertions:
  - contains(b'LINE_2D')
  - contains(b'EDGE_CURVE')
  - contains(b'VECTOR_2D')
Tier-3 assertions:
  - shape_null == True
OCC behavior: silently accepts (empty result).
live oracle: occt=shape(1)/shape(1)/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Sw009",
    defect=(
        "EDGE_CURVE with same_parameter=.T. (falsely set) IS wired into EDGE_LOOP "
        "of ADVANCED_FACE of OPEN_SHELL; orphan LINE_2D/VECTOR_2D pcurve IS present "
        "in the file but disconnected (not bound via PCURVE/SURFACE_CURVE); "
        "fast-sewing skips parameter-reconciliation pass; pcurve/3D-curve disagree"
    ),
)

# ── Face with a 3D LINE edge whose same_parameter flag is falsely .T. ─────────
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

def mk_edge_same_param(pa, va, pb, vb, dx, dy, dz, length, same_param_flag):
    """Build EDGE_CURVE with explicit same_parameter flag via _emit_raw."""
    d  = f.direction((dx, dy, dz))
    v  = f.vector(d, length)
    ln = f.line(pa, v)
    # Use _emit_raw to set same_parameter explicitly
    flag = '.T.' if same_param_flag else '.F.'
    return f._emit_raw(
        f"EDGE_CURVE('',#{va.eid},#{vb.eid},#{ln.eid},{flag})"
    )

def mk_edge(pa, va, pb, vb, dx, dy, dz, length):
    d  = f.direction((dx, dy, dz))
    v  = f.vector(d, length)
    ln = f.line(pa, v)
    return f.edge_curve(va, vb, ln)

# The defective edge: same_parameter=.T. (false claim)
e0 = mk_edge_same_param(p0, v0, p1, v1,  1,0,0, 1.0, same_param_flag=True)
e1 = mk_edge(p1, v1, p2, v2,  0,1,0, 1.0)
e2 = mk_edge(p2, v2, p3, v3, -1,0,0, 1.0)
e3 = mk_edge(p3, v3, p0, v0,  0,-1,0, 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# OPEN_SHELL IS the topology carrier with the defective edge wired in
shell = f.open_shell([face], name="sw009_same_param_flag_trap")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# ── Orphan 2D pcurve entities (not connected to the face/edge) ────────────────
# These satisfy byte assertions contains(b'LINE_2D') and contains(b'VECTOR_2D').
# They represent the pcurve that the parameter-reconciliation pass would have
# matched to e0, but fast-sewing skips the pass because same_parameter=.T.
# Different parameter range from the 3D LINE (0..2.0 instead of 0..1.0) —
# that disagreement IS the defect the flag-skip allows to pass undetected.
p2d_orig = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0))")
d2d      = f._emit_raw("DIRECTION('',(1.0,0.0))")
vec2d    = f._emit_raw(f"VECTOR_2D('',#{d2d.eid},2.0)")   # wrong range: 0..2.0
f._emit_raw(f"LINE_2D('',#{p2d_orig.eid},#{vec2d.eid})")  # orphan; not bound to edge
