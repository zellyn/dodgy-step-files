"""Wr016 — Re-output of intermediate construction entities (orphan geometry).

Catalog claim: DATA section contains hundreds of CARTESIAN_POINT, LINE,
CIRCLE, and other primitive entities not referenced by any
PRODUCT_DEFINITION_SHAPE chain.  Model is correct but the file is
bloated 3-5× by construction-history scratch geometry.

Reproducer recipe: a minimal valid solid plus 30 unreferenced
CARTESIAN_POINT entities scattered through DATA.

Byte assertions:
  count_entity_def(b'CARTESIAN_POINT') >= 10 or count_entity_def(b'LINE') >= 3 or count_entity_def(b'CIRCLE') >= 3
  count_entity_def(b'CARTESIAN_POINT') >= 5

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr016",
    defect=(
        "Re-output of intermediate construction entities (orphan geometry); "
        "DATA section contains CARTESIAN_POINT, LINE, and CIRCLE entities "
        "not referenced by any PRODUCT_DEFINITION_SHAPE chain; "
        "construction-history scratch geometry is not pruned before export; "
        "model is correct but file is bloated 3-5x by orphan geometry; "
        "common in Pro/E exports of complex parts with sketch history; "
        "writers that emit every kernel-internal entity including scratch geometry; "
        "expected kernel behavior: parse normally; ignore unreferenced entities; "
        "a re-emit pass may normalize/prune; a strict policy emits a warning; "
        "synonyms: STEP file has unreferenced entities, orphan geometry in DATA section, "
        "construction history not pruned, STEP file unnecessarily large"
    ),
)

# Minimal real geometry: a single planar face as the product's shape.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Orphan construction entities — 30 unreferenced CARTESIAN_POINTs scattered
# through the DATA section, simulating Pro/E sketch history residue.
# None of these are referenced by any entity in the product chain.
_orphan_coords = [
    (2.5, 0.0, 0.0), (3.0, 0.5, 0.0), (3.5, 1.0, 0.0),
    (4.0, 0.5, 0.0), (4.5, 0.0, 0.0), (5.0, 1.5, 0.0),
    (1.5, 2.0, 0.0), (2.0, 2.5, 0.0), (2.5, 3.0, 0.0),
    (3.0, 3.5, 0.0), (0.5, 4.0, 0.0), (1.0, 4.5, 0.0),
    (1.5, 5.0, 0.0), (2.0, 0.3, 0.0), (2.5, 0.7, 0.0),
    (3.0, 0.2, 0.0), (0.7, 2.0, 0.0), (1.3, 2.3, 0.0),
    (4.0, 1.5, 0.0), (4.5, 2.0, 0.0), (5.0, 2.5, 0.0),
    (0.3, 3.0, 0.0), (0.8, 3.5, 0.0), (1.2, 4.0, 0.0),
    (3.5, 3.0, 0.0), (4.0, 3.5, 0.0), (4.5, 4.0, 0.0),
    (5.0, 4.5, 0.0), (0.2, 5.0, 0.0), (0.6, 5.5, 0.0),
]
for i, (x, y, z) in enumerate(_orphan_coords):
    f._emit_raw(
        f"CARTESIAN_POINT('scratch_{i}',"
        f"({x:.1f},{y:.1f},{z:.1f}))"
    )

# Orphan LINE entities: direction + vector + line, unreferenced.
_od1 = f._emit_raw("DIRECTION('scratch_d1',(1.0,0.0,0.0))")
_ov1 = f._emit_raw(f"VECTOR(#{_od1.eid},5.0)")
_ol1 = f._emit_raw(
    f"LINE('scratch_ln1',#{f._emit_raw('CARTESIAN_POINT('',(6.,0.,0.))').eid},#{_ov1.eid})"
)
_od2 = f._emit_raw("DIRECTION('scratch_d2',(0.0,1.0,0.0))")
_ov2 = f._emit_raw(f"VECTOR(#{_od2.eid},5.0)")
_ol2 = f._emit_raw(
    f"LINE('scratch_ln2',#{f._emit_raw('CARTESIAN_POINT('',(6.,0.,0.))').eid},#{_ov2.eid})"
)
_od3 = f._emit_raw("DIRECTION('scratch_d3',(0.707,0.707,0.0))")
_ov3 = f._emit_raw(f"VECTOR(#{_od3.eid},3.0)")
_ol3 = f._emit_raw(
    f"LINE('scratch_ln3',#{f._emit_raw('CARTESIAN_POINT('',(7.,0.,0.))').eid},#{_ov3.eid})"
)
