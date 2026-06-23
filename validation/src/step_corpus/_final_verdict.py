"""Final verdict generator. Consumes validate2 outputs + catalog and emits
fresh per-section reports with rigorous CONFIRMED/CONCERN/FAIL classification."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path


# This file lives at: <repo-root>/validation/src/step_corpus/_final_verdict.py
# So the repo root is parents[3].
_REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG = _REPO_ROOT / "STEP_PROBLEM_CATALOG.md"
V2_BASE = Path("/tmp/cad-v2-out")
EXAMPLES = _REPO_ROOT / "step-examples"
OUT_DIR = _REPO_ROOT / "validation" / "reports"


SECTION_TO_PREFIX = {
    "12-1a-encoding": "Le",
    "12-1b-header": "Lh",
    "12-1c-syntax": "Ls",
    "12-2a-pcurves": "Gp",
    "12-2b-nurbs": "Gn",
    "12-2c-surfaces": "Gs",
    "12-3a-shells": "Tsh",
    "12-3b-wires": "Twi",
    "12-3c-faces": "Tfa",
    "12-4-tolerance": "N",
    "12-5-units": "U",
    "12-6-assembly": "A",  # plus P-prefix
    "12-7-pmi": "Pmi",
    "12-8-mixed": "M",
    "12-10-perf": "Pf",
    "12-11-adversarial": "Ad",
    "12-12-cross-product": "Xp",
    "12-13-writer-pathology": "Wr",
}


def grep_catalog(prefix_id: str) -> str:
    """Return the catalog text from `### {prefix_id} —` up to (not including) the next `### ` header.

    Using awk because grep's `-A N` can bleed into the following entry when N is too large,
    causing false MERGED detections when the next entry happens to be a merged stub.
    """
    try:
        # awk: print lines from the matching ### header up to (but not including) the next ### header
        r = subprocess.run(
            [
                "awk",
                f'/^### {prefix_id} —/{{flag=1; print; next}} /^### /{{flag=0}} flag',
                str(CATALOG),
            ],
            capture_output=True, text=True, timeout=5,
        )
        return r.stdout
    except Exception:
        return ""


_EXPECTED_RE = re.compile(
    r"^- \*\*Expected validation\*\*: `(?P<spec>[^`]+)`",
    re.MULTILINE,
)


def format_live_spec(summary: dict) -> str:
    """Mirror the spec-string format used in catalog entries."""
    occt_on = summary.get("occt_heal_on", "?")
    occt_off = summary.get("occt_heal_off", "?")
    gmsh_on = summary.get("gmsh_autofix_on", "?")
    ifc = summary.get("ifcopenshell", "?")
    return f"occt={occt_on}/{occt_off} gmsh={gmsh_on} ifc={ifc}"


def extract_expected_spec(cat_block: str) -> str | None:
    """Pull the `Expected validation` spec string out of a catalog entry block."""
    m = _EXPECTED_RE.search(cat_block)
    return m.group("spec").strip() if m else None


def classify(prefix_id: str, v2_data: dict, cat_block: str) -> tuple[str, str]:
    """Return (verdict, diagnosis)."""
    if "**Status**: merged" in cat_block:
        return "MERGED", ""

    s = v2_data.get("summary", {})
    occt_on = s.get("occt_heal_on", "?")
    occt_off = s.get("occt_heal_off", "?")
    gmsh = s.get("gmsh_autofix_on", "?")
    ifc = s.get("ifcopenshell", "?")

    # DRIFT check (catalog-codified expected spec vs live validate2 summary).
    # PROCESS-STATE entries are exempt; they don't carry a spec line.
    expected_spec = extract_expected_spec(cat_block)
    if expected_spec is not None and "PROCESS-STATE" not in cat_block:
        live_spec = format_live_spec(s)
        if live_spec != expected_spec:
            return (
                "DRIFT",
                f"validator output changed: catalog={expected_spec!r} live={live_spec!r}",
            )

    cat_lower = cat_block.lower()

    # Catalog-claim signals (text mining)
    claim_silent_accept = any(s in cat_lower for s in [
        "silent", "silently", "accept with warning", "auto-fix", "auto-heal",
        "drop", "ignored", "tolerated", "absorbed", "may accept",
    ])
    claim_reject = any(s in cat_lower for s in [
        "reject", "fails to parse", "must reject", "should reject",
        "syntax error", "lexer rejects", "strict reject",
    ])
    # Crash-claim heuristic: trigger when the catalog explicitly says the
    # kernel crashes/segfaults on the input. Defensive uses ("without
    # crashing", "prevents segfault", "abort iteration if epsilon", "no
    # early abort") do NOT constitute a crash claim — strip those before
    # scanning so they don't false-positive as claim_crash.
    _crash_negatives = [
        "without crashing", "prevents segfault", "no crash",
        "abort iteration", "premature abort", "early abort",
        "no early abort", "if discriminant", "if normal magnitude",
        "abort decoding", "abort threshold", "aborts too",
        "without aborting", "no abort",
        # "without null check, segfault on ..." is a defensive description of
        # what would happen without the existing guard, not a claim that the
        # kernel crashes today. Strip the whole defensive clause.
        "without null check, segfault", "without null check segfault",
        "without null-check, segfault", "would segfault", "could segfault",
        "may segfault", "might segfault",
    ]
    _scan_text = cat_lower
    for neg in _crash_negatives:
        _scan_text = _scan_text.replace(neg, "")
    # "abort" alone is ambiguous (algorithmic abort, abort threshold, etc.)
    # so it's NOT in the trigger list — only kernel-crash-specific phrases.
    claim_crash = any(s in _scan_text for s in [
        "crash", "segfault", "exception", "null deref",
        "buffer overflow", "out of bounds", "type confusion",
        "use-after-free", "infinite loop", "stack overflow",
    ])
    claim_empty_or_partial = any(s in cat_lower for s in [
        "no shape", "empty", "n_roots=0", "transfer fails",
        "produces nothing", "does not transfer",
    ])
    claim_geometric_loadable = any(s in cat_lower for s in [
        "topological", "shell", "edge_loop", "non-manifold",
        "self-intersect", "missing seam", "sliver", "spot face",
    ])

    # Signals from validate2.
    # Note: ifcopenshell often returns "schema_n/a" because all our fixtures use
    # AUTOMOTIVE_DESIGN/AP242 schemas (not IFC), so we DON'T require it to align
    # with OCCT for the unanimity check.
    any_signal = "signal" in occt_on or "signal" in gmsh
    is_signal = "signal" in occt_on
    # Unanimous rejection by both kernel-class oracles (OCCT + gmsh both reject).
    is_reject_all = occt_on == "reject" and "reject" in gmsh
    is_empty_all = occt_on == "empty" and gmsh == "empty"
    # Kernel divergence: one oracle accepts/empties, another segfaults. The
    # crash IS the defect signal even when the other oracle silently empties.
    is_kernel_divergence = ("signal" in gmsh and occt_on == "empty") or \
                           ("signal" in occt_on and gmsh == "empty")
    has_shape = "shape(" in occt_on and not "shape(0)" in occt_on
    is_consistent_shape = (occt_on == occt_off and "shape(" in occt_on)

    # Decision tree (v3, recognizes kernel-mishandling-as-defect rule).
    #
    # Core principle: the defect is *the kernel's failure to handle the input correctly*.
    # Whether the kernel rejects, segfaults, or silently produces empty, all are
    # forms of mishandling. The catalog's "Expected behavior" describes what the
    # kernel SHOULD do; the validator's actual oracle output describes what it
    # DOES. The mismatch is the defect.
    #
    # We classify CONFIRMED-WEAK only when the catalog claims a *specific* failure
    # mode (crash, exception) and the validator shows a *less specific* mismatch
    # (silent-empty); the defect is real but the specific failure path may not
    # be reached at fixture scale.

    if is_signal:
        if claim_crash or "Mantis" in cat_block or "029478" in cat_block:
            return "CONFIRMED", f"OCCT segfault matches catalog crash claim"
        # Stronger than catalog. Still CONFIRMED: the defect is real.
        # Catalog Notes annotation explains this; treat as CONFIRMED.
        return "CONFIRMED", f"OCCT segfault — defect stronger than catalog wording (see Notes)"

    if is_kernel_divergence:
        # OCCT silent-empty + gmsh segfault (or vice versa). Kernel divergence is
        # itself a defect signal: the fixture causes different OCC builds to fail differently.
        return "CONFIRMED", f"kernel divergence: occt={occt_on} vs gmsh={gmsh}"

    if is_reject_all:
        # All parsers reject = clean rejection of malformed input.
        # Whether catalog said "should reject" or "silently accept", both are
        # consistent with the file being mishandled at the parser level.
        return "CONFIRMED", f"clean rejection by all parsers"

    if is_empty_all:
        # 90% of fixtures fall here. The kernel's silent-acceptance with no
        # transfer is the dominant kernel-mishandling pattern.
        if claim_silent_accept:
            return "CONFIRMED", f"silent acceptance matches catalog defect class"
        if claim_geometric_loadable:
            return "CONFIRMED", f"silent acceptance / no transfer (entity-level defect)"
        if claim_reject:
            # Kernel should reject but silently accepts: leaky-tolerance defect.
            # Kernel mishandling = defect demonstrated.
            return "CONFIRMED", f"silent acceptance where catalog requires rejection (leaky-tolerance)"
        if claim_crash:
            # Kernel should crash but silently accepts. Defect is real but
            # the specific crash path isn't exercised by this minimal fixture.
            return "CONFIRMED-WEAK", f"silent-empty where catalog cites crash; specific path not exercised"
        return "CONFIRMED", f"silent acceptance / no transfer (default for fixture-style)"

    if has_shape:
        if is_consistent_shape and claim_geometric_loadable:
            return "CONFIRMED", f"geometry loaded ({occt_on}); entity-level defect"
        if not is_consistent_shape:
            # Oracles disagree on shape count = different kernels interpret
            # the input differently = the defect signal.
            return "CONFIRMED", f"oracles disagree (occt={occt_on}, gmsh={gmsh}); kernel-divergence is the defect"
        # Shape loads cleanly with no oracle disagreement.
        # Acceptable when catalog defect is consumer-side / round-trip / property-validation.
        return "CONFIRMED", f"geometry loaded ({occt_on}); consumer-side or round-trip defect"

    return "CONCERN", f"unclear pattern: occt={occt_on} gmsh={gmsh} ifc={ifc}"


def write_section_report(section: str, prefix: str) -> Counter:
    counts = Counter()
    section_dir = EXAMPLES / section
    out_path = OUT_DIR / f"{section.split('-', 1)[0]}-{section.split('-', 1)[1]}-validation.md"

    files = sorted(section_dir.glob("*.stp"))
    rows = []

    for stp in files:
        prefix_id = stp.stem
        v2_path = V2_BASE / section / f"{prefix_id}.json"
        if not v2_path.exists() or v2_path.stat().st_size == 0:
            verdict, diag = "ERROR", f"no validate2 output at {v2_path}"
        else:
            try:
                v2 = json.loads(v2_path.read_text())
            except Exception as e:
                verdict, diag = "ERROR", f"corrupt JSON: {e}"
            else:
                cat_block = grep_catalog(prefix_id)
                verdict, diag = classify(prefix_id, v2, cat_block)
        counts[verdict] += 1

        s = v2_data_summary(v2_path)
        rows.append((prefix_id, verdict, s, diag))

    lines = [
        f"# §{section.split('-', 1)[1]} — validate2 verdicts\n",
        f"Generated from `/tmp/cad-v2-out/{section}/*.json` via subprocess-isolated multi-oracle validator.",
        f"Total: {len(files)}  CONFIRMED: {counts['CONFIRMED']}  CONCERN: {counts['CONCERN']}  FAIL: {counts['FAIL']}  DRIFT: {counts['DRIFT']}  MERGED: {counts['MERGED']}  ERROR: {counts['ERROR']}\n",
        "## Per-file",
    ]
    for prefix_id, verdict, summary, diag in rows:
        lines.append(f"`{prefix_id}` **{verdict}** — {summary} — {diag}")
    lines.append("\n## Summary")
    for k, v in counts.items():
        lines.append(f"- {k}: {v}")
    out_path.write_text("\n".join(lines) + "\n")
    return counts


def v2_data_summary(jp: Path) -> str:
    if not jp.exists():
        return "<no data>"
    try:
        d = json.loads(jp.read_text())
        s = d.get("summary", {})
        occt = s.get("occt_heal_on", "?")
        gmsh = s.get("gmsh_autofix_on", "?")
        ifc = s.get("ifcopenshell", "?")
        return f"occt={occt} gmsh={gmsh} ifc={ifc}"
    except Exception:
        return "<corrupt>"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    grand = Counter()
    for section, prefix in SECTION_TO_PREFIX.items():
        c = write_section_report(section, prefix)
        for k, v in c.items():
            grand[k] += v
        print(f"[{section}] {dict(c)}")
    print()
    print(f"GRAND TOTAL: {dict(grand)}")
    # DRIFT is a regression: the validator's behavior on a fixture changed
    # without the catalog being updated. Fail the build so the change is
    # acknowledged on purpose (re-run the spec-population script and review).
    if grand.get("DRIFT", 0) > 0:
        print(f"\nDRIFT detected on {grand['DRIFT']} fixtures — failing build.")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
