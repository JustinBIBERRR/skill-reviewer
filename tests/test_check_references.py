import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_references.py"


class CheckReferencesCliTests(unittest.TestCase):
    def run_cli(self, skill_dir: Path):
        result = subprocess.run(
            ["py", str(SCRIPT), str(skill_dir)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        return result

    def write_skill(self, skill_dir: Path, body: str) -> None:
        (skill_dir / "SKILL.md").write_text(textwrap.dedent(body).strip() + "\n", encoding="utf-8")

    def test_passes_when_all_referenced_files_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skill-reviewer"
            refs_dir = skill_dir / "references"
            assets_dir = skill_dir / "assets"
            refs_dir.mkdir(parents=True)
            assets_dir.mkdir(parents=True)
            (refs_dir / "gate-rules.md").write_text("# Gate Rules\n", encoding="utf-8")
            (assets_dir / "report-template.md").write_text("# Report Template\n", encoding="utf-8")
            self.write_skill(
                skill_dir,
                """
                ---
                name: skill-reviewer
                description: Review skill packages when users ask to review or score a skill.
                ---

                See [gate rules](references/gate-rules.md).
                Use the template at [report template](assets/report-template.md).
                """,
            )

            result = self.run_cli(skill_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["summary"]["checked_references"], 2)

    def test_fails_when_markdown_reference_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skill-reviewer"
            skill_dir.mkdir(parents=True)
            self.write_skill(
                skill_dir,
                """
                ---
                name: skill-reviewer
                description: Review skill packages when users ask to review or score a skill.
                ---

                See [gate rules](references/gate-rules.md).
                """,
            )

            result = self.run_cli(skill_dir)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            issues = {issue["rule_id"]: issue for issue in payload["issues"]}
            self.assertIn("GATE-REF-001", issues)


if __name__ == "__main__":
    unittest.main()
