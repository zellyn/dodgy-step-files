"""A115 — CATIA V5 PRODUCT_CATEGORY_RELATIONSHIP across AP214→AP242 schema boundary.

Catalog claim: a STEP AP214 file with a PRODUCT_CATEGORY_RELATIONSHIP linking
the product to a PRODUCT_CATEGORY named "raw_material/AL6061" with name
"material_category". AP214-capable readers (OCCT, HOOPS) expose this as a
product attribute; AP242-only readers that use a different GENERAL_PROPERTY
path silently drop it. The geometry (minimal cube face) loads under all readers.

Source: 3DS community CATIA V5 migration forum (DEF-W). LGPL-clean: synthesised
from the defect pattern, no upstream bytes copied.

Byte assertions:
  contains(b'PRODUCT_CATEGORY_RELATIONSHIP')
  contains(b'PRODUCT_CATEGORY')
  contains(b'raw_material/AL6061')
Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="A115",
    defect=(
        "CATIA V5 PRODUCT_CATEGORY_RELATIONSHIP linking PRODUCT to "
        "PRODUCT_CATEGORY('raw_material/AL6061') with name 'material_category'; "
        "AP214-capable readers expose the category as a product attribute; "
        "AP242-only readers silently drop it (different GENERAL_PROPERTY path); "
        "3DS CATIA migration forum DEF-W; geometry loads under all readers"
    ),
)

# ── Valid planar face (1×1 square) providing OCCT a real product chain ─────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d   = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln  = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, (1.0,  0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0,  1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])

# add_product_chain allocates IDs as follows (see StepFile._emit reserved-high logic):
#   APPLICATION_CONTEXT → 9000  (inserted directly)
#   PRODUCT_CONTEXT     → 9050  (_emit skips from 9000 to reserved_high+50=9050)
#   PRODUCT             → 9051  (next after 9050)
# We call add_product_chain and save the PRODUCT entity ID for the relationship below.
sdr = f.add_product_chain(sbsm)
# Walk entities list to find the PRODUCT entity (type_name == "PRODUCT").
_prod_ent = next(e for e in f.entities if e.type_name == "PRODUCT")

# ── PRODUCT_CATEGORY_RELATIONSHIP — the AP214→AP242 schema-boundary defect ─────
# AP214 §4.7 entity chain:
#   PRODUCT_CATEGORY identifies the material class.
#   PRODUCT_CATEGORY_RELATIONSHIP links it to the product definition.
# AP242 readers expect GENERAL_PROPERTY for category data and ignore this chain.
prod_cat = f._emit_raw(
    "PRODUCT_CATEGORY('raw_material/AL6061','aluminium alloy 6061 stock material')"
)
# The relationship links the main PRODUCT to this category.
# name='material_category' is the CATIA V5 conventional name for material links.
f._emit_raw(
    f"PRODUCT_CATEGORY_RELATIONSHIP('material_category','',#{prod_cat.eid},#{_prod_ent.eid})"
)
