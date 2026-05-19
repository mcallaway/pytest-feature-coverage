---
description: Create or refresh a feature-to-code mapping in docs/design/codebase-map.md
---

# Codebase Map

Create or refresh `docs/design/codebase-map.md` — a feature-to-code mapping that helps both humans and agents navigate the project.

## User Input

$ARGUMENTS

## Purpose

As a project grows, knowing where things live becomes increasingly valuable. The codebase map provides a high-level directory overview and maps features, use cases, and concepts to their code locations. This is especially useful for agents that need to understand the project before making changes.

## Steps

### Step 1: Survey the project

Examine the project structure:

1. Top-level directory layout
1. Source code organization (src/, lib/, packages/, etc.)
1. Test organization (tests/, __tests__/, spec/, etc.)
1. Configuration files
1. Documentation structure

### Step 2: Identify features and concepts

From available documentation:

1. Read `docs/features/` for defined features
1. Read `.specify/specs/` for Spec Kit feature specs
1. Read `docs/design/` for documented concepts
1. Examine source code for module boundaries and key abstractions

### Step 3: Build the map

Create or update `docs/design/codebase-map.md`:

````markdown
# Codebase Map

Last updated: [date]

## Directory Overview

```text
[project root tree, 2-3 levels deep, annotated]
```

## Source Packages

| Package/Module | Purpose        | Key Files         |
| -------------- | -------------- | ----------------- |
| [name]         | [what it does] | [important files] |

## Feature-to-Code Mapping

| Feature        | Primary Code | Tests        | Design Doc        |
| -------------- | ------------ | ------------ | ----------------- |
| [feature name] | [code paths] | [test paths] | [design doc link] |

## Boundaries

Key architectural boundaries and their enforcement:

- [boundary description] — [how it's enforced]

## Entry Points

- CLI: [entry point]
- API: [entry point]
- Tests: [how to run]

````

### Step 4: Handle early-stage projects

If the project is primarily documentation (docs-first, pre-implementation):

- Map documented concepts to planned code locations
- Note which mappings are planned vs implemented
- Focus on the documentation structure itself

### Step 5: Report changes

If updating an existing map, report what changed:

- New entries added
- Stale entries removed or updated
- Structural changes

## Notes

- The codebase map is a design document — it should describe current reality, not aspirations
- Keep it high-level. Detailed API docs belong elsewhere.
- Update the map whenever significant code reorganization occurs
- This map is referenced by `/speckit.agentic.start-work` for context loading
