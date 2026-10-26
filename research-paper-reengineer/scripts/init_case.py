#!/usr/bin/env python3
"""Create a non-destructive reconstruction workspace from bundled templates."""
import argparse
import json
from pathlib import Path
import re
import shutil


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:70].rstrip("-") or "paper"


def init_case(title: str, output: Path) -> list[str]:
    assets = Path(__file__).resolve().parent.parent / "assets"
    if not assets.is_dir():
        raise RuntimeError(f"Cannot find assets directory at {assets}")
    output.mkdir(parents=True, exist_ok=True)
    for name in ("sources", "implementation", "tests", "experiments", "artifacts"):
        (output / name).mkdir(exist_ok=True)
    files = {"case.json": "case.json", "evidence.csv": "evidence.csv",
             "architecture-spec.md": "architecture-spec.md",
             "test-plan.md": "test-plan.md",
             "reconstruction-report.md": "reconstruction-report.md"}
    created = []
    for source_name, dest_name in files.items():
        dest = output / dest_name
        if dest.exists():
            continue
        if source_name == "case.json":
            content = json.loads((assets / source_name).read_text(encoding="utf-8"))
            content["title"] = title
            # exclusive-create, never clobber existing user work
            with dest.open("x", encoding="utf-8") as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
                f.write("\n")
        else:
            # creation with x mode is atomic wrt file overwrites
            with dest.open("x", encoding="utf-8") as f:
                f.write((assets / source_name).read_text(encoding="utf-8"))
        created.append(str(dest))
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="Research paper or target component")
    parser.add_argument("--output", type=Path, help="Destination; defaults to ./recon/<title-slug>")
    args = parser.parse_args()
    dest = args.output or Path("recon") / slugify(args.title)
    try:
        created = init_case(args.title, dest)
    except (OSError, ValueError, RuntimeError) as e:
        parser.exit(2, f"error: {e}\n")
    print(f"Workspace: {dest.resolve()}")
    print(f"Created {len(created)} new template files; existing files preserved.")
    for p in created:
        print(f" + {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
