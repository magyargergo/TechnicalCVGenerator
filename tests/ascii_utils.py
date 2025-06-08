from pdfminer.high_level import extract_text
from typing import Iterable
import difflib


def pdf_to_ascii(pdf_path: str) -> str:
    """Return an ASCII representation of the PDF for testing."""
    return extract_text(pdf_path)


def diff_ascii(expected: str, actual: str) -> str:
    """Return a unified diff between two ASCII strings."""
    return "\n".join(
        difflib.unified_diff(
            expected.splitlines(),
            actual.splitlines(),
            fromfile="expected",
            tofile="actual",
            lineterm="",
        )
    )


def compare_with_baseline(pdf_path: str, baseline_ascii_path: str) -> None:
    """Assert that a generated PDF matches the baseline ASCII content."""
    actual = pdf_to_ascii(pdf_path)
    with open(baseline_ascii_path, "r") as fh:
        expected = fh.read()
    if actual != expected:
        diff = diff_ascii(expected, actual)
        raise AssertionError(f"PDF content mismatch:\n{diff}")
