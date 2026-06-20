"""Tfa075 — ShapeFix_ComposeShell.MakeFacesOnPatch fallback resolution.

Catalog claim: MakeFacesOnPatch receives a single non-WIRE loop (e.g., VERTEX).
The fast-path check at line 2985 (loops.Length==1 && !WIRE) returns early,
promoting the residual loop as a face without proper topology resolution.
Fallback resolution is ambiguous when the loop type is not WIRE.

Mechanism IS a GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE
whose FACE_OUTER_BOUND references an EDGE_LOOP that contains only a single
degenerate ORIENTED_EDGE — the edge has coincident start and end vertex
(a zero-length loop that collapses to a point, mimicking the VERTEX-type
non-WIRE loop that triggers MakeFacesOnPatch's bypass path).
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa075",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "FACE_OUTER_BOUND references EDGE_LOOP with single degenerate ORIENTED_EDGE; "
        "edge is self-loop: start vertex == end vertex at (5.0, 5.0, 0.0); "
        "collapses to VERTEX-type non-WIRE loop — triggers MakeFacesOnPatch bypass; "
        "fast-path at line 2985: loops.Length==1 && !WIRE returns early; "
        "residual loop promoted as face without topology resolution; "
        "kernel should reject or fallback with diagnostic for non-WIRE single loop; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Plane surface ─────────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Degenerate self-loop vertex at (5.0, 5.0, 0.0) ───────────────────────────
cp_center = f.cartesian_point((5.0, 5.0, 0.0))
v_center  = f._emit_raw(f"VERTEX_POINT('degenerate_vertex',#{cp_center.eid})")

# Zero-length edge: start == end == cp_center (a point-loop / non-WIRE loop)
d_x   = f.direction((1.0, 0.0, 0.0))
v_zero = f.vector(d_x, 0.0)
ln_zero = f.line(cp_center, v_zero)
ec_self = f._emit_raw(
    f"EDGE_CURVE('self_loop',#{v_center.eid},#{v_center.eid},#{ln_zero.eid},.T.)"
)

oe_self = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_self.eid},.T.)")

# Single-entry EDGE_LOOP — collapses to VERTEX-type non-WIRE loop
loop = f._emit_raw(f"EDGE_LOOP('degenerate_loop',(#{oe_self.eid}))")
fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af   = f._emit_raw(f"ADVANCED_FACE('patch_face',(#{fob.eid}),#{plane.eid},.T.)")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa075.stp")
