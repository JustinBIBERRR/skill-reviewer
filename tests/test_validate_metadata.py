import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_metadata.py"


class ValidateMetadataCliTests(unittest.TestCase):
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

    def test_reports_valid_skill_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skill-reviewer"
            skill_dir.mkdir()
            self.write_skill(
                skill_dir,
                """
                ---
                name: skill-reviewer
                description: Review complete agent skill packages and explain when to use them for audits and improvement requests.
                ---

                # Skill Reviewer
                """,
            )

            result = self.run_cli(skill_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["summary"]["skill_name"], "skill-reviewer")
            self.assertEqual(payload["summary"]["directory_name"], "skill-reviewer")

    def test_fails_when_description_lacks_trigger_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skill-reviewer"
            skill_dir.mkdir()
            self.write_skill(
                skill_dir,
                """
                ---
                name: skill-reviewer
                description: Review skill packages.
                ---

                # Skill Reviewer
                """,
            )

            result = self.run_cli(skill_dir)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            issues = {issue["rule_id"]: issue for issue in payload["issues"]}
            self.assertIn("GATE-META-005", issues)

    def test_fails_when_name_does_not_match_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skill-reviewer"
            skill_dir.mkdir()
            self.write_skill(
                skill_dir,
                """
                ---
                name: wrong-reviewer-name
                description: Review skill packages when users ask for a review or score.
                ---

                # Skill Reviewer
                """,
            )

            result = self.run_cli(skill_dir)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            issues = {issue["rule_id"]: issue for issue in payload["issues"]}
            self.assertIn("GATE-META-003", issues)

    def test_passes_non_review_action_when_trigger_is_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "find-skills"
            skill_dir.mkdir()
            self.write_skill(
                skill_dir,
                """
                ---
                name: find-skills
                description: Helps users discover and install agent skills when the user is looking for functionality that might exist as an installable skill.
                ---

                # Find Skills
                """,
            )

            result = self.run_cli(skill_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "pass")


if __name__ == "__main__":
    unittest.main()
