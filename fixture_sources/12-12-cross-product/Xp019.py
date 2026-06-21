"""Xp019 — Multiple DATA sections × duplicated entity ID × cross-section reference."""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(catalog_id="Xp019",
             defect='Multiple DATA sections x duplicated entity ID x cross-section reference')

# Build normal geometry for load == "ok" tier-3 assertion
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
f.add_product_chain(sbsm)

# Override render() to add a second DATA section with duplicate #10 and cross-section ref
_orig_render = f.render

def _render_with_multi_data():
    base = _orig_render()
    # Find where ENDSEC comes after DATA
    # Insert a second DATA section before END-ISO-10303-21;
    tail = "ENDSEC;\nEND-ISO-10303-21;\n"
    assert base.endswith(tail), "unexpected render tail"
    head = base[:-len(tail)] + "ENDSEC;\n"
    second_data = (
        "/* xp019 defect: second anonymous DATA section — duplicates #10 and uses @s2 cross-ref */\n"
        "DATA;\n"
        "#10=CARTESIAN_POINT('dup_in_section2',(2.0,0.0,0.0));\n"
        "/* @s2#10 cross-section reference syntax — non-standard in anonymous blocks */\n"
        "#8888=DESCRIPTIVE_REPRESENTATION_ITEM('cross_ref_note','@s2#10');\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )
    return head + second_data

f.render = _render_with_multi_data  # type: ignore[method-assign]
