"""A104 — Exception during STEP write with ExternalReferences mode.

Catalog claim: STEP writer in ExternalReferences mode throws when one
assembly branch is empty. contains(b'EXTERNALLY_DEFINED_ITEM'),
contains(b'PRODUCT_DEFINITION'), count_entity_def(b'PRODUCT_DEFINITION') >= 2.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A104",
             defect="EXTERNALLY_DEFINED_ITEM + 2 PRODUCT_DEFINITION — writer throws in ExternalReferences mode when one assembly branch is empty")

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

# Second PRODUCT_DEFINITION — the empty branch that causes the writer to throw.
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('ext_sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('BranchB','BranchB','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','empty_branch',#{sub_pdf.eid},#9003)")

# NAUO linking root to empty branch.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','empty_branch','',#9004,#{sub_pdef.eid},$)"
)

# EXTERNALLY_DEFINED_ITEM: the multi-file reference that triggered the crash.
# In ExternalReferences mode, the writer emits external document references
# for each peer part. The empty branch (sub_pdef) has no saved peer file.
ext_src = f._emit_raw("EXTERNAL_SOURCE('','peer_parts/')")
f._emit_raw(
    f"EXTERNALLY_DEFINED_ITEM('BranchB_extern',#{ext_src.eid})"
)

# STYLED_ITEM scaffolding for assembly-presence lint.
colour = f._emit_raw("COLOUR_RGB('face_color',0.5,0.5,0.5)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('face_style',(#{psa.eid}),#{face.eid})")
