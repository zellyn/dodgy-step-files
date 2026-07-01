"""A116 — Duplicate PRODUCT.id in multi-body STEP export.

Catalog claim: a STEP AP214 file with two MANIFOLD_SOLID_BREP bodies, each with
its own PRODUCT + PRODUCT_DEFINITION chain, but both PRODUCT entities share
id='Body'. Readers that deduplicate by PRODUCT.id import only one body; readers
that key on entity-instance identity (#NNN) import both correctly.

The cubes are spatially offset: cube1 at origin, cube2 offset +100 in X.

Source: CATIA V5 multi-body STEP export, 3DS community (DEF-X). LGPL-clean:
synthesised from the defect pattern, no upstream bytes copied.

Byte assertions:
  count(b"PRODUCT('Body'") >= 2
  count_entity_def(b'MANIFOLD_SOLID_BREP') >= 2
Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="A116",
    defect=(
        "Duplicate PRODUCT.id='Body' in multi-body STEP: two MANIFOLD_SOLID_BREP "
        "entities (cube1 at origin, cube2 at X+100) each have their own PRODUCT + "
        "PRODUCT_DEFINITION chain but both PRODUCT.id == 'Body'; readers keying "
        "dedup on id string collapse two bodies to one; readers using entity #NNN "
        "import both; CATIA V5 multi-body export DEF-X"
    ),
)

# ── Helper: build a 1×1×1 cube face (planar square) at x-offset ───────────────
def square_face(x_off: float):
    """Return (shell, brep) for a 1×1 square at x=x_off."""
    orig_c = f.cartesian_point((x_off, 0.0, 0.0))
    zd = f.direction((0.0, 0.0, 1.0))
    xd = f.direction((1.0, 0.0, 0.0))
    plc_c = f.axis2_placement_3d(orig_c, zd, xd)
    pln = f.plane(plc_c)
    p0 = f.cartesian_point((x_off + 0.0, 0.0, 0.0))
    p1 = f.cartesian_point((x_off + 1.0, 0.0, 0.0))
    p2 = f.cartesian_point((x_off + 1.0, 1.0, 0.0))
    p3 = f.cartesian_point((x_off + 0.0, 1.0, 0.0))
    v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
    v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
    def le(pa, dv, va, vb):
        d   = f.direction(dv)
        ve  = f.vector(d, 1.0)
        li  = f.line(pa, ve)
        return f.edge_curve(va, vb, li)
    e0 = le(p0, (1.0,  0.0, 0.0), v0, v1)
    e1 = le(p1, (0.0,  1.0, 0.0), v1, v2)
    e2 = le(p2, (-1.0, 0.0, 0.0), v2, v3)
    e3 = le(p3, (0.0, -1.0, 0.0), v3, v0)
    loop = f.edge_loop([
        f.oriented_edge(e0, True), f.oriented_edge(e1, True),
        f.oriented_edge(e2, True), f.oriented_edge(e3, True),
    ])
    fc   = f.advanced_face([f.face_outer_bound(loop)], pln)
    sh   = f.open_shell([fc])
    brep = f._emit_raw(f"MANIFOLD_SOLID_BREP('body',#{sh.eid})")
    return brep

# Build cube1 at origin — registered in the main product chain.
brep1 = square_face(0.0)
f.add_product_chain(brep1, mode="brep_shape", product_id="Body")

# ── Cube2 at X+100 with a SECOND PRODUCT chain (id='Body' — the defect) ────────
# Both products share id='Body'; entity numbers differ (#9001 vs the new IDs).
app_ctx2 = f._emit_raw(
    "APPLICATION_CONTEXT('mechanical design')"
)
prod_ctx2 = f._emit_raw(
    f"PRODUCT_CONTEXT('',#{app_ctx2.eid},'mechanical')"
)
# THE DEFECT: id='Body' duplicates the first product's id.
prod2 = f._emit_raw(
    f"PRODUCT('Body','Body','',(#{prod_ctx2.eid}))"
)
pdf2 = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{prod2.eid})"
)
pdc2 = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx2.eid},'design')"
)
pdef2 = f._emit_raw(
    f"PRODUCT_DEFINITION('','',#{pdf2.eid},#{pdc2.eid})"
)
pds2 = f._emit_raw(
    f"PRODUCT_DEFINITION_SHAPE('','',#{pdef2.eid})"
)

# Cube2 geometry at x_off=100.
brep2 = square_face(100.0)

# Geometry context for cube2.
lu2  = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau2 = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau2 = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc2 = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu2.eid},'distance_accuracy_value','')")
gctx2 = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc2.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu2.eid},#{pau2.eid},#{sau2.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)
sr2 = f._emit_raw(
    f"ADVANCED_BREP_SHAPE_REPRESENTATION('',(#{brep2.eid}),#{gctx2.eid})"
)
f._emit_raw(
    f"SHAPE_DEFINITION_REPRESENTATION(#{pds2.eid},#{sr2.eid})"
)
