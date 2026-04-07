# Skill Reviewer Principles

## Purpose
These principles explain what high-quality agent skills tend to have in common.
They guide scoring and rewrite advice, but they do not automatically act as hard gate failures.

## P-01 Audience Fit
- Write for the agent, not for a human reader.
- Prefer imperative instructions over background-heavy prose.
- Remove fluff that does not help the agent decide or act.
- Treat README-style marketing copy as repository documentation, not skill body content.

## P-02 Trigger Clarity
- Put the core "what this does" and "when to use it" logic in `description`.
- Do not rely on the body to carry the only activation clues.
- Favor concrete trigger words over vague summaries like "helps with coding".

## P-03 Progressive Disclosure
- Keep metadata lightweight because it is always visible.
- Keep `SKILL.md` focused on execution logic once the skill activates.
- Move long references, templates, and detailed guidance into `references/` and `assets/`.

## P-04 Freedom Calibration
- Creative tasks can tolerate broader instructions.
- Fragile tasks need tighter guardrails.
- If a task breaks when one field, token, or character changes, the skill should reduce freedom through templates, scripts, or validation.

## P-05 Execution Efficiency
- Use scripts for deterministic work that is awkward to encode in natural language.
- Keep repeated validation logic out of the main prompt when the result can be checked mechanically.
- Prefer "execute the check" over "describe the check" for reliable automation.

## Mapping To The Reviewer
| Principle | Primary role |
| --- | --- |
| `P-01` | Scoring, advice |
| `P-02` | Gate, scoring, advice |
| `P-03` | Scoring, structure checks |
| `P-04` | Scoring, advice |
| `P-05` | Scoring, automation hints |

## Legacy Notes Migrated From `references.md`
The original root-level `references.md` is merged here to avoid split sources.
The table below preserves the previous wording so historical context is not lost.

| Principle | Legacy statement | Legacy quote sample | Source status |
| --- | --- | --- | --- |
| P-01 Audience Fit | Remove human-centric fluff and keep instructions concise for agents. | "Default assumption: Codex is already very smart." | Needs explicit source links |
| P-02 Trigger Clarity | Put when-to-use conditions in frontmatter description, not body-only logic. | "Primary triggering mechanism for your skill." | Needs explicit source links |
| P-03 Progressive Disclosure | Keep metadata light and move long material to `references/` resources. | "Three-level loading system..." | Needs explicit source links |
| P-04 Freedom Calibration | Use lower freedom for brittle tasks and higher freedom for creative tasks. | "Narrow bridge needs guardrails..." | Needs explicit source links |
| P-05 Execution Efficiency | Use scripts to isolate deterministic and repeated validation logic. | "Scripts can run without reading all internals." | Needs explicit source links |

### Legacy summary
The original summary remains valid: design skills to spend fewer tokens on context,
put constraints at the right layer, and maximize reliable execution under clear boundaries.
