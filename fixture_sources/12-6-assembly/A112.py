"""A112 — pattern-mined fixture (see catalog for source).

B4 wave-3 issue-tracker mining. LGPL-clean: synthesized from the defect
*pattern*, no upstream bytes copied.

Repair 2026-07-12 (DRIFT audit): the original construction wired all
3 NAUOs as `#9054,#9054` (relating == related == the root
PRODUCT_DEFINITION, a self-loop). STEPControl_Reader treats a product
referenced as NAUO.related as "used" (non-root); the root stopped
being a transferable root and TransferRoots() produced 0 shapes
instead of the claimed shape(1). Fixed to wire 3 *distinct* child
PRODUCT_DEFINITIONs (each with its own placement + MAPPED_ITEM) as
NAUO.related — genuinely 3 separate component instances, each still
labelled 'C1' on the NAUO, which is the actual "same id, different
entity" signature the claim requires. Live-verified shape(1).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A112",
             defect='KiCad#14125 + CadQuery#1962: NAUO name reuse causes dedup-by-name collapse')

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

# Shared leaf-geometry representation (one "capacitor" footprint), reused
# by 3 distinct child PRODUCT_DEFINITIONs -- 3 real components, each wired
# via its own NAUO + REPRESENTATION_MAP + MAPPED_ITEM, but every NAUO
# shares the label 'C1'. Receivers that dedup by NAUO.id (rather than
# entity #N) collapse the three into one.
leaf_sr = f._emit_raw(f"SHAPE_REPRESENTATION('leaf_rep',(#{plc.eid}),#9060)")

for k in range(3):
    sub_pdc = f._emit_raw(f"PRODUCT_CONTEXT('sub{k}',#9000,'mechanical')")
    sub_prod = f._emit_raw(f"PRODUCT('C1','Capacitor {k}','',(#{sub_pdc.eid}))")
    sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
    sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)")
    f._emit_raw(
        f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('C1','same name {k}','',#9054,#{sub_pdef.eid},$)"
    )
    rep_map_k = f._emit_raw(f"REPRESENTATION_MAP(#{plc.eid},#{leaf_sr.eid})")
    inst_orig = f._emit_raw(f"CARTESIAN_POINT('inst{k}_origin',({float(k)*2.0},0.0,0.0))")
    inst_z = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
    inst_x = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
    inst_plc = f._emit_raw(
        f"AXIS2_PLACEMENT_3D('inst{k}_plc',#{inst_orig.eid},#{inst_z.eid},#{inst_x.eid})"
    )
    f._emit_raw(f"MAPPED_ITEM('mi{k}',#{rep_map_k.eid},#{inst_plc.eid})")
