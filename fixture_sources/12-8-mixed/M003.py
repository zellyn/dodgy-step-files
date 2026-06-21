"""M003 — Free-edge tessellated shell cannot use tessellated_connecting_edge.

Catalog claim: tessellated_connecting_edge requires both face1 and face2 to be set, so it
cannot represent edges on the free boundary of an open shell. Writers either fall back to plain
tessellated_edge (losing connectivity) or, incorrectly, point face2 at an arbitrary face.
Receivers may then think the shell is closed.

Reproducer recipe: Build an open tessellated shell that has a free boundary (e.g., a half-plane
strip). Force the writer to emit tessellated_connecting_edge for the free boundary edge —
pointing face2 at an arbitrary face, making the shell appear closed.

Byte assertions:
  contains(b'TESSELLATED_CONNECTING_EDGE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M003",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing TESSELLATED_SHELL; "
        "open tessellated shell has a free-boundary edge represented by "
        "TESSELLATED_CONNECTING_EDGE with both face1 and face2 set, "
        "incorrectly implying the shell is closed; "
        "AP242 Tessellated Geometry §5.4.2: TESSELLATED_CONNECTING_EDGE requires both "
        "face1 and face2 to be set — it cannot represent a free-boundary edge; "
        "writers on free-boundary edges must use TESSELLATED_EDGE not TESSELLATED_CONNECTING_EDGE; "
        "buggy writer points face2 at an arbitrary face to avoid a null reference, "
        "making receivers think the shell is closed; "
        "kernel must heal: detect free-boundary TESSELLATED_CONNECTING_EDGEs and not infer "
        "a closed shell from their presence; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: tessellated_connecting_edge on free edge, open shell connecting edge invalid, "
        "free-boundary connecting edge has only one face, face2 missing on boundary edge"
    ),
)

# ── Open tessellated shell: two triangles forming a strip with one free edge ──
# Layout:
#   Face A: triangle (P0, P1, P2) — left half
#   Face B: triangle (P1, P3, P2) — right half
# Shared (internal) edge: P1-P2 — valid TESSELLATED_CONNECTING_EDGE
# Free edges: P0-P1, P0-P2, P1-P3, P3-P2 — boundary; P0-P1 is the defect edge

# ── COORDINATES_LIST for face A ───────────────────────────────────────────────
coords_a = f._emit_raw(
    "COORDINATES_LIST('face_a_coords',3,"
    "((0.,0.,0.),(10.,0.,0.),(5.,10.,0.)))"
)
# Face A: one triangle, indices 0-based
face_a = f._emit_raw(
    f"TRIANGULATED_FACE('face_a',#{coords_a.eid},$,"
    "((.FALSE.,.FALSE.,.FALSE.)),((0,1,2)))"
)

# ── COORDINATES_LIST for face B ───────────────────────────────────────────────
coords_b = f._emit_raw(
    "COORDINATES_LIST('face_b_coords',3,"
    "((10.,0.,0.),(20.,0.,0.),(5.,10.,0.)))"
)
# Face B: one triangle (shares P1-P2 edge with face A)
face_b = f._emit_raw(
    f"TRIANGULATED_FACE('face_b',#{coords_b.eid},$,"
    "((.FALSE.,.FALSE.,.FALSE.)),((0,1,2)))"
)

# ── TESSELLATED_SHELL wrapping both faces ─────────────────────────────────────
shell = f._emit_raw(
    f"TESSELLATED_SHELL('open_tess_shell',(#{face_a.eid},#{face_b.eid}))"
)

# ── TESSELLATED_CONNECTING_EDGE on the free boundary — the defect ─────────────
# Free edge P0-P1 (edge 0-1 of face A, which has no neighbour on the other side).
# A conformant writer must use TESSELLATED_EDGE here, not TESSELLATED_CONNECTING_EDGE.
# This buggy writer emits TESSELLATED_CONNECTING_EDGE with face2 pointing at face_b
# (an arbitrary face), incorrectly implying the shell is closed at this edge.
# TESSELLATED_CONNECTING_EDGE(name, face1, edge1_index, face2, edge2_index)
defect_edge = f._emit_raw(
    f"TESSELLATED_CONNECTING_EDGE('free_boundary_edge_WRONG',"
    f"#{face_a.eid},0,#{face_b.eid},2)"
)

# ── Also emit a valid TESSELLATED_EDGE for contrast ──────────────────────────
valid_edge = f._emit_raw(
    f"TESSELLATED_EDGE('internal_edge_ok',#{face_a.eid},2,#{face_b.eid},0)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('free-edge-tess-connecting-edge',"
    f"(#{shell.eid},#{defect_edge.eid},#{valid_edge.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M003.stp")
