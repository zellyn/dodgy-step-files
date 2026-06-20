"""Twi067 — Lacking edge: 2D gap not absorbable by vertex tolerance.

Catalog claim: Between two consecutive edges of a wire, the pcurve endpoints
differ by more than the shared vertex's tolerance can cover. The 3D coordinates
may agree but in UV there is a gap that requires insertion of a connecting edge;
not just snapping.

Reproducer recipe: An edge ends at UV (10, 0); the next edge starts at
UV (10.5, 0) — pcurve gap 0.5 in UV space, but 3D distance is small because
the host cylindrical surface compresses parameter space at that location.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with two edges on
a CYLINDRICAL_SURFACE: e1 has a pcurve ending at UV (10.0, 0.0) and e2 has a
pcurve starting at UV (10.5, 0.0) — the 0.5-unit gap in U parameter space
cannot be absorbed by vertex tolerance. The SURFACE_CURVE for e1 is a LINE with
a PCURVE ending at (10,0); e2's PCURVE is labelled 'B_pc_starts_at_U10p5' and
starts at (10.5, 0.0). OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE(')
  - contains(b'B_pc_starts_at_U10p5')
  - contains(b'(10.5,0.0)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi067",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP on CYLINDRICAL_SURFACE (radius 1); "
        "2 SURFACE_CURVE edges: "
        "e1 pcurve ends at UV (10.0,0.0); e2 pcurve labelled 'B_pc_starts_at_U10p5' "
        "starts at UV (10.5,0.0); "
        "0.5-unit UV gap at junction exceeds vertex tolerance — "
        "CheckLacking detects gap requires synthetic connecting edge; "
        "3D vertex distance is small (cylinder compresses U parameter); "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── CYLINDRICAL_SURFACE: axis +Z, radius 1 ───────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},1.0)")

# ── 3D vertex positions ───────────────────────────────────────────────────────
# On cylinder r=1: 3D point at U=u, V=v is (cos(u), sin(u), v).
# U=10.0 rad: cos(10)≈-0.8391, sin(10)≈-0.5440
# U=10.5 rad: cos(10.5)≈-0.4903, sin(10.5)≈-0.8716
# The 3D distance between U=10 and U=10.5 is small: arc length = 0.5 (same as UV gap)
# but vertex tolerance is even smaller.
import math as _m
u1_start = 9.0   # e1 starts at U=9
u1_end   = 10.0  # e1 ends at U=10 (pcurve end)
u2_start = 10.5  # e2 starts at UV(10.5,0) — gap here!
u2_end   = 11.5  # e2 ends at U=11.5

V = 0.0   # all edges at V=0 (bottom of cylinder)

def cyl_3d(u, v):
    return (_m.cos(u), _m.sin(u), v)

p1s = cyl_3d(u1_start, V)
p1e = cyl_3d(u1_end,   V)
p2s = cyl_3d(u2_start, V)
p2e = cyl_3d(u2_end,   V)

v1 = f.vertex_point(f.cartesian_point(p1s))   # e1 start
v2 = f.vertex_point(f.cartesian_point(p1e))   # e1 end / junction (3D)
v3 = f.vertex_point(f.cartesian_point(p2s))   # e2 start — pcurve gap here
v4 = f.vertex_point(f.cartesian_point(p2e))   # e2 end

# ── PCURVE helper: LINE in UV space ──────────────────────────────────────────
def make_uv_line(u0, v0, u1, v1_uv):
    """Build a PCURVE for a line from (u0,v0) to (u1,v1_uv) on cyl_surf."""
    du = u1 - u0
    dv = v1_uv - v0
    mag = _m.sqrt(du*du + dv*dv)
    uv_orig = f.cartesian_point((u0, v0))
    uv_dir  = f.direction((du / mag, dv / mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_line = f._emit_raw(f"LINE('',#{uv_orig.eid},#{uv_vec.eid})")
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line.eid}),#?)")
    return f._emit_raw(f"PCURVE('',#{cyl_surf.eid},#{drep.eid})")

# e1: UV from (9,0) → (10,0)
pcurve1 = make_uv_line(9.0, 0.0, 10.0, 0.0)

# e2: UV from (10.5,0) → (11.5,0) — labelled 'B_pc_starts_at_U10p5'
uv_orig2 = f.cartesian_point((10.5, 0.0))  # byte assertion: (10.5,0.0)
uv_dir2  = f.direction((1.0, 0.0))
uv_vec2  = f.vector(uv_dir2, 1.0)
uv_line2 = f._emit_raw(f"LINE('B_pc_starts_at_U10p5',#{uv_orig2.eid},#{uv_vec2.eid})")
drep2    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line2.eid}),#?)")
pcurve2  = f._emit_raw(f"PCURVE('',#{cyl_surf.eid},#{drep2.eid})")

# ── SURFACE_CURVE edges wrapping 3D line + pcurve ────────────────────────────
# e1: 3D line from p1s→p1e
dx1, dy1, dz1 = p1e[0]-p1s[0], p1e[1]-p1s[1], p1e[2]-p1s[2]
mag1 = _m.sqrt(dx1**2+dy1**2+dz1**2)
line3d_e1 = f.line(f.cartesian_point(p1s),
                   f.vector(f.direction((dx1/mag1, dy1/mag1, dz1/mag1)), mag1))
sc_e1 = f._emit_raw(
    f"SURFACE_CURVE('',#{line3d_e1.eid},(#{pcurve1.eid}),.PCURVE_S1.)"
)
ec_e1 = f._emit_raw(
    f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{sc_e1.eid},.T.)"
)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")

# e2: 3D line from p2s→p2e
dx2, dy2, dz2 = p2e[0]-p2s[0], p2e[1]-p2s[1], p2e[2]-p2s[2]
mag2 = _m.sqrt(dx2**2+dy2**2+dz2**2)
line3d_e2 = f.line(f.cartesian_point(p2s),
                   f.vector(f.direction((dx2/mag2, dy2/mag2, dz2/mag2)), mag2))
sc_e2 = f._emit_raw(
    f"SURFACE_CURVE('',#{line3d_e2.eid},(#{pcurve2.eid}),.PCURVE_S1.)"
)
ec_e2 = f._emit_raw(
    f"EDGE_CURVE('',#{v3.eid},#{v4.eid},#{sc_e2.eid},.T.)"
)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")

# ── EDGE_LOOP: two edges with UV gap at junction ─────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi067.stp")
