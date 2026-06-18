"""M136 — AP203 APPROVED_ITEM points to a product not in the design pool

Catalog claim: "An APPROVAL entity is bound via CC_DESIGN_APPROVAL to a
PRODUCT_DEFINITION whose entity number is not declared in the file."

Demonstration: Create a valid AP203 approval structure with an
APPROVAL entity that references a PRODUCT_DEFINITION via CC_DESIGN_APPROVAL,
but the referenced PRODUCT_DEFINITION entity ID is a DanglingRef (never
defined in the file body).
"""
from step_corpus.step_builder import StepFile, DanglingRef

f = StepFile(catalog_id="M136",
             defect="APPROVAL references dangling PRODUCT_DEFINITION")

# Create a minimal AP203 product structure
# Product with name and ID
product = f._emit_raw("PRODUCT('product_1','','','('UNKNOWN'))")

# Valid PRODUCT_DEFINITION that exists
pd_valid = f._emit_raw(
    "PRODUCT_DEFINITION('','design',#1,.F.)"
)

# APPROVAL entity with name and description
approval = f._emit_raw(
    "APPROVAL('approval_1','Design review approval')"
)

# CC_DESIGN_APPROVAL that links approval to a PRODUCT_DEFINITION
# The second argument (#999) is intentionally a DanglingRef
cc_design_approval = f._emit_raw(
    "CC_DESIGN_APPROVAL(#6,#999)"  # #6 is approval; #999 does not exist
)

# Add minimal geometry to satisfy validator
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

loop = f.closed_polyline_loop([p0, p1, p2, p3])

ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])

f.add_product_chain(sbsm)
