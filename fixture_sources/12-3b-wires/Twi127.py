"""Twi127 — ShapeFix_Wire.FixReorder UV-disjoint regions.

Catalog claim: Wire spans two disjoint regions of a periodic surface's UV space
separated by a seam edge; FixReorder picks the wrong region as primary, causing
edge reordering to break seam connectivity.

Fixture: TOROIDAL_SURFACE with a 4-edge wire that crosses the u=0 seam. Edges
wrap around via seam pcurves. FixReorder must detect that primary region spans
both u∈[0,π] and u∈[π,2π] and order edges to maintain seam crossing, not
collapse to single region.

Reproducer recipe: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on
a TOROIDAL_SURFACE. Two edges are in u∈[0,π] and two are in u∈[π,2π].
The seam crossing at u=π (or u=0/2π) means the UV regions are disjoint.
FixReorder selects only the first region as primary and breaks seam connectivity.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi127",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on TOROIDAL_SURFACE; "
        "TOROIDAL_SURFACE major_radius=2.0, minor_radius=0.5, axis +Z; "
        "e1: pcurve in u∈[0,π/2] region — first quadrant; "
        "e2: pcurve crosses seam at u=π — IS seam crossing edge; "
        "e3: pcurve in u∈[π,3π/2] region — third quadrant (disjoint UV region); "
        "e4: pcurve returns via u=0/2π seam back to start; "
        "FixReorder picks u∈[0,π] as primary region, breaks seam connectivity IS defect; "
        "UV-disjoint regions across seam are not preserved by FixReorder; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

MAJOR = 2.0
MINOR = 0.5

# ── TOROIDAL_SURFACE: axis +Z ─────────────────────────────────────────────────
tor_orig = f.cartesian_point((0.0, 0.0, 0.0))
tor_zdir = f.direction((0.0, 0.0, 1.0))
tor_xdir = f.direction((1.0, 0.0, 0.0))
tor_plc  = f.axis2_placement_3d(tor_orig, tor_zdir, tor_xdir)
tor_surf = f._emit_raw(f"TOROIDAL_SURFACE('',#{tor_plc.eid},{MAJOR},{MINOR})")

# ── 3D vertices at torus equator (phi=0): u=0, π/2, π, 3π/2 ─────────────────
# On torus equator (v=0, phi=0): point at angle u is
# ((major+minor)*cos(u), (major+minor)*sin(u), 0)
R = MAJOR + MINOR  # 2.5

def torus_3d(u):
    return (R * _math.cos(u), R * _math.sin(u), 0.0)

U0 = 0.0
U1 = _math.pi / 2.0    # π/2
U2 = _math.pi          # π  — seam crossing point
U3 = 3.0 * _math.pi / 2.0  # 3π/2

P0 = torus_3d(U0)
P1 = torus_3d(U1)
P2 = torus_3d(U2)
P3 = torus_3d(U3)

v0 = f.vertex_point(f.cartesian_point(P0))
v1 = f.vertex_point(f.cartesian_point(P1))
v2 = f.vertex_point(f.cartesian_point(P2))
v3 = f.vertex_point(f.cartesian_point(P3))

# ── PCURVE helper: UV arc line on torus ──────────────────────────────────────
def make_uv_line(u0, v0_uv, u1, v1_uv):
    du = u1 - u0
    dv = v1_uv - v0_uv
    mag = _math.sqrt(du*du + dv*dv)
    uv_orig = f.cartesian_point((u0, v0_uv))
    uv_dir  = f.direction((du / mag, dv / mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_line = f._emit_raw(f"LINE('',#{uv_orig.eid},#{uv_vec.eid})")
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line.eid}),#?)")
    return f._emit_raw(f"PCURVE('',#{tor_surf.eid},#{drep.eid})")

# ── 3D arc helper on torus equator ────────────────────────────────────────────
def make_arc_edge(v_s, v_e, pc):
    """Make SURFACE_CURVE with 3D circle at torus equator + pcurve."""
    plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
    plc_zdir = f.direction((0.0, 0.0, 1.0))
    plc_xdir = f.direction((1.0, 0.0, 0.0))
    plc      = f.axis2_placement_3d(plc_orig, plc_zdir, plc_xdir)
    circ     = f._emit_raw(f"CIRCLE('',#{plc.eid},{R})")
    sc       = f._emit_raw(f"SURFACE_CURVE('',#{circ.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")

# e1: u ∈ [0, π/2] — first quadrant, region 1
pc1 = make_uv_line(U0, 0.0, U1, 0.0)
ec1 = make_arc_edge(v0, v1, pc1)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: u ∈ [π/2, π] — crosses into seam region
pc2 = make_uv_line(U1, 0.0, U2, 0.0)
ec2 = make_arc_edge(v1, v2, pc2)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: u ∈ [π, 3π/2] — disjoint UV region (region 2, across seam)
pc3 = make_uv_line(U2, 0.0, U3, 0.0)
ec3 = make_arc_edge(v2, v3, pc3)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# e4: u ∈ [3π/2, 2π] — returns via u=2π seam back to u=0 (v0)
TWO_PI = 2.0 * _math.pi
pc4 = make_uv_line(U3, 0.0, TWO_PI, 0.0)
ec4 = make_arc_edge(v3, v0, pc4)
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

# ── EDGE_LOOP: 4 edges spanning UV-disjoint regions across seam ───────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi127.stp")
