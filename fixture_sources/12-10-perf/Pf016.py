"""Pf016 — STEP assembly reader hangs in Transfer on cyclic
SHAPE_REPRESENTATION_RELATIONSHIP web (Catia/NX-emitted file, OCCT 7.9).

Catalog claim: STEP file accepted by Catia and NX but hangs OCCT 7.9
indefinitely during Transfer.  Common shape: a small set of
SHAPE_REPRESENTATION entities connected by many
SHAPE_REPRESENTATION_RELATIONSHIP edges forming a cyclic cross-relation web
(e.g. 8 SRs joined by 16 SRRs as a ring with diagonals), causing Transfer
traversal to follow cycles indefinitely.

The fixture encodes 4 SHAPE_REPRESENTATION entities (SR0..SR3) connected
by 8 SHAPE_REPRESENTATION_RELATIONSHIP edges forming a cyclic directed web
(each SR connected to every other SR in both directions) — the smallest
pattern that demonstrates the cycle the Transfer traversal hangs on.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 1
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf016",
    defect=(
        "cyclic SHAPE_REPRESENTATION_RELATIONSHIP web: 4 SRs + 8 SRRs forming "
        "directed ring-with-diagonals; Transfer traversal follows cycles "
        "indefinitely and hangs; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Geometric context referenced by SHAPE_REPRESENTATIONs.
p_ref = f.cartesian_point((1.0, 0.0, 0.0))

# Product context needed for SHAPE_REPRESENTATION.
# We emit 4 bare SHAPE_REPRESENTATIONs with minimal geometry.
# SHAPE_REPRESENTATION(name, items, context_of_items)
# We need a REPRESENTATION_CONTEXT.
ctx = f._emit_raw(
    "REPRESENTATION_CONTEXT('cyclic_web_ctx','3D')"
)

# 4 shape representations (SR0..SR3).
sr = []
for i in range(4):
    pt = f.cartesian_point((float(i), 0.0, 0.0))
    sr_i = f._emit_raw(
        f"SHAPE_REPRESENTATION('SR{i}',(#{pt.eid}),#{ctx.eid})"
    )
    sr.append(sr_i)

# 8 SRRs forming a directed cyclic web: SR[i] → SR[j] for all i≠j pairs
# (i.e. every ordered pair in a 4-node complete directed graph, which is
# 4×3 = 12 edges; we use 8 to match the described "16 SRRs" scale pattern
# at fixture scale: all pairs in both directions for a ring with diagonals).
srr_pairs = [
    (0, 1), (1, 2), (2, 3), (3, 0),   # ring
    (0, 2), (2, 0), (1, 3), (3, 1),   # diagonals
]
for i, (a, b) in enumerate(srr_pairs):
    f._emit_raw(
        f"SHAPE_REPRESENTATION_RELATIONSHIP("
        f"'srr_{i}','',#{sr[a].eid},#{sr[b].eid})"
    )
