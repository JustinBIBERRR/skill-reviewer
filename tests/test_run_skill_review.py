import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_skill_review.py"


class RunSkillReviewCliTests(unittest.TestCase):
    def write_file(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")

    def run_cli(self, skill_dir: Path, output_dir: Path):
        return subprocess.run(
            ["py", str(SCRIPT), str(skill_dir), "--output-dir", str(output_dir)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

    def run_cli_with_args(self, args: list[str]):
        return subprocess.run(
            ["py", str(SCRIPT), *args],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

    def test_generates_markdown_and_json_report_for_valid_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skill-reviewer"
            output_dir = Path(tmp) / "reports"
            self.write_file(
                skill_dir / "SKILL.md",
                """
                ---
                name: skill-reviewer
                description: Review skill packages when users ask for a review or score.
                ---

                See [gate rules](references/gate-rules.md).
                Use [report template](assets/report-template.md).
                """,
            )
            self.write_file(skill_dir / "README.md", "# skill-reviewer")
            self.write_file(skill_dir / "references" / "gate-rules.md", "# Gate Rules")
            self.write_file(skill_dir / "assets" / "report-template.md", "# Report Template")
            self.write_file(skill_dir / "scripts" / "helper.py", "print('ok')")

            result = self.run_cli(skill_dir, output_dir)
            self.assertEqual(result.returncode, 0, result.stderr)

            report_json = output_dir / "skill-review-report.json"
            report_md = output_dir / "skill-review-report.md"
            self.assertTrue(report_json.exists())
            self.assertTrue(report_md.exists())

            payload = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertIn("gate_summary", payload)
            self.assertIn("quality_score", payload)
            self.assertEqual(payload["gate_summary"]["overall_status"], "pass")
            self.assertEqual(payload["skill_name"], "skill-reviewer")

    def test_returns_nonzero_when_gate_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skill-reviewer"
            output_dir = Path(tmp) / "reports"
            self.write_file(
                skill_dir / "SKILL.md",
                """
                ---
                name: wrong-reviewer-name
                description: Review skill packages.
                ---

                # Broken
                """,
            )

            result = self.run_cli(skill_dir, output_dir)
            self.assertEqual(result.returncode, 1)

            report_json = output_dir / "skill-review-report.json"
            payload = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["gate_summary"]["overall_status"], "fail")
            failed = [r for r in payload["gate_summary"]["results"] if r["status"] == "fail"]
            self.assertGreaterEqual(len(failed), 1)

    def test_target_flag_overrides_positional_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken_dir = Path(tmp) / "broken"
            valid_dir = Path(tmp) / "skill-reviewer"
            output_dir = Path(tmp) / "reports"

            self.write_file(
                broken_dir / "SKILL.md",
                """
                ---
                name: wrong-reviewer-name
                description: Review skill packages.
                ---
                """,
            )

            self.write_file(
                valid_dir / "SKILL.md",
                """
                ---
                name: skill-reviewer
                description: Review skill packages when users ask for a review or score.
                ---

                See [gate rules](references/gate-rules.md).
                """,
            )
            self.write_file(valid_dir / "references" / "gate-rules.md", "# Gate Rules")

            result = self.run_cli_with_args(
                [
                    str(broken_dir),
                    "--target",
                    str(valid_dir),
                    "--output-dir",
                    str(output_dir),
                ]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads((output_dir / "skill-review-report.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["skill_name"], "skill-reviewer")
            self.assertEqual(payload["gate_summary"]["overall_status"], "pass")

    def test_strict_mode_returns_exit_code_two_on_blocker_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skill-reviewer"
            output_dir = Path(tmp) / "reports"
            self.write_file(
                skill_dir / "SKILL.md",
                """
                ---
                name: wrong-reviewer-name
                description: Review skill packages.
                ---
                """,
            )

            result = self.run_cli_with_args(
                [str(skill_dir), "--strict", "--output-dir", str(output_dir)]
            )
            self.assertEqual(result.returncode, 2)
            self.assertTrue((output_dir / "skill-review-report.json").exists())


if __name__ == "__main__":
    unittest.main()
