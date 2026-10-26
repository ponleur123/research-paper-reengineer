#!/usr/bin/env python3
"""Perform a structural audit of a reconstruction claim-evidence CSV."""
import argparse
import csv
from collections import Counter
from pathlib import Path

FIELDS = ("claim_id", "claim", "source_kind", "source_locator", "artifact_path",
          "evidence", "status", "test_id", "notes")
STATUSES = {"observed", "derived", "hypothesis", "contradicted", "unknown"}


def audit(path: Path):
    errors = []
    warnings = []
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        missing = [col for col in FIELDS if col not in columns]
        if missing:
            errors.append(f"missing columns: {', '.join(missing)}")
        if len(columns) != len(set(columns)):
            errors.append("duplicate header column")
        for line_no, row in enumerate(reader, start=2):
            if None in row:
                errors.append(f"line {line_no}: too many columns")
                continue
            rows.append((line_no, row))
    ids = set()
    for line_no, row in rows:
        def field(name):
            return (row.get(name) or "").strip()
        claim_id = field("claim_id")
        status = field("status").lower()
        if not claim_id:
            errors.append(f"line {line_no}: missing claim_id")
        elif claim_id in ids:
            errors.append(f"line {line_no}: repeated claim_id {claim_id}")
        else:
            ids.add(claim_id)
        if not field("claim"):
            errors.append(f"line {line_no}: missing claim")
        if status not in STATUSES:
            errors.append(f"line {line_no}: invalid status '{status}'")
        if status in {"observed", "contradicted"}:
            for required in ("source_kind", "source_locator", "evidence"):
                if not field(required):
                    errors.append(f"line {line_no}: {status} claim missing {required}")
        if status == "derived" and not (field("evidence") and (field("source_locator") or field("notes"))):
            errors.append(f"line {line_no}: derived claim needs reasoning and sources/linked IDs")
        if status in {"unknown", "hypothesis"} and not field("notes"):
            warnings.append(f"line {line_no}: {status} claim needs a limitation or discriminating test in notes")
        if status in {"observed", "derived"} and not field("test_id"):
            warnings.append(f"line {line_no}: no verification test linked to claim {claim_id}")
    counts = Counter((row.get("status") or "").strip().lower() for _, row in rows)
    if not rows:
        warnings.append("No claims recorded yet; audit cannot verify science or provenance.")
    return errors, warnings, counts, len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path, help="Path to evidence.csv")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()
    try:
        errors, warnings, counts, size = audit(args.csv_file)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        parser.exit(2, f"error reading CSV: {exc}\n")
    print(f"Claims: {size}")
    for status in sorted(STATUSES):
        print(f"  {status}: {counts[status]}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    print(f"Structural audit: {'FAIL' if errors or (args.strict and warnings) else 'PASS'}")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
