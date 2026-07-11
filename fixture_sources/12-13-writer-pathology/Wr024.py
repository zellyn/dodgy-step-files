"""Wr024 — NAUO assembly-tree flattened on re-export.

Catalog claim: hierarchical assembly top → subA → part1, part2 and
top → subB → part3, part4 (two-level NAUO tree) is re-exported as a flat
top → part1, part2, part3, part4 (one-level NAUO tree).

Reproducer recipe: a flat NAUO chain top → part_1, part_2, part_3, part_4
with comment noting the original had two intermediate subassemblies.

Byte assertions:
  count(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 4
  count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 4

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr024",
    defect=(
        "NAUO assembly-tree flattened on re-export; "
        "original hierarchy: top → subassembly_A → part_1, part_2; "
        "top → subassembly_B → part_3, part_4; "
        "re-emitted file flattens to: top → part_1, part_2, part_3, part_4; "
        "subassembly grouping is lost; semantically wrong; "
        "writers whose internal assembly model is flat (one-level) "
        "forced to flatten multi-level assembly trees on export; "
        "expected kernel behavior: preserve NAUO hierarchy depth on round-trip; "
        "if the kernel cannot represent multi-level hierarchies internally, "
        "document the limitation and warn on input; "
        "synonyms: subassembly structure flattened, STEP lost assembly hierarchy, "
        "all parts now siblings"
    ),
)

# Minimal geometry: a single face representing the top assembly shape.
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

# Flat NAUO chain: top (#9054) → part_1, part_2, part_3, part_4
# Comment documents the original two-level hierarchy that was lost.
f._emit_raw(
    "/* DEFECT: original hierarchy had two subassemblies: "
    "top->subassembly_A->{part_1,part_2} and top->subassembly_B->{part_3,part_4}; "
    "writer flattened to one level on re-export */"
)

# Build four leaf part definitions
part_pdc = f._emit_raw(f"PRODUCT_CONTEXT('parts',#9000,'mechanical')")

part1_prod = f._emit_raw(f"PRODUCT('part_1','part_1','',(#{part_pdc.eid}))")
part1_pdf  = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{part1_prod.eid})")
part1_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{part1_pdf.eid},#9053)")

part2_prod = f._emit_raw(f"PRODUCT('part_2','part_2','',(#{part_pdc.eid}))")
part2_pdf  = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{part2_prod.eid})")
part2_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{part2_pdf.eid},#9053)")

part3_prod = f._emit_raw(f"PRODUCT('part_3','part_3','',(#{part_pdc.eid}))")
part3_pdf  = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{part3_prod.eid})")
part3_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{part3_pdf.eid},#9053)")

part4_prod = f._emit_raw(f"PRODUCT('part_4','part_4','',(#{part_pdc.eid}))")
part4_pdf  = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{part4_prod.eid})")
part4_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{part4_pdf.eid},#9053)")

# Four flat NAUOs: top (#9054) → part1..part4 directly (no intermediate subassembly)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','part_1_flat','',"
    f"#9054,#{part1_pdef.eid},$)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('2','part_2_flat','',"
    f"#9054,#{part2_pdef.eid},$)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('3','part_3_flat','',"
    f"#9054,#{part3_pdef.eid},$)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('4','part_4_flat','',"
    f"#9054,#{part4_pdef.eid},$)"
)
