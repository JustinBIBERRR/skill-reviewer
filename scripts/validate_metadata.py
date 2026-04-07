import json
import re
import sys
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TRIGGER_HINTS = (
    "use when",
    "when ",
    "if ",
    "for requests",
    "when users ask",
    "when the user",
    "当",
    "用于",
    "在",
)
VAGUE_DESCRIPTION_PATTERNS = (
    "helps with",
    "a skill for coding",
    "tool for coding",
)


def parse_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("SKILL.md is missing YAML frontmatter.")

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("SKILL.md frontmatter is not closed correctly.")

    frontmatter_block = parts[1].strip()
    metadata = {}
    for raw_line in frontmatter_block.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("'\"")
    return metadata


def build_issue(rule_id: str, message: str, severity: str = "blocker") -> dict:
    return {"rule_id": rule_id, "severity": severity, "message": message}


def has_meaningful_purpose(description: str) -> bool:
    normalized = description.strip().lower()
    if not normalized:
        return False
    if any(pattern in normalized for pattern in VAGUE_DESCRIPTION_PATTERNS):
        return False

    # English-like token count check.
    token_count = len([token for token in re.split(r"\s+", normalized) if token])
    if token_count >= 6:
        return True

    # Fallback for CJK-like descriptions without spaces.
    compact = re.sub(r"\s+", "", description)
    if len(compact) >= 12:
        return True

    return False


def validate(skill_dir: Path) -> dict:
    issues = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        issues.append(build_issue("GATE-META-001", "Missing SKILL.md in skill root."))
        return {"status": "fail", "issues": issues, "summary": {"directory_name": skill_dir.name}}

    try:
        metadata = parse_frontmatter(skill_md)
    except ValueError as exc:
        issues.append(build_issue("GATE-META-002", str(exc)))
        return {"status": "fail", "issues": issues, "summary": {"directory_name": skill_dir.name}}

    name = metadata.get("name", "")
    description = metadata.get("description", "")

    if not name:
        issues.append(build_issue("GATE-META-003", "Missing required `name` field."))
    elif not NAME_PATTERN.match(name):
        issues.append(build_issue("GATE-META-003", "Skill `name` must use lowercase letters, numbers, and hyphens only."))
    elif name != skill_dir.name:
        issues.append(build_issue("GATE-META-003", "Skill `name` must match the parent directory name."))

    if not description:
        issues.append(build_issue("GATE-META-004", "Missing required `description` field."))
    else:
        lowered = description.lower()
        has_trigger = any(hint in lowered for hint in TRIGGER_HINTS)
        has_purpose = has_meaningful_purpose(description)
        if not (has_purpose and has_trigger):
            issues.append(
                build_issue(
                    "GATE-META-005",
                    "`description` must describe what the skill does and when to use it.",
                )
            )

    status = "pass" if not issues else "fail"
    return {
        "status": status,
        "issues": issues,
        "summary": {
            "skill_name": name or None,
            "directory_name": skill_dir.name,
            "description_length": len(description),
        },
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"status": "fail", "issues": [build_issue("CLI-ARGS", "Usage: py scripts/validate_metadata.py <skill-dir>", "major")]}))
        return 2

    skill_dir = Path(sys.argv[1]).resolve()
    result = validate(skill_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
