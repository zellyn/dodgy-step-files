"""A080 — Hierarchy & colours lost on partial-document IGES/STEP write.

Catalog claim: writing only a subset of an XCAF document flattens the
assembly tree and drops per-branch colours.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: nested
hierarchy (Root → Branch → Leaf) with per-branch STYLED_ITEM colors
attached to NAUO references.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A080",
             defect="nested NAUO + per-branch STYLED_ITEM (partial-write target)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
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

# Build Branch and Leaf PRODUCTs.
branch_pdc = f._emit_raw(f"PRODUCT_CONTEXT('branch',#9000,'mechanical')")
branch_prod = f._emit_raw(f"PRODUCT('Branch','Branch','',(#{branch_pdc.eid}))")
branch_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{branch_prod.eid})")
branch_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{branch_pdf.eid},#9003)"
)
# Root → Branch NAUO.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','RootBranch','',"
    f"#9004,#{branch_pdef.eid},$)"
)

leaf_prod = f._emit_raw(f"PRODUCT('Leaf','Leaf','',(#{branch_pdc.eid}))")
leaf_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{leaf_prod.eid})")
leaf_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{leaf_pdf.eid},#9003)"
)
# Branch → Leaf NAUO.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('2','BranchLeaf','',"
    f"#{branch_pdef.eid},#{leaf_pdef.eid},$)"
)

# Per-branch STYLED_ITEM — a color attached to the face (the per-branch
# attribution the catalog claims gets lost on partial write).
colour = f._emit_raw("COLOUR_RGB('branch_color',0.7,0.5,0.2)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('branch_styling',(#{psa.eid}),#{face.eid})")

# Second STYLED_ITEM + COLOUR_RGB for the Leaf branch (the catalog
# claim is about per-branch colours, plural).
colour2 = f._emit_raw("COLOUR_RGB('leaf_color',0.2,0.5,0.7)")
fasc2 = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour2.eid})")
fas2 = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc2.eid}))")
ssfa2 = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas2.eid})")
sss2 = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa2.eid}))")
ssu2 = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss2.eid})")
psa2 = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu2.eid}))")
f._emit_raw(f"STYLED_ITEM('leaf_styling',(#{psa2.eid}),#{face.eid})")
