# Scoring Rubric

## Purpose
This file defines the quality score after gate checks finish.
The rubric measures how strong a skill package is, not just whether it is minimally valid.

## Scale
- Total score: 100
- Five dimensions
- 20 points per dimension

## S-01 Task Focus
### High score
- The skill targets one clear, repeatable workflow.
- The task boundary is easy to understand.
- The skill avoids unrelated responsibilities.

### Low score
- The skill tries to do too many unrelated jobs.
- The activation scope is vague or unstable.
- Success criteria are unclear.

## S-02 Trigger Clarity
### High score
- The description clearly states what the skill does.
- The description clearly states when to use it.
- Trigger words and boundaries are concrete.

### Low score
- The description is generic.
- Critical trigger details only appear in the body.
- It is hard to tell when the skill should activate.

## S-03 Execution Quality
### High score
- Instructions are concrete and imperative.
- The sequence is easy to follow.
- Inputs, outputs, and decision points are clear.

### Low score
- Instructions are mostly abstract commentary.
- The skill uses vague style goals instead of actions.
- A reviewer cannot easily tell how the agent should proceed.

## S-04 Resource Organization
### High score
- `SKILL.md` stays focused on activation-time instructions.
- Long references move into `references/`.
- Templates and schemas live in `assets/`.
- Related checks are automated when practical.

### Low score
- The skill overloads the main file with long reference material.
- Resources exist but have unclear roles.
- File references are inconsistent or hard to follow.

## S-05 Failure Defense
### High score
- The skill identifies brittle tasks and reduces freedom.
- Deterministic checks use scripts or templates where appropriate.
- The skill describes what to do when evidence is missing or ambiguous.

### Low score
- Strict output requirements rely only on prompt wording.
- The package lacks fallback or validation strategy.
- Advice and gate logic are mixed without clear safety boundaries.
