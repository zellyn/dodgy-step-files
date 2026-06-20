"""Bo030 — EDGE_CURVE start VERTEX_POINT lies off the underlying LINE: inner-vertex
tolerance smaller than the deviation it bounds.

Catalog claim: An EDGE_CURVE whose endpoints are vertices declared with tolerance
1e-7 but whose 3D coordinates are 1e-3 distant from the curve evaluation at the
boundary parameter.  The vertex's "tolerance ball" doesn't actually contain the
geometry it indexes.

Mechanism IS the EDGE_CURVE/VERTEX_POINT wired into shell topology: the EDGE_CURVE's
start VERTEX_POINT is at (0, 1e-3, 0) while the underlying LINE starts at (0,0,0);
the 1e-3 deviation exceeds the global UNCERTAINTY (1e-7) so the tolerance ball does
NOT cover the deviation.  The defective EDGE_CURVE IS wired into EDGE_LOOP →
ADVANCED_FACE → CLOSED_SHELL → MANIFOLD_SOLID_BREP shell topology.

Byte assertions:
  - contains(b'EDGE_CURVE')
  - contains(b'VERTEX_POINT')
  - count_entity_def(b'CARTESIAN_POINT') == 3

Tier-3 assertion: shape_null == True
OCC behavior: silently accepts (no diagnostic, empty result); strict kernels must heal.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo030",
    defect=(
        "EDGE_CURVE start VERTEX_POINT at (0,1e-3,0) lies 1e-3 from LINE starting "
        "at (0,0,0); deviation 1e-3 >> global UNCERTAINTY 1e-7; tolerance ball does "
        "NOT cover geometric deviation; defective EDGE_CURVE IS wired into "
        "EDGE_LOOP→ADVANCED_FACE→CLOSED_SHELL→MANIFOLD_SOLID_BREP shell topology"
    ),
)

# ── Exactly 3 CARTESIAN_POINTs (byte assertion: count_entity_def == 3) ────────
# p_orig = (0,0,0)   — LINE start + plane origin + vertex C
# p_off  = (0,1e-3,0)— start VERTEX_POINT (1e-3 off the LINE) — THE DEFECT
# p_end  = (1,0,0)   — end VERTEX_POINT + vertex B
#
# Triangle: A=(0,1e-3,0), B=(1,0,0), C=(0,0,0)
# Edge AB: LINE from p_orig=(0,0,0) in +X; v_start at p_off (1e-3 off) — defect
# Edge BC: LINE from p_end to p_orig
# Edge CA: LINE from p_orig to p_off
p_orig = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
p_off  = f._emit_raw("CARTESIAN_POINT('off_by_1e-3',(0.0,1.0E-3,0.0))")
p_end  = f._emit_raw("CARTESIAN_POINT('',(1.0,0.0,0.0))")

# Vertices: A at p_off (displaced), B at p_end, C at p_orig
v_a = f._emit_raw(f"VERTEX_POINT('off',#{p_off.eid})")   # Byte: VERTEX_POINT (displaced)
v_b = f._emit_raw(f"VERTEX_POINT('',#{p_end.eid})")
v_c = f._emit_raw(f"VERTEX_POINT('',#{p_orig.eid})")

# Directions and vectors for the three edges
d_x   = f.direction(( 1.0, 0.0, 0.0))
d_neg = f.direction((-1.0, 0.0, 0.0))
d_y   = f.direction(( 0.0, 1.0, 0.0))
vec_1 = f.vector(d_x,   1.0)
vec_1n= f.vector(d_neg, 1.0)
vec_s = f.vector(d_y,   1.0e-3)

# Plane for the triangular face — normal ~+Z, placement at p_orig
zdir  = f.direction((0.0, 0.0, 1.0))
plc   = f.axis2_placement_3d(p_orig, zdir, d_x)
plane = f.plane(plc)

# ── CATALOG MECHANISM: EDGE_CURVE AB — LINE starts at p_orig=(0,0,0), ────────
# v_start = v_a at p_off=(0,1e-3,0).  Deviation = 1e-3 >> UNCERTAINTY 1e-7.
# Tolerance ball around v_a does NOT cover the LINE's geometric start point.
line_ab = f._emit_raw(f"LINE('',#{p_orig.eid},#{vec_1.eid})")  # LINE start at (0,0,0)
e_ab = f._emit_raw(
    f"EDGE_CURVE('tolerance_lying',#{v_a.eid},#{v_b.eid},#{line_ab.eid},.T.)"
)   # Byte: EDGE_CURVE; v_a IS displaced start vertex — the defect, wired in here

# Edge BC: B=(1,0,0) → C=(0,0,0), direction -X
line_bc = f._emit_raw(f"LINE('',#{p_end.eid},#{vec_1n.eid})")
e_bc = f._emit_raw(
    f"EDGE_CURVE('',#{v_b.eid},#{v_c.eid},#{line_bc.eid},.T.)"
)

# Edge CA: C=(0,0,0) → A=(0,1e-3,0), direction +Y, length 1e-3
line_ca = f._emit_raw(f"LINE('',#{p_orig.eid},#{vec_s.eid})")
e_ca = f._emit_raw(
    f"EDGE_CURVE('',#{v_c.eid},#{v_a.eid},#{line_ca.eid},.T.)"
)

# Wire into shell / brep topology — IS the mechanism path
oe_ab = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e_ab.eid},.T.)")
oe_bc = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e_bc.eid},.T.)")
oe_ca = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e_ca.eid},.T.)")
loop  = f._emit_raw(
    f"EDGE_LOOP('',({oe_ab.ref()},{oe_bc.ref()},{oe_ca.ref()}))"
)
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('bo030_vtx_tol_underflow',(#{face.eid}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('bo030_solid',#{shell.eid})")

f.add_product_chain(msb, mode="brep_shape")
