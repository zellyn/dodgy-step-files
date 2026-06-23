"""Ctl003 — Clean cylindrical ADVANCED_FACE (negative control for §12-2c-surfaces).

A half-cylinder wall: radius=1, height=2, theta=0..pi.  One seam edge at
theta=0 and theta=pi, two half-circle boundary edges at z=0 and z=2.
CYLINDRICAL_SURFACE is correctly placed; same_sense=True.

Expected: occt=shape(1)/shape(1)
"""
import sys
import math
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl003",
    defect="NEGATIVE CONTROL: clean cylindrical ADVANCED_FACE, no surface defect",
)

R = 1.0
H = 2.0

# Axis along +Z, origin at (0,0,0), ref-direction +X
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_ax   = f.direction((0.0, 0.0, 1.0))
cyl_ref  = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_ax, cyl_ref)
cyl_surf = f.cylindrical_surface(cyl_plc, R)

# Seam vertices: theta=0 → (R,0,*), theta=pi → (-R,0,*)
p0b = f.cartesian_point((R,  0.0, 0.0))   # theta=0,  z=0
pPb = f.cartesian_point((-R, 0.0, 0.0))   # theta=pi, z=0
p0t = f.cartesian_point((R,  0.0, H))     # theta=0,  z=H
pPt = f.cartesian_point((-R, 0.0, H))     # theta=pi, z=H

v0b = f.vertex_point(p0b); vPb = f.vertex_point(pPb)
v0t = f.vertex_point(p0t); vPt = f.vertex_point(pPt)

# Bottom circle (z=0) and top circle (z=H)
bot_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)), f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))
)
bot_circle = f.circle(bot_plc, R)

top_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, H)), f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))
)
top_circle = f.circle(top_plc, R)

# Half-arc edge_curves (theta=0..pi)
bot_arc = f.edge_curve(v0b, vPb, bot_circle, True)
top_arc = f.edge_curve(v0t, vPt, top_circle, True)

# Vertical seam edges at theta=0 and theta=pi
zdir = f.direction((0.0, 0.0, 1.0))
zvec = f.vector(zdir, H)
seam0_line = f.line(p0b, zvec)
seamP_line = f.line(pPb, zvec)
seam0 = f.edge_curve(v0b, v0t, seam0_line, True)
seamP = f.edge_curve(vPb, vPt, seamP_line, True)

oe = f.oriented_edge
loop = f.edge_loop([
    oe(bot_arc,  True),    # bottom arc: v0b -> vPb
    oe(seamP,    True),    # seam pi: vPb -> vPt
    oe(top_arc,  False),   # top arc reversed: vPt -> v0t
    oe(seam0,    False),   # seam 0 reversed: v0t -> v0b
])

face = f.advanced_face([f.face_outer_bound(loop)], cyl_surf, True)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
