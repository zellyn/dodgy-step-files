"""Twi069 — Wire 2D-gap analysis must enumerate all pcurve gaps.

Catalog claim: Pcurve-space analogue of Twi068. A wire whose pcurves have
multiple gaps in UV should produce a per-junction list. Often produced when
the wire is built by stitching pcurves from different sources without parameter
alignment.

Reproducer recipe: A wire where edges' pcurve endpoints land at U values that
disagree at junctions 1 and 3.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with three
SURFACE_CURVE edges on a CYLINDRICAL_SURFACE. The pcurves have UV endpoint
mismatches at two junctions:
- Junction 1 (e1/e2): e1 pcurve ends at U=1.0, e2 pcurve starts at U=1.5
- Junction 2 (e2/e3): e2 pcurve ends at U=3.0, e3 pcurve starts at U=3.4
Both (1.5,0.0) and (3.4,0.0) are pcurve start points. CheckGaps2d must
enumerate all UV gaps, not stop at the first. OCC sees a GEOMETRIC_CURVE_SET
and returns empty.

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE(')
  - contains(b'(1.5,0.0)')
  - contains(b'(3.4,0.0)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi069",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP on CYLINDRICAL_SURFACE (radius 1); "
        "3 SURFACE_CURVE edges with pcurve UV gaps at 2 junctions: "
        "junction 1: e1 pcurve ends at (1.0,0.0), e2 pcurve starts at (1.5,0.0) — gap 0.5; "
        "junction 2: e2 pcurve ends at (3.0,0.0), e3 pcurve starts at (3.4,0.0) — gap 0.4; "
        "CheckGaps2d must enumerate both UV gaps per-junction; "
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
# On cylinder r=1: point at (u,v) → (cos(u), sin(u), v).
# We use 3D coords matching the gap pcurve starts (not perfect, the point is UV mismatch)
def cyl_3d(u, v=0.0):
    return (_math.cos(u), _math.sin(u), v)

# e1: U from 0 to 1.0 (pcurve)
v1s = f.vertex_point(f.cartesian_point(cyl_3d(0.0)))
v1e = f.vertex_point(f.cartesian_point(cyl_3d(1.0)))   # e1 3D end
# e2 starts at 3D position for U=1.5 (pcurve gap: should be U=1.0 but is 1.5)
v2s = f.vertex_point(f.cartesian_point(cyl_3d(1.5)))   # e2 3D start
v2e = f.vertex_point(f.cartesian_point(cyl_3d(3.0)))   # e2 3D end
# e3 starts at 3D position for U=3.4 (pcurve gap: should be U=3.0 but is 3.4)
v3s = f.vertex_point(f.cartesian_point(cyl_3d(3.4)))   # e3 3D start
v3e = f.vertex_point(f.cartesian_point(cyl_3d(4.5)))   # e3 3D end

# ── PCURVE helper ─────────────────────────────────────────────────────────────
def make_uv_line(u0, v0, u1, v1_):
    du = u1 - u0
    dv = v1_ - v0
    mag = _math.sqrt(du*du + dv*dv)
    uv_orig = f.cartesian_point((u0, v0))
    uv_dir  = f.direction((du / mag, dv / mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_line = f._emit_raw(f"LINE('',#{uv_orig.eid},#{uv_vec.eid})")
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line.eid}),#?)")
    return f._emit_raw(f"PCURVE('',#{cyl_surf.eid},#{drep.eid})")

# Pcurves with intentional UV gaps at junctions
pc_e1 = make_uv_line(0.0, 0.0, 1.0, 0.0)    # ends at (1.0, 0.0)

# e2 pcurve: starts at (1.5, 0.0) — byte assertion; ends at (3.0, 0.0)
uv_orig_e2 = f.cartesian_point((1.5, 0.0))   # byte assertion: (1.5,0.0)
uv_dir_e2  = f.direction((1.0, 0.0))
uv_vec_e2  = f.vector(uv_dir_e2, 1.5)
uv_line_e2 = f._emit_raw(f"LINE('',#{uv_orig_e2.eid},#{uv_vec_e2.eid})")
drep_e2    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line_e2.eid}),#?)")
pc_e2      = f._emit_raw(f"PCURVE('',#{cyl_surf.eid},#{drep_e2.eid})")

# e3 pcurve: starts at (3.4, 0.0) — byte assertion; ends at (4.5, 0.0)
uv_orig_e3 = f.cartesian_point((3.4, 0.0))   # byte assertion: (3.4,0.0)
uv_dir_e3  = f.direction((1.0, 0.0))
uv_vec_e3  = f.vector(uv_dir_e3, 1.1)
uv_line_e3 = f._emit_raw(f"LINE('',#{uv_orig_e3.eid},#{uv_vec_e3.eid})")
drep_e3    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line_e3.eid}),#?)")
pc_e3      = f._emit_raw(f"PCURVE('',#{cyl_surf.eid},#{drep_e3.eid})")

# ── SURFACE_CURVE edges (3D LINE + pcurve) ────────────────────────────────────
def make_3d_line(p0, p1):
    dx, dy, dz = p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]
    mag = _math.sqrt(dx**2+dy**2+dz**2)
    return f.line(f.cartesian_point(p0),
                  f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))

p1s = cyl_3d(0.0); p1e = cyl_3d(1.0)
p2s = cyl_3d(1.5); p2e = cyl_3d(3.0)
p3s = cyl_3d(3.4); p3e = cyl_3d(4.5)

sc_e1 = f._emit_raw(
    f"SURFACE_CURVE('',#{make_3d_line(p1s, p1e).eid},(#{pc_e1.eid}),.PCURVE_S1.)"
)
ec_e1 = f._emit_raw(f"EDGE_CURVE('',#{v1s.eid},#{v1e.eid},#{sc_e1.eid},.T.)")
oe1   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")

sc_e2 = f._emit_raw(
    f"SURFACE_CURVE('',#{make_3d_line(p2s, p2e).eid},(#{pc_e2.eid}),.PCURVE_S1.)"
)
ec_e2 = f._emit_raw(f"EDGE_CURVE('',#{v2s.eid},#{v2e.eid},#{sc_e2.eid},.T.)")
oe2   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")

sc_e3 = f._emit_raw(
    f"SURFACE_CURVE('',#{make_3d_line(p3s, p3e).eid},(#{pc_e3.eid}),.PCURVE_S1.)"
)
ec_e3 = f._emit_raw(f"EDGE_CURVE('',#{v3s.eid},#{v3e.eid},#{sc_e3.eid},.T.)")
oe3   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

# ── EDGE_LOOP: UV gaps at junctions 1 and 2 ──────────────────────────────────
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi069.stp")
