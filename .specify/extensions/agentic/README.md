# Agentic Development Workflow — Spec Kit Extension

A Spec Kit extension that adds TTL-aware project memory, rubric-driven quality gates, and lifecycle commands for building durable shared understanding across sessions.

## What This Adds to Spec Kit

Spec Kit manages **per-feature** lifecycle artifacts (spec → plan → tasks → implement) under `.specify/specs/`. This extension adds the **project-level knowledge layer** that persists across features:

| Artifact          | Purpose                               | TTL       |
| ----------------- | ------------------------------------- | --------- |
| `docs/features/`  | User stories with acceptance criteria | medium    |
| `docs/plans/`     | Roadmap dashboard + plan rubric       | short     |
| `docs/decisions/` | Architecture Decision Records         | immutable |
| `docs/design/`    | System as it currently is             | long      |
| `docs/guides/`    | How to use the system                 | long      |
| `docs/notes.md`   | Scratch pad                           | short     |

Each folder includes a `README.md` (format, TTL, authors, audience) and a `RUBRIC.md` (evaluative criteria for quality).

## Commands

### Project Setup

| Command                     | Description                                                 |
| --------------------------- | ----------------------------------------------------------- |
| `/speckit.agentic.scaffold` | Create the docs/ tree, rubrics, and layered AGENTS.md files |

### Session Lifecycle

| Command                       | Description                       |
| ----------------------------- | --------------------------------- |
| `/speckit.agentic.start-work` | Load context for a coding session |

### Review and Quality

| Command                             | Description                                           |
| ----------------------------------- | ----------------------------------------------------- |
| `/speckit.agentic.code-review`      | Post-implementation code review                       |
| `/speckit.agentic.review-pr`        | Comprehensive pre-merge PR review                     |
| `/speckit.agentic.review-alignment` | Detect drift between code and design docs             |
| `/speckit.agentic.apply-rubric`     | Apply a rubric for deterministic pass/fail evaluation |

### Knowledge Capture

| Command                               | Description                                        |
| ------------------------------------- | -------------------------------------------------- |
| `/speckit.agentic.close-plan`         | Pre-merge finalization — close plan, finalize ADRs |
| `/speckit.agentic.document-decisions` | Capture trade-offs as ADR drafts                   |
| `/speckit.agentic.extract-lessons`    | Promote patterns from commits to durable docs      |
| `/speckit.agentic.codebase-map`       | Create/refresh feature-to-code mapping             |

### Onboarding

| Command                    | Description                                      |
| -------------------------- | ------------------------------------------------ |
| `/speckit.agentic.onboard` | Interactive project onboarding for new engineers |

## Installation

**Prerequisites**: `specify-cli` installed, an AI agent with slash command support.

### Development (local)

```bash
specify extension add --dev /path/to/this/extension
```

### From GitHub (after publishing)

```bash
specify extension add agentic
```

## Quick Start

```bash
# 1. Install the extension
specify extension add --dev /path/to/extensions/agentic-workflow

# 2. Scaffold the docs tree and AGENTS.md files
# (in your AI agent)
/speckit.agentic.scaffold

# 3. Start a session
/speckit.agentic.start-work

# 4. After implementing, review
/speckit.agentic.code-review

# 5. Before merging
/speckit.agentic.review-pr
/speckit.agentic.close-plan
```

## How It Complements Spec Kit

```text
Spec Kit Core                    This Extension
─────────────                    ──────────────
/speckit.constitution     ←→     AGENTS.md (guiding principles)
/speckit.specify          ←→     docs/features/ (project-level features)
/speckit.plan             ←→     docs/plans/README.md (roadmap dashboard)
                                 docs/plans/RUBRIC.md (after_plan hook)
/speckit.tasks                   [no overlap]
/speckit.implement        →      /speckit.agentic.code-review (after)
                                 /speckit.agentic.review-alignment
                                 /speckit.agentic.close-plan
                                 /speckit.agentic.document-decisions
                                 /speckit.agentic.extract-lessons
                                 /speckit.agentic.codebase-map
                                 /speckit.agentic.onboard
```

## Philosophy

Three guiding principles from the agentic development pattern:

1. **Honest Technical Judgment Over Politeness** — push back, say "I don't know"
1. **Investigate Before Acting** — stop and ask when multiple valid approaches exist
1. **Strive For Durable Shared Understanding** — make knowledge persist across sessions

## Companion Preset

A companion preset at [`presets/agentic-preset/`](../../presets/agentic-preset/) enriches Spec Kit's core templates (spec, plan, tasks, constitution) with TTL metadata, rubric references, and decision capture prompts. Install it alongside the extension for the full experience:

```bash
specify preset add --dev /path/to/presets/agentic-preset
```

## License

MIT
