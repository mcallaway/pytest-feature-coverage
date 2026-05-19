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
