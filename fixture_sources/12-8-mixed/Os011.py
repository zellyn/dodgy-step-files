"""Os011 — ThruSections loft used outside its supported envelope.

Catalog claim: ThruSections is invoked where one section is a single VERTEX_POINT
and the other is a closed wire profile (a CIRCLE edge).  Mixing a point section
with a wire section is outside the algorithm's supported envelope (WrongUsage).

Mechanism IS a GEOMETRIC_CURVE_SET containing:
  - Profile 1: a VERTEX_POINT entity (point section)
  - Profile 2: a closed EDGE_LOOP with a CIRCLE edge (wire section at z=5)
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'VERTEX_POINT')
  - contains(b'CIRCLE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os011",
    defect=(
        "GEOMETRIC_CURVE_SET containing two loft profiles; "
        "profile 1: VERTEX_POINT at origin (point section — WrongUsage); "
        "profile 2: closed EDGE_LOOP with CIRCLE edge of radius 5 at z=5; "
        "ThruSections does not support point-to-wire loft; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Profile 1: single VERTEX_POINT at origin ──────────────────────────────────
vp_pt  = f.cartesian_point((0.0, 0.0, 0.0))
v_apex = f.vertex_point(vp_pt)   # VERTEX_POINT — byte assertion ✓

# ── Profile 2: closed circle wire at z=5 ─────────────────────────────────────
cplc_orig = f.cartesian_point((0.0, 0.0, 5.0))
cplc_zdir = f.direction((0.0, 0.0, 1.0))
cplc_xdir = f.direction((1.0, 0.0, 0.0))
cplc      = f.axis2_placement_3d(cplc_orig, cplc_zdir, cplc_xdir)
circle    = f.circle(cplc, 5.0)   # CIRCLE — byte assertion ✓

p_seam = f.cartesian_point((5.0, 0.0, 5.0))
v_seam = f.vertex_point(p_seam)

ec_circ = f._emit_raw(
    f"EDGE_CURVE('circle_edge',#{v_seam.eid},#{v_seam.eid},#{circle.eid},.T.)"
)
oe_circ = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_circ.eid},.T.)")
loop2   = f._emit_raw(f"EDGE_LOOP('wire_profile',(#{oe_circ.eid}))")

# ── GEOMETRIC_CURVE_SET wrapping vertex + wire loop ──────────────────────────
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{v_apex.eid},#{loop2.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os011.stp")
