"""Tsh067 — Inner void shell extends beyond outer shell extent (void poking through).

Catalog claim: BREP_WITH_VOIDS expresses a solid with internal cavities: an outer
CLOSED_SHELL plus one or more inner CLOSED_SHELLs (the voids). A producer that
boolean-subtracts a long pin-shaped tool whose extent exceeds the host part, and emits
the result as BREP_WITH_VOIDS without trimming the tool's shell, leaves a void shell
whose extent pokes through one face of the outer shell.

Mechanism IS the shell structure: outer CLOSED_SHELL is a 10x10x10 mm cube (Z = 0..10).
Inner CLOSED_SHELL is a 2x2x15 mm pin centred at (5,5,0), extending Z = -2.5..12.5,
which pokes 2.5 mm below Z=0 and 2.5 mm above Z=10. The pin IS directly wired into a
BREP_WITH_VOIDS entity as the void shell via ORIENTED_CLOSED_SHELL. The violation — void
shell extent exceeds outer shell along Z — IS directly encoded in the shell topology (outer
cube faces at Z=0 and Z=10 do not bound the pin).

Byte assertions:
  - contains(b'BREP_WITH_VOIDS')
  - contains(b'ORIENTED_CLOSED_SHELL')
  - count_entity_def(b'CLOSED_SHELL') == 2

Tier-3 assertion: shape_null == True

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh067",
    defect=(
        "BREP_WITH_VOIDS with outer CLOSED_SHELL (10x10x10 cube, Z=0..10) and "
        "inner void CLOSED_SHELL (2x2x15 pin, Z=-2.5..12.5); "
        "pin void IS directly wired into BREP_WITH_VOIDS via ORIENTED_CLOSED_SHELL; "
        "pin protrudes 2.5 mm below Z=0 and 2.5 mm above Z=10 IS the violation; "
        "outer cube faces at Z=0 and Z=10 do not bound the pin shell; "
        "fix: validate that each void shell is geometrically contained inside the outer shell; "
        "reject when measurable protrusion detected; heal by trimming void to outer boundary"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz, length=1.0):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, length)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def make_quad_face(p0, p1, p2, p3, plane):
    v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
    v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
    e0 = led(v0, v1, p0, 1, 0, 0)
    e1 = led(v1, v2, p1, 0, 1, 0)
    e2 = led(v2, v3, p2,-1, 0, 0)
    e3 = led(v3, v0, p3, 0,-1, 0)
    lp = f.edge_loop([f.oriented_edge(e0,True), f.oriented_edge(e1,True),
                      f.oriented_edge(e2,True), f.oriented_edge(e3,True)])
    return f.advanced_face([f.face_outer_bound(lp)], plane)

def make_plane(ox, oy, oz, nx, ny, nz, rx, ry, rz):
    plc = f.axis2_placement_3d(cp(ox,oy,oz), dir3(nx,ny,nz), dir3(rx,ry,rz))
    return f.plane(plc)

# ── Outer cube: 10x10x10, corners (0,0,0)-(10,10,10) ─────────────────────────
pl_out_z0 = make_plane(0,0,0,  0,0,-1,  1,0,0)
pl_out_z1 = make_plane(0,0,10, 0,0, 1,  1,0,0)
pl_out_x0 = make_plane(0,0,0, -1,0, 0,  0,1,0)
pl_out_x1 = make_plane(10,0,0, 1,0, 0,  0,1,0)
pl_out_y0 = make_plane(0,0,0,  0,-1,0,  1,0,0)
pl_out_y1 = make_plane(0,10,0, 0, 1,0,  1,0,0)

outer_z0 = make_quad_face(cp(0,0,0),  cp(10,0,0), cp(10,10,0),  cp(0,10,0),  pl_out_z0)
outer_z1 = make_quad_face(cp(0,0,10), cp(0,10,10),cp(10,10,10), cp(10,0,10), pl_out_z1)
outer_x0 = make_quad_face(cp(0,0,0),  cp(0,10,0), cp(0,10,10),  cp(0,0,10),  pl_out_x0)
outer_x1 = make_quad_face(cp(10,0,0), cp(10,0,10),cp(10,10,10), cp(10,10,0), pl_out_x1)
outer_y0 = make_quad_face(cp(0,0,0),  cp(0,0,10), cp(10,0,10),  cp(10,0,0),  pl_out_y0)
outer_y1 = make_quad_face(cp(0,10,0), cp(10,10,0),cp(10,10,10), cp(0,10,10), pl_out_y1)

outer_shell = f.closed_shell([outer_z0, outer_z1, outer_x0, outer_x1, outer_y0, outer_y1])

# ── Inner void: 2x2x15 pin centred at (5,5), Z = -2.5..12.5 (POKES THROUGH) ─
# Pin corners: (4,4,-2.5) to (6,6,12.5)
pl_in_z0 = make_plane(4,4,-2.5, 0,0,-1,  1,0,0)
pl_in_z1 = make_plane(4,4,12.5, 0,0, 1,  1,0,0)
pl_in_x0 = make_plane(4,4,-2.5,-1,0, 0,  0,1,0)
pl_in_x1 = make_plane(6,4,-2.5, 1,0, 0,  0,1,0)
pl_in_y0 = make_plane(4,4,-2.5, 0,-1,0,  1,0,0)
pl_in_y1 = make_plane(4,6,-2.5, 0, 1,0,  1,0,0)

pin_z0 = make_quad_face(cp(4,4,-2.5), cp(6,4,-2.5), cp(6,6,-2.5), cp(4,6,-2.5), pl_in_z0)
pin_z1 = make_quad_face(cp(4,4,12.5), cp(4,6,12.5), cp(6,6,12.5), cp(6,4,12.5), pl_in_z1)
pin_x0 = make_quad_face(cp(4,4,-2.5), cp(4,6,-2.5), cp(4,6,12.5), cp(4,4,12.5), pl_in_x0)
pin_x1 = make_quad_face(cp(6,4,-2.5), cp(6,4,12.5), cp(6,6,12.5), cp(6,6,-2.5), pl_in_x1)
pin_y0 = make_quad_face(cp(4,4,-2.5), cp(4,4,12.5), cp(6,4,12.5), cp(6,4,-2.5), pl_in_y0)
pin_y1 = make_quad_face(cp(4,6,-2.5), cp(6,6,-2.5), cp(6,6,12.5), cp(4,6,12.5), pl_in_y1)

inner_shell = f.closed_shell([pin_z0, pin_z1, pin_x0, pin_x1, pin_y0, pin_y1])

# ORIENTED_CLOSED_SHELL wrapping inner (void shell normal points inward for voids)
oriented_inner = f._emit_raw(
    f"ORIENTED_CLOSED_SHELL('void_pin',*,#{inner_shell.eid},.T.)"
)

# BREP_WITH_VOIDS: outer_shell + oriented void — IS the mechanism
f._emit_raw(
    f"BREP_WITH_VOIDS('outer_with_protruding_void',"
    f"#{outer_shell.eid},"
    f"(#{oriented_inner.eid}))"
)

# Product chain via surface shape
sbsm = f.shell_based_surface_model([outer_shell, inner_shell])
f.add_product_chain(sbsm)
