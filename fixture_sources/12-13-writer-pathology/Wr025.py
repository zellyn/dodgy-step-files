"""Wr025 — NAUO chain re-rooted incorrectly (component becomes top).

Catalog claim: the input was rooted on 'plate' with 'screw' as a
component; re-export swapped the root so 'screw' is now the top product
and 'plate' is a child.

Reproducer recipe: a NAUO chain rooted on 'screw' with 'plate' as a
component, when comment notes input was rooted on 'plate'.

Byte assertions:
  contains(b'screw->plate')
  contains(b"'screw") or contains(b"'plate")

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr025",
    defect=(
        "NAUO chain re-rooted incorrectly (component becomes top); "
        "input had 'plate' as assembly root with 'screw' as component; "
        "re-export emitted 'screw' as root with 'plate' as child; "
        "semantic owner of the assembly is changed; "
        "writers whose internal assembly representation does not distinguish "
        "top product from subcomponent and emit first-encountered product as top; "
        "expected kernel behavior: preserve input's choice of assembly root; "
        "document a tie-break rule when the input has multiple unconnected products; "
        "synonyms: wrong root product after re-export, STEP swapped which part is top, "
        "assembly root re-rooted"
    ),
)

# Minimal geometry: a single face as product shape.
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
# add_product_chain emits the 'Wr025' product as the top; we then also
# emit 'screw' as a second root product with 'plate' as its component
# to demonstrate screw->plate mis-rooting.
f.add_product_chain(sbsm)

# DEFECT: writer re-rooted the assembly.
# Original input was: plate (root) -> screw (component)
# Re-exported as:     screw (root) -> plate (component)
f._emit_raw(
    "/* DEFECT: original root was 'plate'; writer emitted 'screw' as new root; "
    "screw->plate relationship inverted from input — screw->plate */"
)

pdc_extra = f._emit_raw(f"PRODUCT_CONTEXT('',#9000,'mechanical')")

# 'screw' is incorrectly emitted as the top product
screw_prod = f._emit_raw(f"PRODUCT('screw','screw','',(#{pdc_extra.eid}))")
screw_pdf  = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{screw_prod.eid})")
screw_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{screw_pdf.eid},#9053)")

# 'plate' is incorrectly emitted as a component
plate_prod = f._emit_raw(f"PRODUCT('plate','plate','',(#{pdc_extra.eid}))")
plate_pdf  = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{plate_prod.eid})")
plate_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{plate_pdf.eid},#9053)")

# NAUO: screw -> plate (wrong direction; input had plate -> screw)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','screw->plate','',"
    f"#{screw_pdef.eid},#{plate_pdef.eid},$)"
)
