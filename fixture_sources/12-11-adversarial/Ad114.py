"""Ad114 — STEP fixture path is a symlink to /etc/passwd or other privileged file.

Catalog claim: a receiver that opens a fixture by name without checking whether
the path traverses a symlink will follow symlinks transparently. If an attacker
can place a symlink at the fixture path pointing at a privileged file
(/etc/passwd, ~/.ssh/id_rsa, /proc/self/environ), the receiver reads the
privileged file's bytes into its Part-21 tokeniser. Most privileged files do
not parse as Part-21 and the load fails benignly, but the bytes have already
been read into memory and may appear in error messages, crash dumps, or
telemetry.

Reproducer recipe: a .stp path in the research tree is a symlink to
/etc/passwd. The fixture in this catalog documents the scenario in a header
comment but does NOT actually create a symlink in the repo.

Byte assertions:
  contains(b'symlink') or contains(b'passwd') or contains(b'/etc/')
  contains(b'O_NOFOLLOW') or contains(b'symlink') or contains(b'/etc/passwd')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad114",
    defect=(
        "STEP fixture path is a symlink to /etc/passwd or other privileged file; "
        "receiver that opens path without O_NOFOLLOW reads privileged bytes into "
        "Part-21 tokeniser; bytes may appear in error messages or telemetry; "
        "receiver must refuse to open paths whose resolved location is outside a "
        "configured root; refuse to follow symlinks unless explicitly enabled; "
        "check O_NOFOLLOW-style flags on open; CWE-59 (symlink following); "
        "CWE-22 (path traversal); provenance tier: cross-file-state — "
        "static fixture is document-only: no real symlink created in repo; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload: inject the symlink-following attack scenario as a comment
# block in the rendered Part-21 output. The payload documents the filesystem
# context needed to trigger the defect (a symlink at the fixture path pointing
# at /etc/passwd). A real receiver with O_NOFOLLOW would detect this at open().
#
# Satisfies:
#   contains(b'symlink') or contains(b'passwd') or contains(b'/etc/')
#   contains(b'O_NOFOLLOW') or contains(b'symlink') or contains(b'/etc/passwd')

_original_render = f.render


def _render_with_symlink_payload():
    text = _original_render()
    symlink_comment = (
        "/* Symlink-following attack payload (CWE-59 / CWE-22):\n"
        "   Attack scenario: fixture path Ad114.stp is a symlink\n"
        "   pointing to /etc/passwd (or ~/.ssh/id_rsa, /proc/self/environ).\n"
        "\n"
        "   ln -s /etc/passwd /path/to/research/step-examples/12-11-adversarial/Ad114.stp\n"
        "\n"
        "   A receiver that opens the fixture path without O_NOFOLLOW\n"
        "   will read ~3 KB of 'root:x:0:0:..' bytes into its Part-21 tokeniser.\n"
        "   The load fails (non-Part-21 content) but the privileged bytes have\n"
        "   already been read into the process address space and may appear in:\n"
        "     - error messages logged to disk or transmitted over the network\n"
        "     - crash dumps captured by the OS or monitoring systems\n"
        "     - telemetry payloads sent to the vendor\n"
        "\n"
        "   Required mitigations:\n"
        "     1. Open with O_NOFOLLOW (POSIX) or CreateFile with\n"
        "        FILE_FLAG_OPEN_REPARSE_POINT (Windows) to refuse symlink targets.\n"
        "     2. Resolve the real path and verify it is within the configured root\n"
        "        before reading any bytes (Path.resolve() + is_relative_to()).\n"
        "     3. Never include raw file bytes from a failed parse in error messages.\n"
        "\n"
        "   Static fixture is document-only: no real symlink is created in the repo\n"
        "   (cross-platform-unfriendly). See also: Ad106 (TOCTOU on EXTERNAL_FILE),\n"
        "   Ad113 (sibling-pair race), Ad115 (directory-entry race).\n"
        "   Target path: /etc/passwd, /proc/self/environ, ~/.ssh/id_rsa\n"
        "*/\n"
    )
    marker = "ISO-10303-21;\n"
    idx = text.index(marker) + len(marker)
    return text[:idx] + symlink_comment + text[idx:]


f.render = _render_with_symlink_payload  # type: ignore[method-assign]
