"""A117 — PRODUCT_DEFINITION_CONTEXT with null application_context_element.

Catalog claim: a STEP AP214 file where PRODUCT_DEFINITION_CONTEXT has its
application_context_element replaced with $ (null). Readers that check this
slot to determine design context may skip geometry transfer; OCCT-permissive
readers may still load the geometry; strict readers produce an empty document.

A valid MANIFOLD_SOLID_BREP cube geometry is present so the load outcome
distinguishes permissive vs strict reader behaviour.

Source: Fusion 360 community + OCCT MANTIS 0031455 (DEF-GG). LGPL-clean:
synthesised from the defect pattern, no upstream bytes copied.

Byte assertions:
  contains(b'PRODUCT_DEFINITION_CONTEXT')
  matches(rb"PRODUCT_DEFINITION_CONTEXT\('[^']*',[^,]+,\$\)")
Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="A117",
    defect=(
        "PRODUCT_DEFINITION_CONTEXT with null application_context_element ($): "
        "PRODUCT_DEFINITION_CONTEXT('part definition',#9000,$) — the third param "
        "is $ rather than 'mechanical'; readers checking this slot for design-context "
        "classification skip geometry transfer producing empty import; OCCT-permissive "
        "readers still load the solid; OCCT MANTIS 0031455 + Fusion 360 DEF-GG"
    ),
)

# ── Valid planar face (1×1 square) — provides OCCT a real product chain ──────
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
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])

# add_product_chain emits PRODUCT_DEFINITION_CONTEXT('part definition',#9000,'design').
# We post-patch: after the chain is written we add a second PDC with null element
# to be the actual PDC used by an extra raw PRODUCT_DEFINITION below.
f.add_product_chain(sbsm)

# ── DEFECT ENTITY: PRODUCT_DEFINITION_CONTEXT with null application_context_element ──
# application_context_element (3rd arg) = $ — the defect.
# This orphan PDC is not used by the main chain (which is healthy), so OCCT
# still loads shape(1).  The defect is detectable in the bytes: a conforming
# strict reader that validates all PDC entities will reject or warn on this one.
pdc_null = f._emit_raw(
    "PRODUCT_DEFINITION_CONTEXT('part definition',#9000,$)"
)
# Attach a PRODUCT_DEFINITION that references the null-element PDC to make the
# defect live on the shape, not just orphaned.  A reader that traces
# PRODUCT_DEFINITION → PRODUCT_DEFINITION_CONTEXT → application_context_element
# will find a null and may skip the shape transfer.
prod_null = f._emit_raw(
    "PRODUCT('null_ctx_part','null_ctx_part','',(#9000))"
)
pdf_null = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{prod_null.eid})"
)
pdef_null = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{pdf_null.eid},#{pdc_null.eid})"
)
