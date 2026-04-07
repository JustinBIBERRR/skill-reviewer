# Evidence Policy

## Purpose
This file tells `skill-reviewer` how to justify findings.
Evidence must be explicit before a report claims that a package passes, fails, or needs changes.

## Evidence levels
### `official`
- Anthropic docs and Help Center content
- May justify gate failures

### `standard`
- Agent Skills open specification
- May justify gate failures

### `example`
- Anthropic example repositories and published patterns
- Supports scoring and advice, but cannot independently block

### `best_practice`
- Stable guidance synthesized from multiple trusted sources
- Supports scoring and advice only

### `heuristic`
- Reviewer judgment or contextual inference
- Advisory only

## Hard rules
1. Every gate failure must cite at least one `official` or `standard` source.
2. `example`, `best_practice`, and `heuristic` evidence cannot independently create a blocker.
3. High-risk score deductions should cite evidence whenever possible.
4. If a recommendation is not an official requirement, label it clearly as advice.
5. If sources conflict, prefer `official` over `standard`, and document the conflict in the report.

## Reporting requirements
- Gate findings must include:
  - `rule_id`
  - `source_level`
  - `source_title`
  - `source_url`
  - `source_quote`
- Score deductions should include:
  - dimension id
  - evidence level
  - short rationale
- Advice should include:
  - recommendation
  - evidence level
  - whether it is mandatory or optional
