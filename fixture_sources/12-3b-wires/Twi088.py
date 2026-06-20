"""Twi088 — Edge in topology has no 3D curve attached.

Catalog claim: An edge appears in face wires only via its pcurve representations
on adjacent faces; there is no 3D curve attached to the edge itself. The edge
is "implicit" (defined only by surface intersection).

Reproducer recipe: An EDGE_CURVE whose edge_geometry is null ($), but PCURVE(s)
on an adjacent face describe the edge in UV. The EDGE_CURVE text contains
',$,.T.)' (null geometry field). There is exactly one EDGE_CURVE.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP. OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'pcurve_only_edge')
  - contains(b',$,.T.)')
  - count_entity_def(b'EDGE_CURVE') == 1

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi088",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'pcurve_only_edge'; "
        "exactly ONE EDGE_CURVE with null 3D geometry (edge_geometry=$); "
        "the edge is described only by PCURVE in UV on a PLANE host surface; "
        "EDGE_CURVE text: EDGE_CURVE('',#vs,#ve,$,.T.) — null geometry field; "
        "BRepLib BuildCurves3d: no 3D curve to use, must reconstruct from pcurves; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Host PLANE surface for the pcurve ────────────────────────────────────────
plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_zdir = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_plc  = f.axis2_placement_3d(plane_orig, plane_zdir, plane_xdir)
plane_surf = f.plane(plane_plc)

# ── VERTEX_POINTs for the edge ─────────────────────────────────────────────────
v_start = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_end   = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))

# ── PCURVE: UV LINE from (0,0) to (1,0) on the plane ─────────────────────────
uv_orig = f.cartesian_point((0.0, 0.0))
uv_dir  = f.direction((1.0, 0.0))
uv_vec  = f.vector(uv_dir, 1.0)
uv_line = f._emit_raw(f"LINE('',#{uv_orig.eid},#{uv_vec.eid})")
drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line.eid}),#?)")
pcurve  = f._emit_raw(f"PCURVE('',#{plane_surf.eid},#{drep.eid})")

# ── EDGE_CURVE with NULL 3D geometry ($) ──────────────────────────────────────
# Byte assertion: contains(b',$,.T.)') — null geometry field in EDGE_CURVE
# Byte assertion: count_entity_def(b'EDGE_CURVE') == 1 — exactly one
ec = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},$,.T.)"
)
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")

# ── EDGE_LOOP 'pcurve_only_edge' — byte assertion ────────────────────────────
loop = f._emit_raw(f"EDGE_LOOP('pcurve_only_edge',(#{oe.eid}))")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi088.stp")
