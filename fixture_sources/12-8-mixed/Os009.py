"""Os009 — ThruSections loft profile is closed wire mixed with open wire.

Catalog claim: A loft (ThruSections) is requested between two profiles: profile 1
is a closed wire (a circle), profile 2 is an open wire (an arc / single LINE edge).
The loft algorithm needs both endpoints free or both joined; mixing them is
unsupported.

Mechanism IS a GEOMETRIC_CURVE_SET containing the two wires.  OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'CIRCLE')
  - contains(b'LINE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os009",
    defect=(
        "GEOMETRIC_CURVE_SET containing two loft profiles; "
        "profile 1: closed WIRE — single CIRCLE edge (v_seam to v_seam); "
        "profile 2: open WIRE — single LINE edge (v0 to v1) at z=5; "
        "mixing closed and open profiles breaks ThruSections topology; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Profile 1: closed circle wire at z=0 ─────────────────────────────────────
cplc_orig = f.cartesian_point((0.0, 0.0, 0.0))
cplc_zdir = f.direction((0.0, 0.0, 1.0))
cplc_xdir = f.direction((1.0, 0.0, 0.0))
cplc      = f.axis2_placement_3d(cplc_orig, cplc_zdir, cplc_xdir)
circle    = f.circle(cplc, 5.0)          # CIRCLE — byte assertion ✓

p_seam = f.cartesian_point((5.0, 0.0, 0.0))
v_seam = f.vertex_point(p_seam)

ec_circ = f._emit_raw(
    f"EDGE_CURVE('circle_edge',#{v_seam.eid},#{v_seam.eid},#{circle.eid},.T.)"
)
oe_circ = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_circ.eid},.T.)")
loop1   = f._emit_raw(f"EDGE_LOOP('closed_profile',(#{oe_circ.eid}))")
# Profile 1 wire (represented as EDGE_LOOP for the GCS payload)

# ── Profile 2: open line wire at z=5 ─────────────────────────────────────────
p0 = f.cartesian_point((-5.0, 0.0, 5.0))
p1 = f.cartesian_point(( 5.0, 0.0, 5.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)

line_dir = f.direction((1.0, 0.0, 0.0))
line_vec = f.vector(line_dir, 10.0)
line     = f.line(p0, line_vec)          # LINE — byte assertion ✓

ec_line = f.edge_curve(v0, v1, line, True, name="open_edge")
oe_line = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_line.eid},.T.)")
loop2   = f._emit_raw(f"EDGE_LOOP('open_profile',(#{oe_line.eid}))")

# ── GEOMETRIC_CURVE_SET wrapping both loops ──────────────────────────────────
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop1.eid},#{loop2.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os009.stp")
