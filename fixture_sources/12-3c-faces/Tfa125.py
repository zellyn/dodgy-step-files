"""Tfa125 — ShapeFix_Face.FixPeriodicDegenerated u-axis-degenerate.

Catalog claim: Spherical surface where U direction is degenerate at the south
pole (v=0). FixPeriodicDegenerated handles V-degenerate surfaces but assumes
U parametric direction is always non-degenerate.

Mechanism: GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a
SPHERICAL_SURFACE. The face is bounded by a single degenerate edge loop at
the south pole (v = -π/2 in surface parametrics). At the south pole all U
values map to the same 3D point, making U degenerate. FixPeriodicDegenerated
only repairs V-degenerate cases; when the degenerate axis is U the algorithm
leaves the face in an unresolvable state.

The degenerate south-pole loop is represented as a single EDGE_CURVE whose
start and end vertex coincide at the south pole (0, 0, -R).

OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'SPHERICAL_SURFACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa125",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on SPHERICAL_SURFACE; "
        "sphere radius=5.0, centred at origin; "
        "face has degenerate south-pole loop: single edge with coincident start/end vertex; "
        "south pole at (0,0,-5) — all U values map to same 3D point; "
        "U parametric direction degenerate at v=0 (south pole, v=-π/2 in natural params); "
        "FixPeriodicDegenerated assumes U non-degenerate; leaves face unresolvable; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Spherical surface ─────────────────────────────────────────────────────────
# Standard orientation: axis=(0,0,1), x-ref=(1,0,0)
# South pole at (0, 0, -5) in 3D
R = 5.0
sp_orig = f.cartesian_point((0.0, 0.0, 0.0))
sp_zdir = f.direction((0.0, 0.0, 1.0))
sp_xdir = f.direction((1.0, 0.0, 0.0))
sp_plc  = f.axis2_placement_3d(sp_orig, sp_zdir, sp_xdir)
sphere  = f._emit_raw(f"SPHERICAL_SURFACE('u_degen_sphere',#{sp_plc.eid},{R})")

# ── South pole: single 3D point, degenerate in U ─────────────────────────────
south_pt = f.cartesian_point((0.0, 0.0, -R))
v_south_a = f._emit_raw(f"VERTEX_POINT('south_pole_a',#{south_pt.eid})")
v_south_b = f._emit_raw(f"VERTEX_POINT('south_pole_b',#{south_pt.eid})")

# Degenerate edge: start and end at south pole — zero-length line
d_u = f.direction((1.0, 0.0, 0.0))
vec_zero = f.vector(d_u, 0.0)
ln_degen = f.line(south_pt, vec_zero)
ec_degen = f._emit_raw(
    f"EDGE_CURVE('degen_u_edge',#{v_south_a.eid},#{v_south_b.eid},#{ln_degen.eid},.T.)"
)
oe_degen = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_degen.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('south_pole_loop',(#{oe_degen.eid}))")
fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af   = f._emit_raw(f"ADVANCED_FACE('u_degen_face',(#{fob.eid}),#{sphere.eid},.T.)")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa125.stp")
