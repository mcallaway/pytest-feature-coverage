---
name: speckit-agentic-scaffold
description: Create the TTL-aware docs/ tree with READMEs, rubrics, and layered AGENTS.md
  files
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: bayer-int
  source: extension:agentic
---

# Agentic Scaffold Skill

# Scaffold Agentic Development Structure

Set up the project-level documentation tree and layered instruction files that complement Spec Kit's per-feature artifacts (`specs/NNN/` by default, or `.specify/specs/NNN/` for repos still on the legacy location).

## User Input

$ARGUMENTS

## Purpose

Spec Kit manages per-feature lifecycle artifacts (spec, plan, tasks) under `specs/NNN/` (the current default; some repos still have existing features at the legacy `.specify/specs/NNN/` location). This command creates the **project-level knowledge layer** that persists across features — design documents, architectural decisions, guides, and plans that accumulate over the life of the project.

Every folder has explicit metadata: purpose, TTL (time-to-live), intended authors, and intended audience. This metadata helps both humans and agents understand when to create, update, and retire documents.

## Steps

### Step 1: Create the docs/ tree

Create the following directory structure at the project root. If any directory already exists, skip it. If a file already exists, do NOT overwrite it.

```text
docs/
├── README.md
├── notes.md
├── features/
│   ├── README.md
│   └── RUBRIC.md
├── plans/
│   ├── README.md
│   └── RUBRIC.md
├── decisions/
│   ├── README.md
│   └── RUBRIC.md
├── design/
│   ├── README.md
│   ├── RUBRIC.md
│   └── 001-agentic-development-pattern.md
└── guides/
    ├── README.md
    └── 001-agentic-development-workflow.md
```

### Step 2: Write docs/README.md

````markdown
# Documentation

- **Purpose**: Entry point and orientation for all project documentation.
- **TTL**: long -- updated when folders are added, removed, or repurposed.
- **Author(s)**: Anyone maintaining the docs tree.
- **Audience(s)**: New humans and agents orienting to the project; readers navigating between folders.

## Folders

| Folder        | What lives here                          | TTL       |
|---------------|------------------------------------------|-----------|
| `features/`   | User stories with acceptance criteria    | long      |
| `plans/`      | Roadmap dashboard + plan rubric          | short     |
| `decisions/`  | ADRs (immutable once accepted)           | immutable |
| `design/`     | The system as it currently is            | long      |
| `guides/`     | How to use the system                    | long      |
| `notes.md`    | Scratch pad (pruned aggressively)        | short     |

## Relationships

```text
features/ (what) --drives--> plans/ (work) --produces--> decisions/ (why)
    |                                                          |
    +<-------------------design/ (how)<------------------------+
```

- **features/** define capabilities the system must provide
- **design/** describes how those capabilities are implemented
- **plans/** durable project-level plan entries, paired with `specs/NNN/` implementation plans via cross-reference; dashboard indexing them; rubric for plan quality
- **decisions/** record trade-offs encountered during implementation
- **guides/** explain how to use the system for humans and agents

````

### Step 3: Write docs/notes.md

```markdown
# Notes

Freeform scratch for half-baked ideas, observations, and things to revisit.
Keep this short and current. Items should be acted on (promoted to a feature,
plan, decision, design doc, or guide) or pruned.

<!-- Add notes below -->
```

### Step 4: Write docs/features/README.md

```markdown
# Feature Specifications

- **Purpose**: User stories that describe what the system does, with acceptance criteria for verifying it works. Feature docs are the stable reference for what the system promises; distinct from design (HOW) and decisions (WHY).
- **TTL**: long -- stable reference for what the system promises; updated when features are added, changed, or deprecated.
- **Author(s)**: Humans (often with an agent) when an idea is taking shape; revised as scope clarifies.
- **Audience(s)**: Agents picking up implementation work; humans planning iterations; reviewers checking that built code matches the promised behavior.

See `RUBRIC.md` in this folder for the criteria a feature spec must meet.

## Feature Document Format

Every feature document should include:

- **Title and summary** with status (Pending or Implemented)
- **User Story** in "As a..., I want to..., so that..." format
- **Dependencies** on other features
- **Acceptance Criteria** that are concrete and verifiable
- **Notes** for additional context, constraints, or open questions

## Index

<!-- Add feature entries here as they are created -->
```

### Step 5: Write docs/features/RUBRIC.md

```markdown
# Feature Document Rubric

A rubric for evaluating feature documents after they are written. Apply this at authoring time and at review time when assessing whether acceptance criteria are ready to drive implementation.

## User Story

### All three parts are present and distinct

The story has a who ("As a..."), a what ("I want to..."), and a value clause ("so that..."). The value clause states why the capability matters, not a restatement of the capability itself.

- Weak: "so that I can create notes" (same as the "I want")
- Strong: "so that I spend time thinking, not wrestling with file paths and frontmatter"

### The persona is the right level of specificity

"As a knowledge worker" is appropriate when the feature serves any user. A more specific persona is appropriate when the audience is narrowed by design. Avoid overly vague personas ("as a user") that carry no signal.

## Acceptance Criteria

### Each criterion is independently falsifiable

A criterion that can be evaluated on its own, with a clear pass or fail.

### Criteria describe user-observable behavior

The criterion states what the user or caller observes -- a command, output, exit code, file, message -- not what happens internally.

### Criteria are concrete enough to write a test from directly

A test author should be able to read a criterion and write a test without seeking clarification.

- Weak: "handles errors gracefully"
- Strong: "exit code is non-zero when any file fails validation; exit code is 0 when all files pass"

### Criteria are not implementation steps

Criteria describe what is true after the feature is working, not the steps taken to build it.

### Collective coverage matches the feature scope

Gaps between the description and the criteria are missing criteria.

### Edge cases and failure modes are represented

At least one criterion covers how the feature behaves when things go wrong.

## Signals that a feature doc should be revised

- A criterion uses "handles," "supports," or "manages" without specifying what the user observes
- The "so that" clause could be deleted without losing information
- Two or more criteria would always pass or fail together
- The criteria are all happy-path with no failure or edge cases
```

### Step 6: Write docs/plans/README.md

```markdown
# Plans — Project Roadmap

- **Purpose**: The story of the project's evolution. This folder holds durable, project-level plan
  entries (`NNN-slug.md`) alongside a roadmap dashboard (this file) that indexes them. Each
  project-level plan is paired -- via an explicit cross-reference, not necessarily matching numbers
  -- with the Spec Kit implementation-level plan it corresponds to (default location `specs/NNN/plan.md`).
  Not every implementation-level plan needs a paired project-level entry (small bugfixes may not
  warrant one); use judgment.
- **TTL**: short (updated each session that changes what's active).
- **Author(s)**: Updated every session that touches the active plan.
- **Audience(s)**: Fresh agent sessions resuming work; humans tracking progress.

See `RUBRIC.md` in this folder for criteria applied to both this dashboard and individual project
plans, via the `after_plan` hook.

## Current Focus

<!-- Link to the active docs/plans/NNN-slug.md entry here, cross-referenced to its specs/NNN/plan.md -->

None yet.

## Next Steps

<!-- Upcoming work -->

## Completed

<!-- Closed plans move here with a one-line summary -->
```

### Step 7: Write docs/plans/RUBRIC.md

```markdown
# Plan Rubric

Evaluative criteria for plan documents at both layers: project-level plans (`docs/plans/NNN.md`)
and Spec Kit's implementation-level plans (`specs/NNN/plan.md`). Applied automatically via the
`after_plan` hook (against whichever document `/speckit.plan` just created or updated), or manually
with `/speckit.agentic.apply-rubric`.

## Header

### Status/Created/Updated metadata is present

A `docs/plans/NNN.md` project-level plan states its Status (Active, Deferred, Completed, or
Proposed for a backlog entry created ahead of implementation), and when it was created/last updated.

## Phases

### Each phase has a concrete deliverable

The deliverable is something tangible (a file, an endpoint, a passing test suite), not an abstract goal.

### Phases can be completed or explicitly deferred

Every phase ends in a clear done/not-done state. Phases that cannot be completed in the current cycle are deferred, not left dangling.

### Phase order reflects genuine dependencies

Phase N+1 should depend on outputs from phase N. If phases are independent, they should be parallelizable, not sequenced.

## Scope Discipline

### Goals and non-goals are present

The plan states what is in scope and what is explicitly out of scope.

### Plan is sized to be resumable

A plan that requires more than a handful of sessions to complete should be broken into smaller plans.

## Traceability

### Links back to motivating feature or decision

The plan references the feature doc or decision that triggered the work.

### Cross-reference to the paired plan is present, when one is warranted

A `docs/plans/NNN.md` project-level plan links to its paired `specs/NNN/plan.md` implementation-level
plan, and vice versa, whenever such a pairing exists. **Exception**: a project-level plan in
`Proposed` status MUST NOT fail this criterion solely for lacking that cross-reference yet.

### Close-out criteria match deliverables

What counts as "done" aligns with what the phases produce.

## Signals that a plan should be revised

- A phase deliverable is stated as a process ("researching X") rather than an artifact
- Goals section is missing or only restates the title
- No feature or decision is referenced as motivation
- A non-`Proposed` project-level plan has no cross-reference to any implementation-level plan, and
  no stated reason why one does not (yet) apply
```

### Step 8: Write docs/decisions/README.md

```markdown
# Architecture Decision Records

- **Purpose**: Point-in-time records of hard-to-reverse decisions with context and rejected alternatives. Once accepted, the record is immutable (amend with a new ADR that supersedes).
- **TTL**: immutable -- the record never changes; the decision may be superseded.
- **Author(s)**: Humans (with agent assistance) when a trade-off is encountered during implementation.
- **Audience(s)**: Anyone understanding constraints; future agents picking up adjacent work; reviewers.

See `RUBRIC.md` in this folder for the criteria an ADR must meet.

## ADR Format

- **Title**: Short imperative statement (e.g., "Use SQLite for local storage")
- **Status**: Proposed | Accepted | Deprecated | Superseded by ADR-NNN
- **Date**: ISO 8601 (YYYY-MM-DD)
- **Context**: What prompted the decision
- **Decision**: What was decided (imperative mood)
- **Consequences**: Both positive and negative effects

## Index

<!-- Add ADR entries here as they are created -->
```

### Step 9: Write docs/decisions/RUBRIC.md

```markdown
# ADR Rubric

Evaluative criteria for architecture decision records.

## Worth Recording

### The decision is hard to reverse

If the decision is trivially changeable later, it may not need an ADR.

### Alternatives were genuinely considered

At least two alternatives were evaluated. Straw-man alternatives (included only to be rejected) weaken the record.

## Ages Well

### Context reads correctly months later

A reader unfamiliar with the project can understand why the decision was made from the context alone.

### Consequences are two-sided

Both benefits and drawbacks are listed. An ADR with only positive consequences is a sales pitch, not a record.

### Decision is stated imperatively and specifically

- Weak: "We should probably use a database"
- Strong: "Use PostgreSQL 16 for the primary data store"

## Stays Current

### Status reflects reality

An accepted ADR whose decision was later reversed should be marked Superseded with a link to the new ADR.

## Signals that an ADR should be revised

- Context section references "we" without explaining who or why
- Consequences section lists only benefits
- Decision uses hedging language ("might," "should consider")
- Status is Accepted but the decision is no longer followed
```

### Step 10: Write docs/design/README.md

```markdown
# Design Documents

- **Purpose**: The system as it currently is. Bridge between decisions (WHY) and code (WHAT). A stale design doc is a defect.
- **TTL**: long -- updated alongside code as the system evolves.
- **Author(s)**: Updated alongside code when design changes.
- **Audience(s)**: Agents understanding intent before changing implementation; humans onboarding.

See `RUBRIC.md` in this folder for the criteria a design doc must meet.

## Document Format

Each design document should include:

- **Title** -- what this document describes (a subsystem, a data model, a workflow)
- **Overview** -- one-paragraph summary of the component and its role in the system
- **Current Design** -- how it works today: key abstractions, data flow, relationships to other components
- **Interfaces** -- public API, configuration, or integration points that other components depend on
- **Constraints and Invariants** -- rules that must hold (e.g., "all writes go through the event bus")
- **See Also** -- links to related ADRs, feature docs, or other design docs

Diagrams (Mermaid preferred) are encouraged when they clarify relationships that prose alone would obscure.

## Organization

- **Conceptual**: Domain models, core abstractions, key relationships
- **Technical**: Architecture, data flow, infrastructure
- **Features**: UI workflows, integration points, user-facing behavior
```

### Step 11: Write docs/design/001-agentic-development-pattern.md

This is the methodology's foundational design document. It explains the driving ideas behind the pattern and how the four components (docs/ scheme, AGENTS.md, prompts, rubrics) derive from them.

````markdown
# The Agentic Development Pattern

A development pattern for projects where humans and AI agents share authorship of code, documentation, and decisions. It describes how layered instructions, a documentation scheme, focused prompts, and evaluative rubrics work together to keep authors and audiences aligned over time.

This pattern is portable. It can be implemented in any project repository regardless of language, framework, or domain.

## The Driving Ideas

Two observations shape every part of the pattern.

**Information has a time-to-live.** Some statements are meant to be true forever — a decision was made on a date, and these alternatives were rejected. Some are meant to be true until the system changes — the design as it currently stands. Some are meant to be true until the work completes — an in-flight plan. Some are meant to be true for the rest of an afternoon — a session note. Storing these the same way, in the same place, with the same review discipline, is what causes documentation to drift, conflict, and rot.

**Authors and audiences can each be a human or an agent, in the present or in the future.** A plan written today by a human-and-agent pair will be read tomorrow by a different agent in a fresh session. A design doc written today will be read months later by a human joining the project, or by an agent picking up an unrelated task. A decision recorded in a moment will be consulted years later by readers who were not there when the choice was made.

The pattern is what falls out of taking both seriously.

## How the Pattern Falls Out

```text
                    +------------------+
                    |   docs/ scheme   |
                    |  (project memory)|
                    +--------+---------+
                             |
                  reads from / writes to
                             |
    +------------------------+------------------------+
    |                        |                        |
+---v-----------+    +-------v-------+    +-----------v--------+
| AGENTS.md     |    | RUBRIC.md     |    |   Prompt library   |
| (prescriptive)|    | (evaluative)  |    | (review workflows) |
+---------------+    +---------------+    +--------------------+
```

Four components, each derivable from the driving ideas:

- The **`docs/` scheme** is project memory. Each folder holds a different kind of statement with a different lifetime, written by and for a different mix of authors and audiences.
- **AGENTS.md files** are long-lived prescriptive guidance for any agent working in a given area. They tell agents how to behave; they reference `docs/` for context.
- The **prompt library** (Spec Kit commands) carries the workflow from one kind of artifact to another. Each prompt knows where to read context and where to write findings.
- **RUBRIC.md files** are long-lived evaluative standards. Where AGENTS.md says how to do something, a rubric asks whether the result is actually good.

## Component 1: Documentation Scheme (Project Memory)

Folders differ from one another not by topic but by how long their contents are meant to stay true and by who is expected to read them later.

| Folder       | What it holds                    | TTL       | Key readers                      |
| ------------ | -------------------------------- | --------- | -------------------------------- |
| `features/`  | User stories, acceptance criteria | long      | Agents implementing; humans reviewing scope |
| `plans/`     | Roadmap dashboard + plan rubric  | short     | Fresh agent sessions resuming work |
| `decisions/` | ADRs (immutable once accepted)   | immutable | Future humans/agents understanding constraints |
| `design/`    | The system as it currently is    | long      | Agents before changing code; humans onboarding |
| `guides/`    | How to use the system            | long      | Both humans and agents needing workflows |
| `notes.md`   | Scratch pad                      | short     | Current session |

Individual per-feature implementation plans live in `specs/NNN/plan.md` (managed by Spec Kit;
`.specify/specs/NNN/plan.md` for repos still on the legacy location). Durable, project-level plan
entries live in `docs/plans/NNN-slug.md`, each cross-referenced to its paired implementation plan.
`docs/plans/README.md` is a dashboard that indexes active, upcoming, and completed project-level plans.

### The documentation cycle

```text
features/ (what) --drives--> plans/ (work) --produces--> decisions/ (why)
    |                                                          |
    +<-------------------design/ (how)<------------------------+
```

## Component 2: Layered Agent Instructions

AGENTS.md files answer a single question for any agent that opens the project: what is expected of me here?

```text
AGENTS.md                 # Project-wide conventions and principles
src/AGENTS.md             # Source code conventions (optional)
tests/AGENTS.md           # Testing conventions (optional)
docs/AGENTS.md            # Documentation conventions
```

The layering exists so each agent loads only the context relevant to its current task. Each layer adds to (never overrides) the layers above. Project-specific additions go in `AGENTS.local.md`.

## Component 3: Quality Rubrics

A rubric is an evaluative standard. AGENTS.md says how to do something; a rubric asks whether the result is actually good. The two are not redundant: an agent following every prescriptive rule can still produce work that fails on judgment, and a rubric is the explicit step that catches it.

Rubrics live alongside the area they evaluate:

```text
docs/features/RUBRIC.md   # What makes acceptance criteria good
docs/plans/RUBRIC.md       # What makes a plan good (applied via after_plan hook)
docs/decisions/RUBRIC.md   # What makes an ADR good
docs/design/RUBRIC.md      # What makes a design doc good
```

## Component 4: Commands

Commands carry the project from one kind of artifact to the next. They come from two sources: Spec Kit core (the SDD lifecycle) and the agentic-workflow extension (project memory and review).

### One-Time Setup

Run these once when setting up a new project:

| Command | What it does |
| ------- | ------------ |
| `specify init` | Initialize Spec Kit in the project |
| `specify extension add agentic` | Install the agentic-workflow extension |
| `specify preset add agentic` | Install the companion preset (optional) |
| `/speckit.constitution` | Create the project's guiding principles |
| `/speckit.agentic.scaffold` | Create the docs/ tree, AGENTS.md files, and rubrics |

### New Feature Development (Full Lifecycle)

Use the full sequence for any new capability that merits a specification:

| Step | Command | What it does |
| ---- | ------- | ------------ |
| 1 | `/speckit.specify` | Write a spec with user stories and acceptance criteria |
| 2 | `/speckit.clarify` | Refine ambiguous requirements (if needed) |
| 3 | `/speckit.plan` | Break the spec into phases with deliverables |
| 4 | `/speckit.tasks` | Generate dependency-ordered implementation tasks |
| 5 | `/speckit.agentic.start-work` | Load project context for implementation session |
| 6 | `/speckit.implement` | Execute the tasks |
| 7 | `/speckit.agentic.document-decisions` | Capture trade-offs as ADRs (as needed during 5-6) |
| 8 | `/speckit.agentic.review-alignment` | Check for drift between code and design docs |
| 9 | `/speckit.agentic.apply-rubric` | Evaluate changed artifacts against their rubric |
| 10 | `/speckit.agentic.code-review` | Review correctness, clarity, testing |
| 11 | `/speckit.agentic.extract-lessons` | Surface reusable patterns from recent work (optional) |
| 12 | `/speckit.agentic.close-plan` | Finalize docs, ADRs, plan status -- produces the final commit |
| 13 | `/speckit.agentic.review-pr` | Pre-merge PR checklist, run against that final commit |
| 14 | `/speckit.agentic.merge-pr` | Human-invoked: merge and sync local state -- terminal action, never auto-chained (ADR-011) |

### Small Bugfixes

Not every change needs a full spec. For well-understood bugs:

| Step | Command |
| ---- | ------- |
| 1 | `/speckit.agentic.start-work` |
| 2 | Fix the bug |
| 3 | `/speckit.agentic.code-review` |
| 4 | `/speckit.agentic.apply-rubric` |
| 5 | `/speckit.agentic.close-plan` (lightweight, if warranted) |
| 6 | `/speckit.agentic.review-pr` (if creating a PR) -- final check before you merge |
| 7 | `/speckit.agentic.merge-pr` (human-invoked, once ready) |

### Refactoring and Maintenance

For structural improvements, dependency updates, or architectural changes:

| Step | Command |
| ---- | ------- |
| 1 | `/speckit.agentic.start-work` |
| 2 | `/speckit.agentic.review-alignment` (understand current design first) |
| 3 | Make changes |
| 4 | `/speckit.agentic.document-decisions` (if trade-offs were made) |
| 5 | `/speckit.agentic.code-review` |

### Periodic and As-Needed

| Command | When to use |
| ------- | ----------- |
| `/speckit.agentic.extract-lessons` | After a feature lands or at milestones — surface patterns from recent work |
| `/speckit.agentic.codebase-map` | When the codebase map drifts or after significant structural changes |
| `/speckit.agentic.apply-rubric` | Any time — evaluate artifacts against their rubric |
| `/speckit.agentic.onboard` | New team member or agent; re-familiarization after time away |

### Where Commands Read and Write

| Command | Reads from | Writes to |
| ------- | ---------- | --------- |
| `/speckit.specify` | `docs/features/`, `docs/design/` | `specs/NNN/spec.md` |
| `/speckit.plan` | spec, `docs/plans/README.md` | `specs/NNN/plan.md`, paired `docs/plans/NNN.md` |
| `/speckit.implement` | plan, `docs/design/`, AGENTS.md | Source code |
| `start-work` | `docs/plans/README.md`, AGENTS.md | (context loading) |
| `document-decisions` | `docs/design/` | `docs/decisions/` (ADR drafts) |
| `code-review` | AGENTS.md, `docs/design/` | Review findings |
| `review-alignment` | `docs/design/`, codebase map | Drift findings |
| `close-plan` | `docs/plans/`, `docs/decisions/` | Finalized plan, ADRs, design updates |
| `extract-lessons` | Git history, `docs/` | Recommendations for promotion |
| `codebase-map` | Source code, `docs/design/` | `docs/design/codebase-map.md` |

## See Also

- [Agentic Development Workflow Guide](../guides/001-agentic-development-workflow.md) -- how to follow this pattern step by step
````

### Step 12: Write docs/design/RUBRIC.md

```markdown
# Design Document Rubric

Evaluative criteria for design documents.

## Cold-Start Readability

### A reader with no prior context can act on it

The document does not assume familiarity with prior conversations or sessions.

### States current truth, not history

Describes the system as-built, not the journey to get there. History belongs in ADRs.

### Diagrams carry their weight

Every diagram communicates something that prose alone would obscure. Decorative diagrams are noise.

## Correctness

### Matches code

Concepts, names, and relationships described in the design doc exist in the codebase.

### Concepts named in the doc exist in code

If the doc names a "Registry" class, a Registry exists in the source.

## Scope and Framing

### One concern per document

A design doc that covers both data modeling and deployment topology should be split.

### Links, not copies

When referencing information from another doc, link to it. Duplicated content drifts.

## Signals that a design doc should be revised

- A concept in the doc has been renamed or removed from code
- The doc describes a planned state rather than the current state
- Multiple unrelated concerns are covered in one document
```

### Step 13: Write docs/guides/README.md

```markdown
# Guides

- **Purpose**: How to use the system. User and developer manuals that translate design and conventions into actionable steps.
- **TTL**: long -- mutable when practice changes, but stable once established.
- **Author(s)**: Humans, after a practice stabilizes.
- **Audience(s)**: Both humans and agents needing end-to-end workflow instructions.

## Document Format

Each guide should include:

- **Title** -- what this guide teaches or enables
- **Introduction** -- who this guide is for and what they will be able to do after reading it
- **Prerequisites** -- what the reader needs before starting (tools, access, prior knowledge)
- **Steps or Sections** -- the core content, organized as a logical sequence or by topic
- **Examples** -- concrete, runnable examples wherever possible
- **Troubleshooting** (optional) -- common problems and solutions
- **See Also** -- links to related guides, design docs, or external references

## Conventions

- Write for a competent but unfamiliar person
- Include concrete examples, not just abstract descriptions
- Keep guides updated when the practices they describe change

## Index

- [001-agentic-development-workflow.md](001-agentic-development-workflow.md) -- Step-by-step workflow guide
```

### Step 14: Copy docs/guides/001-agentic-development-workflow.md

Copy the workflow guide from the installed extension into the project:

```bash
cp .specify/extensions/agentic/seed/001-agentic-development-workflow.md docs/guides/001-agentic-development-workflow.md
```

If the file already exists, skip this step.

This file is the day-to-day working reference for the project: how to invoke commands (VS Code vs CLI), the feature lifecycle table, workflow details for bugs and refactors, and session discipline. To update it in the future (e.g., after upgrading the extension), re-run the copy command above.

### Step 15: Create layered AGENTS.md files

Create the following files. If any already exist, do NOT overwrite them.

**AGENTS.md** (project root):

```markdown
# AGENTS.md

This project follows the agentic development pattern. Project-specific
additions go in `AGENTS.local.md` -- additive-only, loaded alongside this file.

## Guiding Principles

### 1. Honest Technical Judgment Over Politeness

- Say "I don't know" when you don't know
- Push back when you disagree, providing your reasoning
- Never be agreeable just to be nice

### 2. Investigate Before Acting

- Stop and ask when multiple valid approaches exist
- Read error messages completely -- they often contain the solution
- Find and understand working examples before implementing patterns
- Test one hypothesis at a time

### 3. Strive For Durable Shared Understanding

- Consider whether what is being asked is well formulated and clear
- Ask clarifying questions if needed
- Once you believe you understand, restate what you think the shared intent is
- Read `./docs` and consider if what is being asked is additive or a change

## This Project

See `docs/design/001-agentic-development-pattern.md` for the model that
organizes this file, the docs/ scheme, and the rubrics.

## Working with Project Knowledge

- Check `docs/plans/README.md` for current priorities at session start
- Check `docs/decisions/` when making architectural choices
- Update plans and create ADRs before committing significant changes

## AGENTS.local.md

Include `AGENTS.local.md` for project-specific additions. Its rules add to --
never override -- those above.

@AGENTS.local.md
```

### Step 16: (Optional) Create src/ and tests/ AGENTS.md files

These are optional. Create them if the project has source code and tests directories. Adapt the directory names to match the project's structure (e.g., `lib/` instead of `src/`).

**src/AGENTS.md** (or equivalent source directory):

```markdown
# Source Code Conventions

## Code Quality

- Simple, clean, and maintainable beats clever
- The best code is code you don't write (YAGNI)
- Reduce duplication; commit frequently

## Naming

- Names describe what things ARE, not implementation details
- Good: Registry, Tool, execute()
- Bad: MCPToolWrapper, executeToolWithValidation()

## Comments

- Correct, clear, and concise docstrings
- Explain WHAT and WHY, never reference what "used to be"
- Match surrounding code style; use the project's formatter and linter

## Testing

- Strive for TDD: write test, see it fail, write code, green
- See tests/AGENTS.md for testing conventions
```

**tests/AGENTS.md**:

```markdown
# Testing Conventions

## Framework

- Use the project's established test framework
- Avoid mocking except where demonstrably valuable
- Target >75% coverage (not dogmatic 100%)

## Workflow

- Write a failing test first, confirm it fails, make it pass, refactor

## Rules

- Separate unit tests from acceptance/integration tests
- Never hide failing tests with trivial assertions
- Never delete a failing test without understanding why it fails
- Test real logic, not mocked behavior
- Test output should be pristine (capture expected errors)
```

**docs/AGENTS.md** (always create — this is part of the docs/ tree):

````markdown
# Documentation Conventions

## Format

- Write in Markdown with Mermaid for diagrams
- Plain ASCII: no em-dashes, no smart-quotes
- Do not wrap long lines (one sentence or clause per line is fine)
- Prefer bullet lists to numbered lists
- Blank lines after headings and around code fences
- Code blocks must have a language qualifier (e.g., ```python, ```bash)
- Fix all linter warnings

## Tooling

- **mdformat**: auto-formatter. Config in `.mdformat.toml`.
- **markdownlint-cli2**: linter. Config in `.markdownlint.json` and `.markdownlint-cli2.jsonc`.
- Run `mise run lint:markdown` before committing markdown changes.

## When Making Changes

- Update existing docs or deprecate them if the system changed
- Update docs/plans/README.md if priorities shifted
- Create an ADR if an architectural decision was made
````

### Step 17: (Optional) Set up markdown tooling

This step is optional. It sets up formatting and linting for markdown files. Skip it if the project does not need automated markdown quality checks.

If the user wants markdown tooling, create the following configuration files (skip any that already exist).

**.mdformat.toml** (project root):

```toml
# mdformat configuration
# https://mdformat.readthedocs.io/en/stable/users/configuration_file.html

wrap = "no"         # Don't rewrap paragraphs
number = false      # Use 1. for all ordered list items (minimizes diffs)
end_of_line = "lf"  # Unix line endings

# Extensions
# - frontmatter: preserve YAML frontmatter
# - gfm: GitHub Flavored Markdown (tables, etc.)
extensions = ["frontmatter", "gfm"]
```

**.markdownlint.json** (project root):

```json
{
  "MD007": {
    "indent": 2
  },
  "MD013": false,
  "MD032": false,
  "MD034": false,
  "MD036": false,
  "MD046": false
}
```

**.markdownlint-cli2.jsonc** (project root):

```jsonc
{
  // Extend the existing markdownlint config
  "extends": ".markdownlint.json",
  // Ignore auto-generated and vendored files
  "ignores": [".github/**", ".specify/**", ".venv/**", "node_modules/**"]
}
```

**.mise/tasks/lint/markdown.sh**:

```bash
#!/usr/bin/env bash
#MISE description="Lint markdown files (mdformat + markdownlint-cli2)"

set -o pipefail
set -o nounset
set -o errexit

cd "$(git rev-parse --show-toplevel)"

git ls-files '*.md' ':!CHANGELOG.md' ':!.github/**' | xargs mdformat --check

markdownlint-cli2 "**/*.md"
```

After creating the lint task, make it executable (`chmod +x`).

Also ensure the project has the required dependencies:

- **mdformat** and plugins: install via pip, uv, or your package manager (`pip install mdformat mdformat-frontmatter mdformat-gfm`)
- **markdownlint-cli2**: add via mise (`mise use npm:markdownlint-cli2`) or npm

### Step 18: Report completion

After creating all files, report a summary of what was scaffolded:

- Count of directories created
- Count of files created vs skipped (already existed)
- Remind the user to customize AGENTS.md and fill in docs/plans/README.md

## Notes

- This command is idempotent: re-running it will not overwrite existing files
- The docs/ tree is project-owned, not extension-owned — users should customize freely
- AGENTS.local.md files are for project-specific additions that layer on top of AGENTS.md
