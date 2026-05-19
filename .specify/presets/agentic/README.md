# Agentic Workflow Preset

A companion preset for the [agentic-workflow extension](../extensions/agentic-workflow/).

## What It Does

Enriches Spec Kit's core templates with sections that connect per-feature artifacts to the project-level knowledge in `docs/`. Uses the `append` strategy so core template content is preserved -- the preset adds sections, it never replaces them.

## Template Additions

| Template       | What's Added                                              |
| -------------- | --------------------------------------------------------- |
| spec-template  | TTL metadata, project context checks, quality gate rubric |
| plan-template  | TTL metadata, project context, ADR capture reminder       |
| tasks-template | Post-implementation review checklist                      |
| constitution   | AGENTS.md layering reference, docs/ scheme overview       |

## Installation

```bash
specify preset add --dev ./presets/agentic-preset
```

## Usage

After installation, every `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, and `/speckit.constitution` command will include the appended sections automatically. No configuration needed.

## Requires

- Spec Kit >= 0.6.0
- The agentic-workflow extension (for the commands referenced in checklists)
- A scaffolded `docs/` tree (run `/speckit.agentic.scaffold` first)
