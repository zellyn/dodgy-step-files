"""Tsh209 — U-closed seam-edge period wrapping.

Catalog claim: Shell with U-closed surface (cylindrical) and seam edge crossing
parametric boundary (U=0→2π). Orientation propagation fails to detect period
wraparound, causing undefined seam edge orientation.

Mechanism IS the shell structure: AN OPEN_SHELL containing ONE ADVANCED_FACE
on a CYLINDRICAL_SURFACE (radius=1, height=1) with a SEAM EDGE (circle arc at
U=0≡2π) IS the defect trigger. The seam edge IS an EDGE_CURVE whose start and
end vertex IS the same point (both on the seam line at U=0), and whose curve IS
a full CIRCLE — IS the parametric period crossing. OrientedShells IS the defect
path: orientation propagation reaches the seam edge and cannot determine
direction because U=0 and U=2π are the same position — IS the period-wraparound
ambiguity — IS the defect.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Tsh209",
    defect=(
        "OPEN_SHELL with ONE ADVANCED_FACE on CYLINDRICAL_SURFACE with SEAM EDGE IS the U-closed period-wrapping defect trigger; "
        "cylindrical surface has radius=1 and axis along Z — IS the U-closed surface (U∈[0,2π]); "
        "seam edge IS EDGE_CURVE referencing a full CIRCLE at the bottom rim (Z=0) — IS the period-crossing seam; "
        "seam edge start vertex and end vertex ARE THE SAME POINT at (1,0,0) on the seam line (U=0≡2π) — IS the wraparound; "
        "top rim IS a second full CIRCLE at Z=1 — IS the top seam edge; "
        "two vertical line edges at U=0 close the face boundary — IS the seam line edges; "
        "FACE_OUTER_BOUND loop: bottom-seam → right-vertical → top-seam-reversed → left-vertical-reversed — IS the loop; "
        "OrientedShells IS the defect path: orientation propagation reaches seam edge at U=0≡2π; "
        "period wraparound IS not detected — IS the ambiguity; "
        "seam edge orientation IS undefined — IS the defect outcome; "
        "fix: OrientedShells must detect U-period seam edges and apply modular orientation; "
        "emit E_SEAM_PERIOD_WRAPAROUND when seam edge start==end on U-closed surface"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))

R = 1.0   # cylinder radius
H = 1.0   # cylinder height

# Seam line vertices at U=0 (x=R, y=0): bottom and top — IS the seam endpoints
p_bot = cp(R, 0, 0);  v_bot = f.vertex_point(p_bot)   # bottom seam point (U=0, Z=0)
p_top = cp(R, 0, H);  v_top = f.vertex_point(p_top)   # top seam point (U=0, Z=H)

# Cylinder axis placement: origin at (0,0,0), axis=+Z, ref=+X
cyl_origin = cp(0, 0, 0)
cyl_ax = f.axis2_placement_3d(cyl_origin, dir3(0, 0, 1), dir3(1, 0, 0))
cyl = f.cylindrical_surface(cyl_ax, R)

# Bottom seam edge: full circle at Z=0 — IS the period-crossing seam edge
bot_ax = f.axis2_placement_3d(cp(0, 0, 0), dir3(0, 0, 1), dir3(1, 0, 0))
bot_circle = f.circle(bot_ax, R)
# Same vertex start and end — IS the seam wraparound: U=0 and U=2π are identical
e_bot_seam = f.edge_curve(v_bot, v_bot, bot_circle, same_sense=True)

# Top seam edge: full circle at Z=H — IS the top period-crossing seam edge
top_ax = f.axis2_placement_3d(cp(0, 0, H), dir3(0, 0, 1), dir3(1, 0, 0))
top_circle = f.circle(top_ax, R)
e_top_seam = f.edge_curve(v_top, v_top, top_circle, same_sense=True)

# Vertical seam line edges — IS the seam-line boundary closing the parametric face
d_up = dir3(0, 0, 1)
vec_up = f.vector(d_up, H)
ln_right = f.line(p_bot, vec_up)   # seam line from bottom to top
e_right = f.edge_curve(v_bot, v_top, ln_right, same_sense=True)

d_down = dir3(0, 0, -1)
vec_down = f.vector(d_down, H)
ln_left = f.line(p_top, vec_down)  # seam line from top to bottom
e_left = f.edge_curve(v_top, v_bot, ln_left, same_sense=True)

# FACE_OUTER_BOUND loop: bottom seam → right seam-line → top seam (reversed) → left seam-line (reversed)
loop = f.edge_loop([
    f.oriented_edge(e_bot_seam, True),    # full bottom circle forward — IS the seam at U=0→2π
    f.oriented_edge(e_right,    True),    # vertical: bot → top
    f.oriented_edge(e_top_seam, False),   # full top circle reversed — IS the reversed top seam
    f.oriented_edge(e_left,     False),   # vertical reversed: bot → top as reversed
])
face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], cyl, same_sense=True)

# OPEN_SHELL: cylindrical face with seam — IS the U-closed period-wrapping mechanism
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
