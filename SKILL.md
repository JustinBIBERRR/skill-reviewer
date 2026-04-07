---
name: skill-reviewer
description: Review complete AI agent skill packages when users ask to review, score, audit, or improve a skill. Use for local skill directories that need gate checks, quality scoring, evidence-backed findings, and actionable rewrite advice.
---

# Skill Reviewer

## Goal
Review a target skill package with a two-layer model:
1. Gate checks for minimum package validity
2. Quality scoring for maintainability, trigger clarity, execution quality, resource design, and failure defense

## Review Scope
Default to the full package, not only `SKILL.md`:
- `SKILL.md`
- `README.md`
- `references/`
- `assets/`
- `scripts/`
- `evals/` when present

If the user only provides part of a skill, keep reviewing but explicitly state the coverage limitation in the report.

## Source Of Truth
Use these files in order:
- [official sources](references/official-sources.md)
- [gate rules](references/gate-rules.md)
- [scoring rubric](references/scoring-rubric.md)
- [evidence policy](references/evidence-policy.md)
- [principles](references/principles.md)

Use these runtime helpers when useful:
- [inspect package](scripts/inspect_package.py)
- [validate metadata](scripts/validate_metadata.py)
- [check references](scripts/check_references.py)
- [run skill review](scripts/run_skill_review.py)

Use these output contracts:
- [report template](assets/report-template.md)
- [report schema](assets/report-schema.json)

## Required Workflow
Execute the review in this order:

1. Identify the target skill directory and report the review scope.
2. Inventory the package structure.
3. Run metadata validation.
4. Run file reference validation.
5. Apply gate rules from [gate rules](references/gate-rules.md).
6. Score the package with [scoring rubric](references/scoring-rubric.md).
7. Justify findings with [evidence policy](references/evidence-policy.md).
8. Use [principles](references/principles.md) for rewrite and improvement guidance.
9. Produce both:
   - a human-readable Markdown report
   - a structured JSON result aligned to [report schema](assets/report-schema.json)

## Output Requirements
Every final review must include:
- review scope
- gate summary
- total score and dimension scores
- high-risk findings
- evidence log with source level
- actionable fixes

If a recommendation is not a hard requirement, label it as advice instead of presenting it as a blocker.

## Guardrails
- Do not invent sources.
- Do not present community or heuristic guidance as Anthropic official requirements.
- Do not skip evidence on gate failures.
- Do not hide missing inputs; declare review coverage limits clearly.
- Keep the product name consistent as `skill-reviewer` in all user-facing output.
