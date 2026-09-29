# ADR-006: Define "Covering Test" as Execution-Aware, Not Collection-Time (Amends ADR-003 Layer 2)

- **Status**: Accepted
- **Date**: 2026-09-29
- **Deciders**: pytest-feature-coverage maintainers (agentic session)

## Context

ADR-003 defines Layer 2 ("Feature coverage") as: "every declared requirement has at least one covering test." That wording does not say what "covering" requires of the test beyond having been collected with a matching `req()` marker. In practice, the plugin computed coverage during `pytest_collection_modifyitems`: any collected node ID carrying a `req()` marker counted as covering, regardless of whether that test later passed, failed, was skipped, or errored.

This produced false confidence: a skipped test, an expected failure (`xfail`), or a test that failed during setup or execution all counted as proof the requirement was covered, when none of them supplied any actual verification evidence. The plugin is meant to be a CI gate and completion signal (ADR-003's own framing); collection proves a test was declared, not that it verified anything.

A related question the feature request forced explicitly: what should happen to a test marked `xfail` that unexpectedly passes (`xpass`, non-strict)? Every other special outcome (fail, skip, xfail, setup/teardown error) clearly should not count. `xpass` is genuinely ambiguous: the test did execute its body without raising, which looks like a pass, but the test's own marker declares an expectation of failure.

This project's `docs/decisions/README.md` treats ADRs as immutable once accepted; amendments to an already-accepted decision are made via a new ADR, not by rewriting the original. ADR-003 is Accepted, so this record amends it rather than editing its body text.

## Decision

Redefine "covering test" (as used in ADR-003 Layer 2, and enforced by `pytest --feature-coverage`) as: a test node ID that was associated with a requirement via `req()` at collection time AND achieved a clean pass across its setup, call, and teardown phases at runtime.

Concretely:

- Passed: counts as coverage.
- Failed, skipped, `xfail` (expected failure), or a setup/teardown error: does NOT count as coverage.
- Unexpected pass (`xpass`, non-strict `xfail`): does NOT count as coverage. An `xfail` marker is a declared expectation of failure; a test passing unexpectedly signals the marker is stale or the requirement's behavior changed underneath it, not that the requirement was verified as intended. Rewarding that with coverage credit would let a known-inconsistent test silently keep a requirement "green."
- Deselected or never-executed tests: excluded by construction, since they never produce a passing outcome for any node ID.
- When multiple tests reference the same requirement, one clean pass is sufficient even if other associated tests fail, skip, or xfail; reports identify only the node IDs that supplied the passing evidence.

Collection-time responsibilities are unchanged: loading and validating requirement IDs, detecting orphan `req()` markers, and associating requirement IDs with collected node IDs. Only the determination of which associated node IDs earn coverage credit moves from collection time to runtime outcome tracking.

ADR-003 itself is not rewritten. Its Layer 2 line is annotated with a pointer to this ADR for the current, precise definition of "covering."

## Alternatives Considered

### Treat xpass as coverage (a passing test body is still a passing test body)

Rejected. This would mean a stale `xfail` marker on a test whose underlying behavior changed could keep reporting a requirement as covered indefinitely, even though the test's own author declared they did not expect it to behave that way. It rewards an inconsistency between the marker and reality instead of surfacing it.

### Rewrite ADR-003's Layer 2 text in place

Rejected. `docs/decisions/README.md` states ADRs are immutable once accepted; amendments happen via a new ADR. Editing ADR-003's body would violate that project convention and erase the historical record of what was actually decided and when.

### Track outcomes by wrapping `pytest_collection_modifyitems` more aggressively (e.g. deferring the whole scan to session finish)

Rejected. Collection-time responsibilities (orphan detection, requirement-to-node-ID association) are correct as-is and have their own test coverage; only the coverage *computation* needs runtime awareness. Keeping the scan at collection time and adding a separate runtime outcome tracker is a smaller, more surgical change than restructuring collection.

## Consequences

### Positive

- The feature-coverage percentage and the `--feature-coverage-min` CI gate become honest signals: a green result means tests actually passed, not merely that tests referencing the requirement exist.
- The `xpass` policy is explicit and documented rather than an accidental side effect of how pytest's `skipping` plugin sets `TestReport.outcome`.
- ADR-003 remains an intact historical record; this ADR is the discoverable, current source of truth for Layer 2's precise definition.

### Negative

- Suites that were passing the coverage threshold purely on collection-time association (with skipped, xfailed, or failing tests attached to `req()` markers) may see their reported coverage percentage drop after upgrading, even though nothing about their requirements changed. This is the intended correction, but it is a behavior change worth calling out in release notes.
- The plugin now needs to track runtime outcomes per node ID across three pytest phases (setup/call/teardown), which is more runtime state than the previous collection-only design.
