"""Tsh136 — ShapeFix_Shell.FixFaceOrientation degenerate-shell-empty

Catalog claim: "Empty shell (zero faces). ShapeFix_Shell::FixFaceOrientation
iterates zero times over face list but returns success status, masking the
degenerate input."

Demonstration: construct a shell with no faces. The OPEN_SHELL or CLOSED_SHELL
contains an empty face list. Shell geometry is completely degenerate.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh136",
             defect="Empty shell with zero faces")

# Create an empty shell (no faces at all)
empty_shell = f.open_shell([])

# Wrap in surface model
sbsm = f.shell_based_surface_model([empty_shell])
f.add_product_chain(sbsm)
