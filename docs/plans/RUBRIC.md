# Plan Rubric

Evaluative criteria for plan documents in `.specify/specs/NNN/plan.md`. Applied automatically via the `after_plan` hook, or manually with `/speckit.agentic.apply-rubric`.

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

### Close-out criteria match deliverables

What counts as "done" aligns with what the phases produce.

## Signals that a plan should be revised

- A phase deliverable is stated as a process ("researching X") rather than an artifact
- Goals section is missing or only restates the title
- No feature or decision is referenced as motivation
