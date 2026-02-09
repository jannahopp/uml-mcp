---
name: sequential-thinking
description: Step-by-step and reflective problem-solving for complex or multi-step tasks. Use when tackling complex tasks, planning, design, analysis that may need revision, unclear scope, or when the user asks for step-by-step reasoning. When the sequential-thinking MCP tool is available, use it for hard problems; otherwise apply the same principles in plain reasoning.
---

# Sequential Thinking

Break down complex work into ordered steps, revise when needed, and produce one clear answer. Use for multi-step tasks, planning, and problems where scope or approach may change.

## When to Use

- Complex or multi-step tasks
- Planning and design with room for revision
- Analysis that might need course correction
- Problems where the full scope is unclear at the start
- Tasks that need context carried across steps
- When irrelevant information must be filtered out
- When the user asks for step-by-step reasoning

## Behavior Without the MCP Tool

1. Break the task into ordered steps.
2. State one step at a time; build on the previous step.
3. Revise earlier steps when you discover they are wrong or incomplete.
4. Branch or backtrack when exploring alternatives.
5. Generate a solution hypothesis when appropriate; verify it against the steps.
6. Repeat until satisfied, then give a single, clear final answer.

Principles: Start with an estimate of how many steps you need and adjust as you go. Express uncertainty. Ignore information that is irrelevant to the current step.

## Using the Sequential Thinking MCP Tool

When the **sequentialthinking** MCP tool is enabled (e.g. user-sequential-thinking server), prefer calling it for hard problems so thoughts are tracked and revisable.

- **Required every call**: `thought` (current step), `thoughtNumber`, `totalThoughts`, `nextThoughtNeeded`.
- Start with an initial estimate of `totalThoughts`; increase or decrease as you progress.
- Set `nextThoughtNeeded: true` until you are done; set `nextThoughtNeeded: false` only when you have a satisfactory final answer.
- **Revisions**: Set `isRevision: true` and `revisesThought` to the thought number you are reconsidering.
- **Branches**: Use `branchFromThought` (thought number) and `branchId` (e.g. "alt-1") when exploring a different path.
- **More thoughts later**: Set `needsMoreThoughts: true` when you reach what seemed like the end but realize you need more steps.

Use the tool to generate a hypothesis, verify it against the chain of thought, and repeat until satisfied before returning one correct answer.

## Principles (With or Without Tool)

- Start with an estimate of steps; adjust freely.
- Revise or add steps at any time.
- Express uncertainty when present.
- Ignore irrelevant information for the current step.
- Hypothesize and verify when useful.
- End with a single, clear answer when satisfied.
