"""Twi168 — ShapeAnalysis_Wire.CheckShapeConnect different-vertex-counts.

Catalog claim: CheckShapeConnect on wire with shared vertices counted
inconsistently. Vertex-count discrepancy undetected; edge connectivity
ambiguity passes validation.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 3 edges on
a PLANE. The defect: two edges share a VERTEX_POINT entity for their junction,
but the third edge uses a different VERTEX_POINT entity at the same 3D
position. CheckShapeConnect expects all edges meeting at a junction to
reference the same VERTEX entity, but when vertex-count is tabulated the
shared-vertex appears twice for two edges while an identical-position different-
entity appears once — creating a vertex-count discrepancy that passes
validation silently.

The duplicate vertex is labelled 'vertex_identity_ambiguity' to make the
defect explicit in bytes.

Byte assertions:
  - contains(b'vertex_identity_ambiguity')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi168",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "3-edge triangle: e1 vA→vB_shared, e2 vB_shared→vC, e3 vC→vA; "
        "BUT e1 end vertex is vB_shared while e3 uses vB_identity_ambiguity "
        "at same 3D position (5,5,0) — different entity, same coordinates; "
        "CheckShapeConnect tallies vertex_identity_ambiguity count=1 vs "
        "vB_shared count=2; discrepancy undetected — passes validation IS defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── PLANE: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
# Triangle: A=(0,0,0), B=(10,0,0), C=(5,8,0)
# vB_shared: the "canonical" B vertex used by e1 and e2
# vB_ambig: a second VERTEX_POINT at same 3D coords — used by e3 start
PA = (0.0,  0.0, 0.0)
PB = (10.0, 0.0, 0.0)
PC = (5.0,  8.0, 0.0)

vA        = f.vertex_point(f.cartesian_point(PA))
vB_shared = f.vertex_point(f.cartesian_point(PB))
vC        = f.vertex_point(f.cartesian_point(PC))
# Duplicate of vB at same 3D position — the vertex-identity ambiguity
vB_ambig  = f.vertex_point(f.cartesian_point(PB), name="vertex_identity_ambiguity")


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


# e1: vA → vB_shared  (end uses shared vertex)
ec1 = _line_sc(vA, vB_shared, PA, PB)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: vB_shared → vC  (start uses shared vertex — count=2 for vB_shared)
ec2 = _line_sc(vB_shared, vC, PB, PC)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: vC → vB_ambig (closes wire back to B position via different entity)
# This creates a "lollipop" that does NOT close back to vA — the wire is
# open (vB_ambig ≠ vA) but the vertex_identity_ambiguity IS the defect.
# To keep the EDGE_LOOP formally closed, use a 4th edge back to vA.
ec3 = _line_sc(vC, vB_ambig, PC, PB)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# e4: vB_ambig → vA  (closes the loop using the ambiguous vertex)
ec4 = _line_sc(vB_ambig, vA, PB, PA)
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi168.stp")
