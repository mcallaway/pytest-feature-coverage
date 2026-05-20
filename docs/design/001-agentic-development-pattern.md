# The Agentic Development Pattern

A development pattern for projects where humans and AI agents share authorship of code, documentation, and decisions. It describes how layered instructions, a documentation scheme, focused prompts, and evaluative rubrics work together to keep authors and audiences aligned over time.

This pattern is portable. It can be implemented in any project repository regardless of language, framework, or domain.

## The Driving Ideas

Two observations shape every part of the pattern.

**Information has a time-to-live.** Some statements are meant to be true forever -- a decision was made on a date, and these alternatives were rejected. Some are meant to be true until the system changes -- the design as it currently stands. Some are meant to be true until the work completes -- an in-flight plan. Some are meant to be true for the rest of an afternoon -- a session note. Storing these the same way, in the same place, with the same review discipline, is what causes documentation to drift, conflict, and rot.

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

| Folder       | What it holds                     | TTL       | Key readers                                    |
| ------------ | --------------------------------- | --------- | ---------------------------------------------- |
| `features/`  | User stories, acceptance criteria | long      | Agents implementing; humans reviewing scope    |
| `plans/`     | Roadmap dashboard + plan rubric   | short     | Fresh agent sessions resuming work             |
| `decisions/` | ADRs (immutable once accepted)    | immutable | Future humans/agents understanding constraints |
| `design/`    | The system as it currently is     | long      | Agents before changing code; humans onboarding |
| `guides/`    | How to use the system             | long      | Both humans and agents needing workflows       |
| `notes.md`   | Scratch pad                       | short     | Current session                                |

Individual per-feature plans live in `.specify/specs/NNN/plan.md` (managed by Spec Kit). `docs/plans/README.md` is a GPS dashboard that indexes active, upcoming, and completed plans.

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

| Command                         | What it does                                        |
| ------------------------------- | --------------------------------------------------- |
| `specify init`                  | Initialize Spec Kit in the project                  |
| `specify extension add agentic` | Install the agentic-workflow extension              |
| `specify preset add agentic`    | Install the companion preset (optional)             |
| `/speckit.constitution`         | Create the project's guiding principles             |
| `/speckit.agentic.scaffold`     | Create the docs/ tree, AGENTS.md files, and rubrics |

### New Feature Development (Full Lifecycle)

Use the full sequence for any new capability that merits a specification:

| Step | Command                               | What it does                                           |
| ---- | ------------------------------------- | ------------------------------------------------------ |
| 1    | `/speckit.specify`                    | Write a spec with user stories and acceptance criteria |
| 2    | `/speckit.clarify`                    | Refine ambiguous requirements (if needed)              |
| 3    | `/speckit.plan`                       | Break the spec into phases with deliverables           |
| 4    | `/speckit.tasks`                      | Generate dependency-ordered implementation tasks       |
| 5    | `/speckit.agentic.start-work`         | Load project context for implementation session        |
| 6    | `/speckit.implement`                  | Execute the tasks                                      |
| 7    | `/speckit.agentic.document-decisions` | Capture trade-offs as ADRs (as needed during 5-6)      |
| 8    | `/speckit.agentic.code-review`        | Review correctness, clarity, testing                   |
| 9    | `/speckit.agentic.review-alignment`   | Check for drift between code and design docs           |
| 10   | `/speckit.agentic.review-pr`          | Pre-merge PR checklist                                 |
| 11   | `/speckit.agentic.close-plan`         | Finalize docs, ADRs, plan status before merge          |

### Small Bugfixes

Not every change needs a full spec. For well-understood bugs:

| Step | Command                                         |
| ---- | ----------------------------------------------- |
| 1    | `/speckit.agentic.start-work`                   |
| 2    | Fix the bug                                     |
| 3    | `/speckit.agentic.code-review`                  |
| 4    | `/speckit.agentic.review-pr` (if creating a PR) |

### Refactoring and Maintenance

For structural improvements, dependency updates, or architectural changes:

| Step | Command                                                               |
| ---- | --------------------------------------------------------------------- |
| 1    | `/speckit.agentic.start-work`                                         |
| 2    | `/speckit.agentic.review-alignment` (understand current design first) |
| 3    | Make changes                                                          |
| 4    | `/speckit.agentic.document-decisions` (if trade-offs were made)       |
| 5    | `/speckit.agentic.code-review`                                        |

### Periodic and As-Needed

| Command                            | When to use                                                                 |
| ---------------------------------- | --------------------------------------------------------------------------- |
| `/speckit.agentic.extract-lessons` | After a feature lands or at milestones -- surface patterns from recent work |
| `/speckit.agentic.codebase-map`    | When the codebase map drifts or after significant structural changes        |
| `/speckit.agentic.apply-rubric`    | Any time -- evaluate artifacts against their rubric                         |
| `/speckit.agentic.onboard`         | New team member or agent; re-familiarization after time away                |

### Where Commands Read and Write

| Command              | Reads from                        | Writes to                            |
| -------------------- | --------------------------------- | ------------------------------------ |
| `/speckit.specify`   | `docs/features/`, `docs/design/`  | `.specify/specs/NNN/spec.md`         |
| `/speckit.plan`      | spec, `docs/plans/README.md`      | `.specify/specs/NNN/plan.md`         |
| `/speckit.implement` | plan, `docs/design/`, AGENTS.md   | Source code                          |
| `start-work`         | `docs/plans/README.md`, AGENTS.md | (context loading)                    |
| `document-decisions` | `docs/design/`                    | `docs/decisions/` (ADR drafts)       |
| `code-review`        | AGENTS.md, `docs/design/`         | Review findings                      |
| `review-alignment`   | `docs/design/`, codebase map      | Drift findings                       |
| `close-plan`         | `docs/plans/`, `docs/decisions/`  | Finalized plan, ADRs, design updates |
| `extract-lessons`    | Git history, `docs/`              | Recommendations for promotion        |
| `codebase-map`       | Source code, `docs/design/`       | `docs/design/codebase-map.md`        |

## See Also

- [Agentic Development Workflow Guide](../guides/001-agentic-development-workflow.md) -- how to follow this pattern step by step
