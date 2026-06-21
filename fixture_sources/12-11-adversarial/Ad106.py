"""Ad106 — EXTERNAL_FILE URI resolves through a symlink (TOCTOU race).

Catalog claim: an EXTERNAL_FILE entry references a sibling Part-21 file
via a path. A receiver that follows the path performs at minimum two
filesystem operations: a stat / access check and an open (to read the
bytes). On systems where the path resolves through a symlink, the symlink
target may change between the check and the open; the classic TOCTOU race.

Reproducer recipe: a STEP file whose REFERENCE / EXTERNAL_FILE clause
names a path /tmp/parts/widget.stp; the receiver-side filesystem is set
up so /tmp/parts/widget.stp is a symlink that the attacker can swap
between the check and the open.

Provenance note: this is a cross-file-state defect; the symlink-swap
requires receiver-side filesystem manipulation. The static fixture encodes
only the path-naming precondition.

Byte assertions:
  contains(b'REFERENCE;') or contains(b'EXTERNAL_FILE') or contains(b'/tmp/')
  contains(b'companion') or contains(b'/tmp/parts/') or contains(b'widget.stp')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad106",
    defect=(
        "EXTERNAL_FILE URI resolves through a symlink; "
        "receiver performs stat then open — TOCTOU race; "
        "symlink target may change between check and open, "
        "causing receiver to read a different file than it validated; "
        "receiver must open path once and stat the resulting fd; "
        "must not re-resolve path between check and open; "
        "must refuse to follow symlinks unless explicitly enabled; "
        "must reject EXTERNAL_FILE paths resolving outside configured root; "
        "CWE-367; ISO 10303-21 Ed.3 §8 REFERENCE/EXTERNAL_FILE; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: raw REFERENCE section + EXTERNAL_FILE entity naming
# a symlink-susceptible path /tmp/parts/widget.stp.
# The REFERENCE section is injected by overriding render() to insert the
# ISO 10303-21 Ed.3 REFERENCE block after ENDSEC; (before END-ISO-10303-21;).
#
# Satisfies:
#   contains(b'EXTERNAL_FILE')          — raw entity in DATA
#   contains(b'/tmp/')                   — path in EXTERNAL_FILE
#   contains(b'/tmp/parts/')             — specific path component
#   contains(b'widget.stp')             — companion filename
#   contains(b'companion')              — label in entity name
#   contains(b'REFERENCE;')             — injected REFERENCE section keyword

# Emit EXTERNAL_FILE entity in DATA section.
# This declares the path that is susceptible to the TOCTOU symlink race.
f._emit_raw(
    "EXTERNAL_FILE('companion_widget',('/tmp/parts/widget.stp'),"
    "'application/step',$)"
)

# Also emit a REFERENCE entity documenting the companion file relationship.
f._emit_raw(
    "/* TOCTOU race payload:\n"
    "   EXTERNAL_FILE path: /tmp/parts/widget.stp\n"
    "   Receiver checks access('/tmp/parts/widget.stp') then\n"
    "   open('/tmp/parts/widget.stp') — two separate syscalls.\n"
    "   Between the stat and the open, an attacker swaps the symlink:\n"
    "     /tmp/parts/widget.stp -> /tmp/parts/safe.stp  (at stat time)\n"
    "     /tmp/parts/widget.stp -> /etc/shadow          (at open time)\n"
    "   Receiver reads /etc/shadow despite validating /tmp/parts/safe.stp.\n"
    "   Fix: open-then-fstat; never re-resolve path after initial open. */"
    "\nCARTESIAN_POINT('toctou_note',(0.0,0.0,0.0))"
)

# Override render() to inject a REFERENCE section after ENDSEC; (before END-ISO-10303-21;).
# This is the Ed.3 REFERENCE block syntax — a second named section in the file.
_original_render = f.render

def _render_with_reference_section():
    text = _original_render()
    # Insert REFERENCE; block between ENDSEC; and END-ISO-10303-21;
    tail = "END-ISO-10303-21;"
    idx = text.index(tail)
    reference_section = (
        "REFERENCE;\n"
        "/* EXTERNAL_FILE /tmp/parts/widget.stp resolves through a symlink;\n"
        "   TOCTOU race: symlink target can be swapped between stat and open.\n"
        "   companion file: widget.stp */\n"
        "ENDSEC;\n"
    )
    return text[:idx] + reference_section + text[idx:]

f.render = _render_with_reference_section  # type: ignore[method-assign]
