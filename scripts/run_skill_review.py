import argparse
import json
from pathlib import Path

from check_references import validate as validate_references
from inspect_package import inspect_package
from validate_metadata import validate as validate_metadata


RULE_DETAILS = {
    "GATE-META-001": {"title": "Skill root must contain SKILL.md", "severity": "blocker"},
    "GATE-META-002": {"title": "SKILL.md must contain valid frontmatter", "severity": "blocker"},
    "GATE-META-003": {"title": "name must match naming rules", "severity": "blocker"},
    "GATE-META-004": {"title": "description must exist", "severity": "blocker"},
    "GATE-META-005": {"title": "description must include function and trigger", "severity": "blocker"},
    "GATE-REF-001": {"title": "Referenced relative files must exist", "severity": "major"},
    "GATE-STRUCT-001": {"title": "Package structure must be parseable", "severity": "major"},
    "GATE-SEC-001": {"title": "Package must not hardcode obvious secrets", "severity": "blocker"},
}

EVIDENCE_SOURCES = {
    "official": {
        "source_level": "official",
        "source_title": "Anthropic Help Center - How to create custom Skills",
        "source_url": "https://support.anthropic.com/en/articles/12512198-how-to-create-custom-skills",
        "source_quote": "A clear description of what the Skill does and when to use it.",
    },
    "standard": {
        "source_level": "standard",
        "source_title": "Agent Skills Specification",
        "source_url": "https://agentskills.io/specification",
        "source_quote": "A skill is a directory containing, at minimum, a SKILL.md file.",
    },
}


def classify_grade(score: int) -> str:
    if score >= 90:
        return "recommended"
    if score >= 75:
        return "usable"
    if score >= 60:
        return "needs-improvement"
    return "not-recommended"


def summarize_gate_results(metadata_result: dict, ref_result: dict, package_info: dict) -> list[dict]:
    issue_map = {}
    for issue in metadata_result.get("issues", []):
        issue_map[issue["rule_id"]] = issue
    for issue in ref_result.get("issues", []):
        issue_map[issue["rule_id"]] = issue

    results = []
    for rule_id, details in RULE_DETAILS.items():
        if rule_id == "GATE-STRUCT-001":
            if package_info.get("has_skill_md"):
                results.append(
                    {
                        "rule_id": rule_id,
                        "status": "pass",
                        "severity": details["severity"],
                        "summary": "Core package structure is reachable.",
                    }
                )
            else:
                results.append(
                    {
                        "rule_id": rule_id,
                        "status": "fail",
                        "severity": details["severity"],
                        "summary": "Missing core package files.",
                    }
                )
            continue

        if rule_id == "GATE-SEC-001":
            results.append(
                {
                    "rule_id": rule_id,
                    "status": "not_applicable",
                    "severity": details["severity"],
                    "summary": "Secret scanning is not implemented in this lightweight runner.",
                }
            )
            continue

        issue = issue_map.get(rule_id)
        if issue:
            results.append(
                {
                    "rule_id": rule_id,
                    "status": "fail",
                    "severity": issue.get("severity", details["severity"]),
                    "summary": issue.get("message", details["title"]),
                }
            )
        else:
            results.append(
                {
                    "rule_id": rule_id,
                    "status": "pass",
                    "severity": details["severity"],
                    "summary": details["title"],
                }
            )
    return results


def build_quality_score(gate_results: list[dict], ref_result: dict, package_info: dict) -> dict:
    scores = {"S-01": 20, "S-02": 20, "S-03": 20, "S-04": 20, "S-05": 20}
    failed_rules = {item["rule_id"] for item in gate_results if item["status"] == "fail"}

    if "GATE-META-005" in failed_rules:
        scores["S-02"] -= 12
    if "GATE-META-003" in failed_rules:
        scores["S-01"] -= 8
    if "GATE-REF-001" in failed_rules:
        scores["S-04"] -= 8
    if not package_info.get("has_scripts_dir"):
        scores["S-05"] -= 6
    if ref_result.get("summary", {}).get("checked_references", 0) == 0:
        scores["S-04"] -= 4

    for key in scores:
        scores[key] = max(0, min(20, scores[key]))

    dimensions = [
        {"dimension_id": "S-01", "score": scores["S-01"], "summary": "Task focus and package intent alignment."},
        {"dimension_id": "S-02", "score": scores["S-02"], "summary": "Trigger clarity in metadata description."},
        {"dimension_id": "S-03", "score": scores["S-03"], "summary": "Instruction quality and execution readability."},
        {"dimension_id": "S-04", "score": scores["S-04"], "summary": "Resource layering and reference hygiene."},
        {"dimension_id": "S-05", "score": scores["S-05"], "summary": "Failure defense and deterministic guardrails."},
    ]
    total = sum(scores.values())
    return {"total_score": total, "grade": classify_grade(total), "dimensions": dimensions}


def build_findings(gate_results: list[dict]) -> list[dict]:
    findings = []
    for item in gate_results:
        if item["status"] != "fail":
            continue
        findings.append(
            {
                "severity": "high" if item["severity"] == "blocker" else "medium",
                "area": item["rule_id"].lower(),
                "issue": item["summary"],
                "evidence_level": "official_or_standard",
                "related_rules": [item["rule_id"]],
            }
        )
    return findings


def build_evidence_log(gate_results: list[dict]) -> list[dict]:
    log = []
    for item in gate_results:
        if item["status"] != "fail":
            continue
        source = EVIDENCE_SOURCES["official"] if item["rule_id"].startswith("GATE-META") else EVIDENCE_SOURCES["standard"]
        log.append({**source, "supports": [item["rule_id"]]})
    if not log:
        log.append({**EVIDENCE_SOURCES["standard"], "supports": ["baseline"]})
    return log


def build_fixes(gate_results: list[dict]) -> dict:
    failed = [item["rule_id"] for item in gate_results if item["status"] == "fail"]
    immediate = []
    if "GATE-META-003" in failed:
        immediate.append("Align frontmatter `name` with the skill directory name `skill-reviewer`.")
    if "GATE-META-005" in failed:
        immediate.append("Rewrite `description` to include both skill purpose and trigger timing.")
    if "GATE-REF-001" in failed:
        immediate.append("Fix or remove broken relative links in SKILL.md.")
    if not immediate:
        immediate.append("No blocker fixes required.")

    return {
        "immediate": immediate,
        "structural": [
            "Keep gate rules and scoring rules separated under references/.",
            "Use scripts for deterministic checks and avoid prompt-only validation.",
        ],
        "optional": [
            "Expand benchmark coverage under evals/.",
            "Add deeper security scanning for GATE-SEC-001.",
        ],
    }


def render_markdown(report: dict) -> str:
    lines = []
    lines.append(f"# Skill Review Report: {report['skill_name']}")
    lines.append("")
    lines.append("## Evaluation Scope")
    lines.append(f"- Package path: `{report['package_path']}`")
    lines.append(f"- Coverage: `{report['coverage']}`")
    lines.append(f"- Reviewer version: `{report.get('reviewer_version', '1.0.0')}`")
    lines.append("")
    lines.append("## Gate Summary")
    lines.append(f"- Overall gate status: `{report['gate_summary']['overall_status']}`")
    lines.append("")
    lines.append("| Rule ID | Status | Severity | Summary |")
    lines.append("| --- | --- | --- | --- |")
    for item in report["gate_summary"]["results"]:
        lines.append(f"| {item['rule_id']} | {item['status']} | {item['severity']} | {item['summary']} |")
    lines.append("")
    lines.append("## Quality Score")
    lines.append(f"- Total score: `{report['quality_score']['total_score']}/100`")
    lines.append(f"- Grade: `{report['quality_score']['grade']}`")
    lines.append("")
    lines.append("| Dimension | Score | Summary |")
    lines.append("| --- | --- | --- |")
    for dimension in report["quality_score"]["dimensions"]:
        lines.append(f"| {dimension['dimension_id']} | {dimension['score']} | {dimension['summary']} |")
    lines.append("")
    lines.append("## Findings")
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(f"- [{finding['severity']}] {finding['issue']} ({', '.join(finding['related_rules'])})")
    else:
        lines.append("- No high-risk findings.")
    lines.append("")
    lines.append("## Actionable Fixes")
    lines.append("### Immediate")
    for item in report["fixes"]["immediate"]:
        lines.append(f"- {item}")
    lines.append("### Structural")
    for item in report["fixes"]["structural"]:
        lines.append(f"- {item}")
    lines.append("### Optional")
    for item in report["fixes"]["optional"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def run_review(skill_dir: Path) -> dict:
    package_info = inspect_package(skill_dir)
    metadata_result = validate_metadata(skill_dir)
    ref_result = validate_references(skill_dir)
    gate_results = summarize_gate_results(metadata_result, ref_result, package_info)

    overall_gate_status = "fail" if any(item["status"] == "fail" for item in gate_results) else "pass"
    quality_score = build_quality_score(gate_results, ref_result, package_info)

    return {
        "skill_name": metadata_result.get("summary", {}).get("skill_name") or skill_dir.name,
        "package_path": str(skill_dir),
        "coverage": "full-package",
        "reviewer_version": "1.0.0",
        "gate_summary": {
            "overall_status": overall_gate_status,
            "results": gate_results,
        },
        "quality_score": quality_score,
        "findings": build_findings(gate_results),
        "evidence_log": build_evidence_log(gate_results),
        "fixes": build_fixes(gate_results),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run skill-reviewer package review and generate Markdown/JSON reports.")
    parser.add_argument("skill_dir", help="Default path to the target skill package root.")
    parser.add_argument("--target", default=None, help="Optional explicit target skill package path. Overrides positional path.")
    parser.add_argument("--output-dir", default="reports", help="Directory where report files will be written.")
    parser.add_argument("--strict", action="store_true", help="Return exit code 2 when any blocker gate fails.")
    args = parser.parse_args()

    skill_dir = Path(args.target).resolve() if args.target else Path(args.skill_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    report = run_review(skill_dir)
    report_json_path = output_dir / "skill-review-report.json"
    report_md_path = output_dir / "skill-review-report.md"
    report_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_md_path.write_text(render_markdown(report), encoding="utf-8")

    gate_results = report.get("gate_summary", {}).get("results", [])
    has_any_fail = any(item.get("status") == "fail" for item in gate_results)
    has_blocker_fail = any(item.get("status") == "fail" and item.get("severity") == "blocker" for item in gate_results)

    print(
        json.dumps(
            {
                "json_report": str(report_json_path),
                "markdown_report": str(report_md_path),
                "strict_mode": args.strict,
                "target_path": str(skill_dir),
            },
            ensure_ascii=False,
        )
    )
    if args.strict and has_blocker_fail:
        return 2
    if has_any_fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
