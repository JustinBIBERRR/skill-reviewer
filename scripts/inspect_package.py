import json
import sys
from pathlib import Path


def inspect_package(skill_dir: Path) -> dict:
    expected = ["SKILL.md", "README.md", "references", "assets", "scripts"]
    entries = {path.name for path in skill_dir.iterdir()} if skill_dir.exists() else set()
    present = [name for name in expected if name in entries]
    missing = [name for name in expected if name not in entries]

    return {
        "package_path": str(skill_dir),
        "present": present,
        "missing": missing,
        "has_skill_md": "SKILL.md" in entries,
        "has_reference_dir": "references" in entries,
        "has_assets_dir": "assets" in entries,
        "has_scripts_dir": "scripts" in entries,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: py scripts/inspect_package.py <skill-dir>"}))
        return 2

    skill_dir = Path(sys.argv[1]).resolve()
    print(json.dumps(inspect_package(skill_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
