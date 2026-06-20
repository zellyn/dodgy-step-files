"""Twi123 — ShapeAnalysis_Wire.CheckGap2d tolerance-equality misclassification.

Catalog claim: Adjacent parametric curves with gap exactly equal to vertex
tolerance threshold (1.0E-7mm). Non-strict comparison (≤ vs <) in FP arithmetic
causes inconsistent flagging based on rounding. CheckGap2d must use strict
inequality or epsilon-band guards.

Reproducer recipe: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with two edges
on a CYLINDRICAL_SURFACE. e1 pcurve ends at UV (1.0, 0.0); e2 pcurve starts at
UV (1.0000001, 0.0) — gap of exactly 1.0E-7 in U parameter space, matching
vertex tolerance threshold. The non-strict ≤ comparison in CheckGap2d causes
inconsistent flagging at this boundary.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi123",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP on CYLINDRICAL_SURFACE (radius 1); "
        "2 SURFACE_CURVE edges: "
        "e1 pcurve ends at UV (1.0, 0.0); "
        "e2 pcurve labelled 'GAP2D_EXACT_TOL_1E7' starts at UV (1.0000001, 0.0); "
        "UV gap = 1.0E-7 exactly equals vertex tolerance threshold IS defect; "
        "CheckGap2d non-strict comparison (≤ vs <) causes inconsistent flagging; "
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

# ── 3D vertex positions on cylinder r=1 ──────────────────────────────────────
# On cylinder r=1: 3D point at U=u, V=v is (cos(u), sin(u), v).
u1_start = 0.0
u1_end   = 1.0          # e1 ends at U=1.0
u2_start = 1.0000001    # e2 starts at U=1.0000001 — gap = 1e-7
u2_end   = 2.0
V = 0.0

def cyl_3d(u, v):
    return (_math.cos(u), _math.sin(u), v)

p1s = cyl_3d(u1_start, V)
p1e = cyl_3d(u1_end,   V)
p2s = cyl_3d(u2_start, V)
p2e = cyl_3d(u2_end,   V)

v1 = f.vertex_point(f.cartesian_point(p1s))
v2 = f.vertex_point(f.cartesian_point(p1e))
v3 = f.vertex_point(f.cartesian_point(p2s))
v4 = f.vertex_point(f.cartesian_point(p2e))

# ── PCURVE helper: LINE in UV space ──────────────────────────────────────────
def make_uv_line(u0, v0_uv, u1, v1_uv, label=''):
    du = u1 - u0
    dv = v1_uv - v0_uv
    mag = _math.sqrt(du*du + dv*dv)
    uv_orig = f.cartesian_point((u0, v0_uv))
    uv_dir  = f.direction((du / mag, dv / mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_line = f._emit_raw(f"LINE('{label}',#{uv_orig.eid},#{uv_vec.eid})")
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line.eid}),#?)")
    return f._emit_raw(f"PCURVE('',#{cyl_surf.eid},#{drep.eid})")

# e1: UV from (0,0) → (1.0,0)
pcurve1 = make_uv_line(0.0, 0.0, 1.0, 0.0)

# e2: UV from (1.0000001,0) → (2.0,0) — gap of exactly 1e-7
pcurve2 = make_uv_line(1.0000001, 0.0, 2.0, 0.0, label='GAP2D_EXACT_TOL_1E7')

# ── 3D SURFACE_CURVE edges ────────────────────────────────────────────────────
def make_3d_line(src, dst):
    dx, dy, dz = dst[0]-src[0], dst[1]-src[1], dst[2]-src[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    return f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag),
    )

line3d_e1 = make_3d_line(p1s, p1e)
sc_e1 = f._emit_raw(
    f"SURFACE_CURVE('',#{line3d_e1.eid},(#{pcurve1.eid}),.PCURVE_S1.)"
)
ec_e1 = f._emit_raw(f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{sc_e1.eid},.T.)")
oe1   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")

line3d_e2 = make_3d_line(p2s, p2e)
sc_e2 = f._emit_raw(
    f"SURFACE_CURVE('',#{line3d_e2.eid},(#{pcurve2.eid}),.PCURVE_S1.)"
)
ec_e2 = f._emit_raw(f"EDGE_CURVE('',#{v3.eid},#{v4.eid},#{sc_e2.eid},.T.)")
oe2   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")

# ── EDGE_LOOP: 1e-7 UV gap at e1→e2 junction ─────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi123.stp")
