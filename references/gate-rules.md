# Gate Rules

## Purpose
This file defines minimum admission rules for `skill-reviewer`.
Every failing gate must map to an `official` or `standard` source.

## Rule format
- `rule_id`: stable identifier used in reports and JSON output
- `source_level`: `official` or `standard`
- `check_method`: `machine`, `model`, or `machine+model`
- `severity`: `blocker` or `major`

## Rules

### GATE-META-001
- Title: Skill root must contain `SKILL.md`
- Source level: `standard`
- Source: Agent Skills Specification
- Check method: `machine`
- Severity: `blocker`
- Pass condition: the package root contains `SKILL.md`
- Fail condition: `SKILL.md` is missing

### GATE-META-002
- Title: `SKILL.md` must contain valid frontmatter
- Source level: `standard`
- Source: Agent Skills Specification
- Check method: `machine`
- Severity: `blocker`
- Pass condition: the file starts with parseable YAML-style frontmatter
- Fail condition: frontmatter is missing or malformed

### GATE-META-003
- Title: `name` must exist and match skill naming rules
- Source level: `official` + `standard`
- Source:
  - Anthropic Help Center: How to create custom Skills
  - Agent Skills Specification
- Check method: `machine`
- Severity: `blocker`
- Pass condition:
  - `name` exists
  - `name` uses lowercase letters, numbers, and hyphens
  - `name` matches the skill directory name
- Fail condition:
  - `name` is missing
  - `name` is malformed
  - `name` does not match the directory

### GATE-META-004
- Title: `description` must exist
- Source level: `official` + `standard`
- Source:
  - Anthropic Help Center: How to create custom Skills
  - Agent Skills Specification
- Check method: `machine`
- Severity: `blocker`
- Pass condition: `description` is non-empty
- Fail condition: `description` is missing or blank

### GATE-META-005
- Title: `description` must explain both function and trigger
- Source level: `official` + `standard`
- Source:
  - Anthropic Help Center: How to create custom Skills
  - Agent Skills Specification
- Check method: `machine+model`
- Severity: `blocker`
- Pass condition:
  - the description explains what the skill does
  - the description explains when to use it
- Fail condition:
  - the description only states purpose
  - the description is vague and lacks trigger language

### GATE-REF-001
- Title: referenced relative files must exist
- Source level: `standard`
- Source: Agent Skills Specification
- Check method: `machine`
- Severity: `major`
- Pass condition: every relative file reference used in `SKILL.md` resolves successfully
- Fail condition: one or more referenced files do not exist

### GATE-STRUCT-001
- Title: package structure must remain parseable
- Source level: `standard`
- Source: Agent Skills Specification
- Check method: `machine`
- Severity: `major`
- Pass condition:
  - package root is intact
  - core references are reachable
  - report assets are reachable if referenced
- Fail condition:
  - broken package structure prevents reliable review

### GATE-SEC-001
- Title: skill package must not hardcode obvious secrets
- Source level: `official`
- Source: Anthropic Help Center: How to create custom Skills
- Check method: `model`
- Severity: `blocker`
- Pass condition: no obvious API keys, passwords, or tokens are embedded
- Fail condition: secrets or credentials are hardcoded into the package
