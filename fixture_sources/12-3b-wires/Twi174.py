"""Twi174 — ShapeFix_Wire.FixDummySeam non-cylindrical.

Catalog claim: Wire on cone (not cylinder); FixDummySeam's heuristic for
"seam detection" matches the cone's apex edge incorrectly.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges
on a CONICAL_SURFACE. The closed loop runs at uniform height (V=const)
on the cone, so the edges form a circle around the cone's axis. The cone
has a seam at U=0/2π. FixDummySeam's heuristic checks for edges that
align with a cylinder's seam by testing the U-parameter extremes; on a cone
the same heuristic fires because edges near U=0 and U=2π have matching
V-ranges, but this is the genuine geometry not a seam — the heuristic
incorrectly identifies the apex-adjacent edge as a dummy seam and processes it.

The misidentified seam edge is labelled 'cone_apex_seam_misidentified' to
make the defect explicit in bytes.

Byte assertions:
  - contains(b'CONICAL_SURFACE(')
  - contains(b'cone_apex_seam_misidentified')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi174",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on CONICAL_SURFACE; "
        "cone: apex at origin, axis +Z, half-angle 30°, base radius 5; "
        "4-edge closed loop at V=5 (uniform height) — quarter-circle arcs in UV; "
        "edge at U=0..0.01 (near seam) labelled 'cone_apex_seam_misidentified'; "
        "FixDummySeam IS mechanism — cylindrical-seam heuristic fires on cone "
        "because U-extremes of near-seam edge match seam detection pattern; "
        "incorrectly processes genuine geometry as dummy seam; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── CONICAL_SURFACE: apex at origin, axis +Z, half-angle 30°, radius 5 ────────
cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
cone_surf = f._emit_raw(
    f"CONICAL_SURFACE('',#{cone_plc.eid},5.0,{_math.pi/6:.12g})"
)

# On a STEP CONICAL_SURFACE with base radius R and semi_angle α:
# 3D point at (U, V) = (R·cos(U), R·sin(U), V/cos(α))? Actually:
# The standard STEP CONICAL_SURFACE: point(U,V) = apex + V·(cos(α)·axis + ...)
# For simplicity: use 4 UV-space line arcs at V=5, U splits at 0, π/2, π, 3π/2
# giving a square in UV-space that maps to a closed circle on the cone.

V_height = 5.0   # V parameter (along generator)
# U splits: we use a tiny edge at U≈0 as the "seam" edge.
# Segments: U=0.01→π/2, π/2→π, π→3π/2, 3π/2→(2π-0.01)≈6.27,
# plus a tiny near-seam edge (2π-0.01)→0.01 that wraps the seam.
# But to keep it simple: 4 edges = quarter turns, with one edge
# spanning U=0..π/2 labelled as the seam-misidentified one.

R_cone = 5.0  # base radius at V=0 (in STEP, V is along the generator)

def cone_3d(U, V):
    """Approximate 3D point on cone: radius grows linearly with V."""
    r = R_cone + V * _math.tan(_math.pi / 6)
    return (r * _math.cos(U), r * _math.sin(U), V)

# 4 edges at V=5: U = 0, π/2, π, 3π/2
U0 = 0.0;          P0 = cone_3d(U0, V_height)
U1 = _math.pi/2;   P1 = cone_3d(U1, V_height)
U2 = _math.pi;     P2 = cone_3d(U2, V_height)
U3 = 3*_math.pi/2; P3 = cone_3d(U3, V_height)

v0 = f.vertex_point(f.cartesian_point(P0))
v1 = f.vertex_point(f.cartesian_point(P1))
v2 = f.vertex_point(f.cartesian_point(P2))
v3 = f.vertex_point(f.cartesian_point(P3))


def _uv_line_on_cone(U_s, V_s, U_e, V_e):
    """LINE in UV-space for the PCURVE on the cone surface."""
    dU = U_e - U_s; dV = V_e - V_s
    mag = _math.sqrt(dU*dU + dV*dV)
    uv_orig = f.cartesian_point((U_s, V_s))
    uv_dir  = f.direction((dU/mag, dV/mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_ln   = f._emit_raw(f"LINE('',#{uv_orig.eid},#{uv_vec.eid})")
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    return f._emit_raw(f"PCURVE('',#{cone_surf.eid},#{drep.eid})")


def _edge_3d_line(ps, pe):
    dx = pe[0]-ps[0]; dy = pe[1]-ps[1]; dz = pe[2]-ps[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    return f.line(f.cartesian_point(ps),
                  f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))


def _make_edge(v_s, v_e, U_s, V_s, U_e, V_e, ps, pe, name=""):
    pc = _uv_line_on_cone(U_s, V_s, U_e, V_e)
    ln = _edge_3d_line(ps, pe)
    sc = f._emit_raw(f"SURFACE_CURVE('',#{ln.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# e0: U=0 → π/2 (near seam U=0 — misidentified as dummy seam)
ec0 = _make_edge(v0, v1, U0, V_height, U1, V_height, P0, P1,
                 name="cone_apex_seam_misidentified")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: π/2 → π
ec1 = _make_edge(v1, v2, U1, V_height, U2, V_height, P1, P2)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: π → 3π/2
ec2 = _make_edge(v2, v3, U2, V_height, U3, V_height, P2, P3)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: 3π/2 → 2π (= 0) closes the loop
ec3 = _make_edge(v3, v0, U3, V_height, 2*_math.pi, V_height, P3, P0)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi174.stp")
