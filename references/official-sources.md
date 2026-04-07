# Official Sources

## Source priority
1. `official`: Anthropic product docs and Help Center
2. `standard`: Agent Skills open specification
3. `example`: Anthropic official example repository
4. `best_practice`: synthesized guidance derived from multiple trusted sources
5. `heuristic`: reviewer judgment

## Official
### Anthropic Help Center: What are Skills?
- URL: <https://support.anthropic.com/en/articles/12512176-what-are-skills>
- Use for:
  - what skills are
  - progressive disclosure
  - role of instructions, scripts, and resources

### Anthropic Help Center: How to create custom Skills
- URL: <https://support.anthropic.com/en/articles/12512198-how-to-create-custom-skills>
- Use for:
  - required metadata
  - directory packaging expectations
  - best practices around focus, clarity, examples, testing, and safety

## Standard
### Agent Skills Specification
- URL: <https://agentskills.io/specification>
- Use for:
  - `SKILL.md` format
  - required fields
  - naming constraints
  - directory structure
  - file references

## Example
### Anthropic example skills repository
- URL: <https://github.com/anthropics/skills>
- Use for:
  - repository README style
  - real-world skill package patterns
  - examples of scripts, references, and packaged assets

## Usage rules
- Only `official` and `standard` sources may independently justify a gate failure.
- `example` sources can strengthen a recommendation but cannot create a hard blocker by themselves.
- `best_practice` and `heuristic` sources must be labeled as advisory.
