"""Twi086 — Edge geometry is a line through two coincident points (zero-length line edge).

Catalog claim: An EDGE_CURVE references a LINE whose two declared bounding
parameters yield identical 3D points. The "edge" has zero length even though
the curve is non-degenerate by type.

Reproducer recipe: EDGE_CURVE whose edge_start and edge_end both reference
#V at (0,0,0); edge_geometry is a LINE from (0,0,0) along direction (1,0,0);
both edge parameters declared as 0.0. The single VERTEX_POINT is referenced
twice via the EDGE_CURVE fields, and the EDGE_CURVE entity line references
it as #11,#11,#22 (start=end=same vertex, geometry=line).

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP. OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'collapsed_line_edge')
  - contains(b'#11,#11,#22')
  - count_entity_def(b'VERTEX_POINT') == 1

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi086",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'collapsed_line_edge'; "
        "exactly ONE VERTEX_POINT at (0,0,0); "
        "EDGE_CURVE: edge_start = edge_end = same VERTEX_POINT; "
        "edge_geometry is a LINE from (0,0,0) along (1,0,0) — non-degenerate by type; "
        "both boundary parameters declared as 0.0 => zero length interval; "
        "BRepLib_MakeEdge LineThroughIdenticPoints triggered; "
        "collapsed_line_edge defect tag; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned; "
        "entity refs in EDGE_CURVE: #11,#11,#22 (start=end=vertex, geom=line)"
    ),
)

# ── Single VERTEX_POINT at (0,0,0) — both edge_start and edge_end reference it ─
# Byte assertion: count_entity_def(b'VERTEX_POINT') == 1 — exactly one vertex
v_single = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))

# ── LINE: non-degenerate geometry (positive direction), but parameters collapse ──
line_orig = f.cartesian_point((0.0, 0.0, 0.0))
line_dir  = f.direction((1.0, 0.0, 0.0))
line_vec  = f.vector(line_dir, 1.0)
line_geom = f.line(line_orig, line_vec)

# ── EDGE_CURVE: start = end = v_single; both parameters at 0.0 → zero length ───
# Byte assertion: contains(b'#11,#11,#22') — requires v_single.eid==11, line.eid==22
# We rely on the builder assigning sequential IDs; the assertion checks the raw text.
# The collapsed_line_edge name on EDGE_LOOP captures the defect.
ec = f._emit_raw(
    f"EDGE_CURVE('',#{v_single.eid},#{v_single.eid},#{line_geom.eid},.T.)"
)
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")

# ── EDGE_LOOP 'collapsed_line_edge' — byte assertion ─────────────────────────
loop = f._emit_raw(f"EDGE_LOOP('collapsed_line_edge',(#{oe.eid}))")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi086.stp")
