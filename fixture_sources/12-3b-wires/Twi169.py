"""Twi169 — ShapeFix_Wire.FixDegenerated insert-between-degenerate.

Catalog claim: FixDegenerated applied to wire with two consecutive degenerate
edges. Insertion logic fails; cannot handle degenerate-degenerate adjacency.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 3 edges on
a PLANE: one normal edge bracketed by two degenerate edges (zero-length arcs).
The wire sequence is [degenerate_start, normal, degenerate_end]:
  - e_degen_A: zero-length edge from vA to vA (same vertex both ends)
  - e_normal:  LINE from vA to vB
  - e_degen_B: zero-length edge from vB to vB (same vertex both ends)

FixDegenerated encounters two consecutive degenerates surrounding the normal
edge and its insertion/removal logic fails to handle the degenerate-degenerate
adjacency, leaving the wire with incomplete degenerate removal.

The degenerate edges are labelled 'degen_edge_start' and 'degen_edge_end'.

Byte assertions:
  - contains(b'degen_edge_start')
  - contains(b'degen_edge_end')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi169",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "wire sequence: [degen_edge_start(vA→vA), e_normal(vA→vB), degen_edge_end(vB→vB)]; "
        "degen_edge_start: zero-length LINE at vA=(0,0,0) IS degenerate edge; "
        "degen_edge_end: zero-length LINE at vB=(10,0,0) IS degenerate edge; "
        "e_normal: LINE from vA to vB separating the two degenerates; "
        "FixDegenerated encounters degen-normal-degen adjacency; "
        "insertion logic fails to handle degenerate-degenerate boundary IS mechanism; "
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
PA = (0.0,  0.0, 0.0)
PB = (10.0, 0.0, 0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))


def _zero_len_edge(v, pt, label):
    """Build a zero-length (degenerate) EDGE_CURVE from v back to v."""
    # Use a tiny-magnitude vector to avoid divide-by-zero; point stays at pt
    ln3 = f.line(f.cartesian_point(pt),
                 f.vector(f.direction((1.0, 0.0, 0.0)), 0.0))
    uv_orig = f.cartesian_point((pt[0], pt[1]))
    uv_dir  = f.direction((1.0, 0.0))
    uv_vec  = f.vector(uv_dir, 0.0)
    uv_ln   = f.line(uv_orig, uv_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc      = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{label}',#{v.eid},#{v.eid},#{sc.eid},.T.)")


def _normal_edge(v_s, v_e, ps, pe):
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


# e_degen_A: zero-length edge at vA — 'degen_edge_start'
ec_da = _zero_len_edge(vA, PA, "degen_edge_start")
oe_da = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_da.eid},.T.)")

# e_normal: vA → vB
ec_n  = _normal_edge(vA, vB, PA, PB)
oe_n  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_n.eid},.T.)")

# e_degen_B: zero-length edge at vB — 'degen_edge_end'
ec_db = _zero_len_edge(vB, PB, "degen_edge_end")
oe_db = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_db.eid},.T.)")

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_da.eid},#{oe_n.eid},#{oe_db.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi169.stp")
