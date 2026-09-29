---
description: Interactive project onboarding — walk a new engineer through the codebase
---

# Onboard

Interactive onboarding guide for a new engineer (human or agent) joining the project.

## User Input

$ARGUMENTS

## Purpose

Walk a newcomer through the project structure, architecture, conventions, and current state. This is interactive — pause for questions and adapt based on the person's background and interests.

## Steps

### Step 1: Orientation

Start with the big picture:

1. **What is this project?** Read the project README and summarize in 2-3 sentences.
1. **Where are we?** Current state — what's been built, what's in progress.
1. **How do we work?** Point to AGENTS.md and the development workflow.

Pause: "What's your background? Anything specific you want to understand?"

### Step 2: Architecture and Design

1. Read `docs/design/` and summarize the system architecture
1. If `docs/design/codebase-map.md` exists, walk through the feature-to-code mapping
1. Highlight key abstractions and boundaries
1. Point out design docs for deeper reading

Pause: "Any questions about the architecture?"

### Step 3: Code Neighborhoods

Walk through the main code areas:

1. **Source structure**: What lives where — point to the primary source directories (`src/`, `lib/`, `packages/`, or equivalent for this project's language)
1. **Key modules**: The 3-5 most important modules and what they do
1. **Testing**: How tests are organized, how to run them
1. **Configuration**: Key config files and what they control

Pause: "Want to dive deeper into any area?"

### Step 4: Development Workflow

1. How to set up the development environment
1. How work flows: feature spec → plan → tasks → implement → review → merge
1. Key commands: Spec Kit slash commands + extension commands
1. Conventions: AGENTS.md principles, testing rules, documentation expectations

### Step 5: Current State

1. Active plans in `docs/plans/README.md`
1. Recent decisions in `docs/decisions/`
1. Open features or specs
1. Any known issues or areas of concern

### Step 6: First Steps

Suggest concrete first tasks based on the person's interests:

- "If you want to understand the code better, try [X]"
- "If you want to contribute immediately, [active plan] has [task]"
- "If you want to improve docs, [area] needs attention"

## Notes

- This is interactive by design. Don't dump everything at once.
- Adapt depth based on the person's questions and background.
- If the project is new/small, some sections will be brief — that's fine.
- For agent onboarding, the pauses become natural section breaks rather than literal questions.
