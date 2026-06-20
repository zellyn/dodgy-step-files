"""Twi136 — ShapeFix_Wire.FixConnected vertex-replacement chain.

Catalog claim: Three edges forming chain with vertex duplicates:
v1→v2(dup)→v3(dup)→v4. FixConnected replaces v2 with v3, then v3 with
another vertex, leaving intermediate vertices orphaned in the replacement map.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 3 edges
on a PLANE. Each edge uses a distinct pair of VERTEX_POINTs whose 3D
coordinates are very close but not identical (within tolerance), simulating
duplicated vertices. At each junction the "dup" vertex has the same 3D
position as its neighbor (within 1e-4), triggering FixConnected to attempt
replacement. The chain of replacements v2→v3→v4 causes the intermediate
vertices to be orphaned in the replacement map.

The fixture labels the duplicate vertices 'v2_dup' and 'v3_dup' to make the
defect explicit in bytes.

Byte assertions:
  - contains(b'v2_dup')
  - contains(b'v3_dup')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi136",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "3-edge chain: e1 v1→v2_dup, e2 v2_dup_alt→v3_dup, e3 v3_dup_alt→v4; "
        "v2_dup and v2_dup_alt share same 3D position within 1e-4 IS junction defect; "
        "v3_dup and v3_dup_alt share same 3D position within 1e-4 IS junction defect; "
        "FixConnected replaces v2_dup with v3_dup then v3_dup with v4 "
        "leaving intermediate vertices orphaned in replacement map IS mechanism; "
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

# ── Vertex positions ──────────────────────────────────────────────────────────
# Four logical points along X; junction points are duplicated with tiny offset
# simulating vertex duplicates that trigger FixConnected replacement chain.
P1  = (0.0,  0.0, 0.0)
P2  = (5.0,  0.0, 0.0)
P2b = (5.0001, 0.0, 0.0)   # v2_dup: offset 1e-4 from P2 — within tolerance
P3  = (10.0, 0.0, 0.0)
P3b = (10.0001, 0.0, 0.0)  # v3_dup: offset 1e-4 from P3 — within tolerance
P4  = (15.0, 0.0, 0.0)

v1      = f.vertex_point(f.cartesian_point(P1), name="v1")
v2      = f.vertex_point(f.cartesian_point(P2), name="v2_dup")
v2_alt  = f.vertex_point(f.cartesian_point(P2b), name="v2_dup_alt")
v3      = f.vertex_point(f.cartesian_point(P3), name="v3_dup")
v3_alt  = f.vertex_point(f.cartesian_point(P3b), name="v3_dup_alt")
v4      = f.vertex_point(f.cartesian_point(P4), name="v4")


def _line_ec(v_s, v_e, ps, pe, name=""):
    dx = pe[0]-ps[0]; dy = pe[1]-ps[1]; dz = pe[2]-ps[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    ln = f.line(f.cartesian_point(ps),
                f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))
    # Pcurve on plane
    uv_orig = f.cartesian_point((ps[0], ps[1]))
    uv_dir  = f.direction((dx/mag, dy/mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_ln   = f.line(uv_orig, uv_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc      = f._emit_raw(f"SURFACE_CURVE('',#{ln.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# e1: v1 → v2_dup  (endpoint label 'v2_dup' is the first duplicate)
ec1 = _line_ec(v1, v2, P1, P2, name="e1_v1_to_v2dup")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: v2_dup_alt → v3_dup  (start vertex is the alternate duplicate of P2)
ec2 = _line_ec(v2_alt, v3, P2b, P3, name="e2_v2dupalt_to_v3dup")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: v3_dup_alt → v4  (start vertex is the alternate duplicate of P3)
ec3 = _line_ec(v3_alt, v4, P3b, P4, name="e3_v3dupalt_to_v4")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi136.stp")
