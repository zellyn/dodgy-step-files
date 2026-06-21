"""Xp043 — CATIA AP242 → Inventor: top-level PRODUCT_DEFINITION without SDR."""
from step_corpus.step_builder import StepFile

# Defect: top-level PRODUCT_DEFINITION exists but no SHAPE_DEFINITION_REPRESENTATION
# binds it to a SHAPE_REPRESENTATION. Child PRODUCT has its own SDR.
# Some receivers infer the missing top-level binding from the child graph;
# Inventor treats it as structurally invalid and aborts the entire import.

f = StepFile(catalog_id="Xp043",
             defect='Top-level PRODUCT_DEFINITION without SDR: Inventor aborts, FreeCAD/Onshape infer')

# Build the child's geometry
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, p1, v0, v1)
e1 = line_edge(p1, p2, v1, v2)
e2 = line_edge(p2, p3, v2, v3)
e3 = line_edge(p3, p0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])

# Build the normal product chain (this will become the CHILD product)
f.add_product_chain(sbsm)
# The product chain is now at IDs 9000+; #9003 = PRODUCT_DEFINITION for the child

# Now add a TOP-LEVEL PRODUCT_DEFINITION without any SHAPE_DEFINITION_REPRESENTATION
# Defect: no SDR references top_prod_def
app_ctx_ref = "#9000"  # APPLICATION_CONTEXT from the product chain

top_prod_ctx = f._emit_raw(
    f"PRODUCT_CONTEXT('',{app_ctx_ref},'mechanical')"
)
top_prod = f._emit_raw(
    f"PRODUCT('top_assembly','Top Assembly (no SDR)','',({top_prod_ctx.ref()}))"
)
top_prod_def_form = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',{top_prod.ref()})"
)
top_prod_def_ctx = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',{app_ctx_ref},'design')"
)
top_prod_def = f._emit_raw(
    f"PRODUCT_DEFINITION('','',{top_prod_def_form.ref()},{top_prod_def_ctx.ref()})"
)
top_pds = f._emit_raw(
    f"PRODUCT_DEFINITION_SHAPE('','',{top_prod_def.ref()})"
)

# Link child to top via NEXT_ASSEMBLY_USAGE_OCCURRENCE
nauo = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('child_nauo','','',{top_prod_def.ref()},#9003,$)"
)

# NOTE: No SHAPE_DEFINITION_REPRESENTATION for top_prod_def
# This is the defect: top-level PRODUCT_DEFINITION has no SDR
f._emit_raw(
    f"/* xp043 defect: {top_prod_def.ref()} (top-level) has no SHAPE_DEFINITION_REPRESENTATION; "
    f"Inventor aborts import; FreeCAD/Onshape infer from child #{nauo.eid} */"
)
