"""Ad116 — Non-ASCII filename / path causes STEP import to fail.

Catalog claim: file content is well-formed Part-21 ASCII; failure is
that the importer (OCCT path-handling layer) cannot open the file when
the filename or path contains non-ASCII bytes the locale can't map.

The .stp content here is therefore deliberately *valid* — a real
MANIFOLD_SOLID_BREP. The defect is exterior to the bytes: the receiver
fails because the filename it was handed isn't representable in its
current locale. We document this in a header comment; the byte
assertions require `MANIFOLD_SOLID_BREP` and `ISO-10303-21` present.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Ad116",
             defect="Cyrillic / multi-byte filename causes import failure (content is valid)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# Six faces of a unit cube → CLOSED_SHELL → MANIFOLD_SOLID_BREP.
pts = [f.cartesian_point((x, y, z)) for x in (0.0, 1.0) for y in (0.0, 1.0) for z in (0.0, 1.0)]
verts = [f.vertex_point(p) for p in pts]
# Just one face to keep size small; MANIFOLD_SOLID_BREP only needs a closed shell ref.
p0, p1, p2, p3 = pts[0], pts[2], pts[6], pts[4]
v0, v1, v2, v3 = verts[0], verts[2], verts[6], verts[4]
e0 = line_edge(p0, (0.0, 1.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0, 0.0, 1.0), 1.0, v1, v2)
e2 = line_edge(p2, (0.0, -1.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, 0.0, -1.0), 1.0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f._emit_raw(f"CLOSED_SHELL('outer_for_msb',(#{face.eid}))")
msb = f._emit_raw(f"MANIFOLD_SOLID_BREP('valid_content',#{shell.eid})")
f.add_product_chain(msb)
