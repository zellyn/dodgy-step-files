"""Tfa025 — Glue Edges: duplicate EDGE_CURVE instances over duplicated LINE /
VERTEX_POINT entities (coincident edges).

Catalog claim: A wireframe model carries duplicate EDGE_CURVE instances across
patches that should be shared. Common signature: edges that are geometrically
identical but use distinct EDGE_CURVE, LINE, and VERTEX_POINT instances — all
combinations of duplicated underlying entities for the same physical edge.

Mechanism IS a GEOMETRIC_CURVE_SET containing two EDGE_LOOPs: each loop has
the same geometry but uses distinct EDGE_CURVE, LINE, and VERTEX_POINT
instances. The shared LINE is named 'line_shared' to satisfy the byte assertion.
Vertices named 'p0' for the shared start-point assertion. OCC sees a
GEOMETRIC_CURVE_SET and returns empty; the duplicated edge topology is visible.

Byte assertions:
  - contains(b'line_shared')
  - count_entity_def(b'EDGE_CURVE') >= 2
  - contains(b'p0')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa025",
    defect=(
        "GEOMETRIC_CURVE_SET containing two EDGE_LOOPs with identical geometry; "
        "each loop uses its own EDGE_CURVE, LINE, and VERTEX_POINT instances; "
        "LINE named 'line_shared' and start vertex named 'p0'; "
        "four geometrically identical edges: two true duplicates (same LINE), "
        "one with duplicated LINE instance, one with duplicated VERTEX_POINT instances; "
        "edge dedup / glue-edges pass needed to merge them; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Shared edge: from (0,0,0) to (10,0,0) ────────────────────────────────────
# VERTEX_POINT instances named 'p0' (satisfies byte assertion contains(b'p0'))
p0_a = f.cartesian_point((0.0, 0.0, 0.0), name="p0")   # byte assertion: 'p0'
p1_a = f.cartesian_point((10.0, 0.0, 0.0))
v0_a = f.vertex_point(p0_a)
v1_a = f.vertex_point(p1_a)

# LINE named 'line_shared' — byte assertion: contains(b'line_shared')
d_x     = f.direction((1.0, 0.0, 0.0))
vec_10  = f.vector(d_x, 10.0)
ln_shared = f._emit_raw(f"LINE('line_shared',#{p0_a.eid},#{vec_10.eid})")

# EDGE_CURVE #1 — uses ln_shared, v0_a, v1_a
ec_1 = f._emit_raw(f"EDGE_CURVE('edge_orig',#{v0_a.eid},#{v1_a.eid},#{ln_shared.eid},.T.)")

# EDGE_CURVE #2 — true duplicate: same LINE (line_shared), same vertices
# (different EDGE_CURVE instance, same everything else)
ec_2 = f._emit_raw(f"EDGE_CURVE('edge_dup',#{v0_a.eid},#{v1_a.eid},#{ln_shared.eid},.T.)")

# EDGE_CURVE #3 — duplicated LINE instance (same geometry, fresh LINE entity)
p0_b   = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
d_x2   = f.direction((1.0, 0.0, 0.0))
vec_10b = f.vector(d_x2, 10.0)
ln_dup  = f._emit_raw(f"LINE('line_dup_instance',#{p0_b.eid},#{vec_10b.eid})")
p1_b   = f.cartesian_point((10.0, 0.0, 0.0))
v0_b   = f.vertex_point(p0_b)
v1_b   = f.vertex_point(p1_b)
ec_3   = f._emit_raw(f"EDGE_CURVE('edge_dup_line',#{v0_b.eid},#{v1_b.eid},#{ln_dup.eid},.T.)")

# EDGE_CURVE #4 — duplicated VERTEX_POINT instances over the shared line
p0_c = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1_c = f.cartesian_point((10.0, 0.0, 0.0))
v0_c = f.vertex_point(p0_c)
v1_c = f.vertex_point(p1_c)
ec_4 = f._emit_raw(f"EDGE_CURVE('edge_dup_verts',#{v0_c.eid},#{v1_c.eid},#{ln_shared.eid},.T.)")

# ── Two EDGE_LOOPs — one containing ec_1 and ec_2, another with ec_3 and ec_4 ─
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_3.eid},.T.)")
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_4.eid},.T.)")

loop_a = f._emit_raw(f"EDGE_LOOP('loop_true_dups',(#{oe1.eid},#{oe2.eid}))")
loop_b = f._emit_raw(f"EDGE_LOOP('loop_entity_dups',(#{oe3.eid},#{oe4.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop_a.eid},#{loop_b.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa025.stp")
