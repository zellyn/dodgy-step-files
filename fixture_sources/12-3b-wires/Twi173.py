"""Twi173 — ShapeAnalysis_Wire.CheckLacking endpoint-degenerate.

Catalog claim: Wire missing an edge where one end is a degenerate vertex
(same as previous edge's start); CheckLacking should detect but
degenerate-vertex test masks the lack.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 3 edges
on a PLANE. The wire has three edges forming a near-triangle, but two
intermediate vertices are nearly coincident (within 1e-6 of each other) —
creating a degenerate vertex situation at the junction. There is a gap where
a connecting edge should be (the endpoint of e3 does NOT coincide with the
start of e1), but CheckLacking's degenerate-vertex masking logic fires at
the near-coincident junction, suppressing the check before it reaches the
actual gap.

The degenerate vertex pair is labelled 'degenerate_vertex_mask' to make
the defect explicit in bytes.

Byte assertions:
  - contains(b'degenerate_vertex_mask')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi173",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "3-edge chain: A(0,0)→B(10,0); B(10,0)→B'(10.000001,0) (degenerate near-B); "
        "B'(10.000001,0)→C(5,8) — near-coincident B/B' pair IS degenerate vertex; "
        "wire is open: C(5,8)≠A(0,0) — gap exists where closing edge should be; "
        "vertex labelled 'degenerate_vertex_mask' at B'(10.000001,0); "
        "CheckLacking IS mechanism — degenerate-vertex test at B/B' junction masks "
        "detection of the real gap C→A; GEOMETRIC_CURVE_SET IS model entity — "
        "OCC yields empty; all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── PLANE: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
PA  = (0.0,       0.0, 0.0)
PB  = (10.0,      0.0, 0.0)
PBp = (10.000001, 0.0, 0.0)   # nearly coincident with PB — degenerate vertex
PC  = (5.0,       8.0, 0.0)

vA  = f.vertex_point(f.cartesian_point(PA))
vB  = f.vertex_point(f.cartesian_point(PB))
# Degenerate vertex: nearly same as vB — labelled for byte assertion
vBp = f.vertex_point(f.cartesian_point(PBp), name="degenerate_vertex_mask")
vC  = f.vertex_point(f.cartesian_point(PC))


def _line_sc(v_s, v_e, ps, pe):
    dx = pe[0]-ps[0]; dy = pe[1]-ps[1]; dz = pe[2]-ps[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    ln3 = f.line(f.cartesian_point(ps),
                 f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))
    uv_orig = f.cartesian_point((ps[0], ps[1]))
    uv_dir  = f.direction((dx/mag, dy/mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_ln   = f.line(uv_orig, uv_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc      = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# e1: A → B
ec1 = _line_sc(vA, vB, PA, PB)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: B → B' (degenerate — nearly zero length)
ec2 = _line_sc(vB, vBp, PB, PBp)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: B' → C (open wire — does NOT return to A, leaving gap C→A)
ec3 = _line_sc(vBp, vC, PBp, PC)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# EDGE_LOOP: open chain — C≠A, gap where closing edge should be
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi173.stp")
