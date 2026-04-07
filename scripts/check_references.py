import json
import re
import sys
from pathlib import Path


MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def build_issue(rule_id: str, message: str, severity: str = "major") -> dict:
    return {"rule_id": rule_id, "severity": severity, "message": message}


def extract_relative_references(text: str) -> list[str]:
    references = []
    for match in MARKDOWN_LINK_PATTERN.findall(text):
        ref = match.strip()
        if "://" in ref or ref.startswith("#"):
            continue
        references.append(ref)
    return references


def validate(skill_dir: Path) -> dict:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {
            "status": "fail",
            "issues": [build_issue("GATE-META-001", "Missing SKILL.md in skill root.", "blocker")],
            "summary": {"checked_references": 0},
        }

    text = skill_md.read_text(encoding="utf-8")
    refs = extract_relative_references(text)
    missing = []
    for ref in refs:
        target = (skill_dir / ref).resolve()
        if not target.exists():
            missing.append(ref)

    issues = [
        build_issue("GATE-REF-001", f"Referenced file does not exist: {ref}")
        for ref in missing
    ]
    return {
        "status": "pass" if not issues else "fail",
        "issues": issues,
        "summary": {
            "checked_references": len(refs),
            "missing_references": len(missing),
        },
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"status": "fail", "issues": [build_issue("CLI-ARGS", "Usage: py scripts/check_references.py <skill-dir>")]}))
        return 2

    skill_dir = Path(sys.argv[1]).resolve()
    result = validate(skill_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
