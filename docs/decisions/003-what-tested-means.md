# ADR-003: What "Tested" Means in This Project

- **Status**: Accepted (Layer 2's definition of "covering test" is refined by [ADR-006](006-execution-aware-covering-test.md))
- **Date**: 2026-07-18

## Context

During a coverage push to reach 100% on the `feat/coverage-filter` branch, three bugs were introduced or left undetected despite the coverage metric reading 100%:

1. A missing `class TestJsonReporter:` declaration caused `pytestmark` to silently overwrite `TestTextReporter`'s mark. All JSON reporter tests ran inside the wrong class, misclassifying six tests under `OUTPUT_FORMATS.1` and zeroing out `COVERAGE_REPORT.1` in the feature coverage report.

1. A `try/except ValueError` guard in `tests/conftest.py` was dead code. `pytest.Parser.addini()` does not raise `ValueError` on duplicate registration — it silently overwrites. The `except` branch was unreachable.

1. A `str.index` / `str.rindex` JSON extraction in an integration test parsed the first `{` and last `}` in raw stdout. It passed, but any brace in pytest headers or warning text would have silently produced a malformed substring. A brace-depth accumulator is the correct approach.

All three bugs were invisible to the coverage metric. The root cause: **we were measuring execution, not correctness**. 100% source coverage says "every line in `src/` ran during the test session." It does not say:

- Test classes are structured correctly and markers are applied to the right tests.
- Test infrastructure (`conftest.py`, helpers) is correct.
- Assertions are resilient to incidental output changes.

A second observation: bug #1 would have been caught by reading the feature coverage report. `COVERAGE_REPORT.1` showing 0 covering tests while `OUTPUT_FORMATS.1` showed an unexpected count was a visible signal we did not check because we were focused on the coverage percentage.

## Decision

Adopt a layered definition of "tested":

**Layer 1 — Execution coverage** (`mise run test:coverage`) Source lines and branches execute. Necessary but not sufficient. The number itself (`100%`) is not the goal — it is a floor that prevents obvious gaps.

**Layer 2 — Feature coverage** (`mise run test:features`) Every declared requirement has at least one covering test. *Read the output*, not just the pass/fail. A requirement with 0 covering tests is a warning even when overall coverage is 100%. See [ADR-006](006-execution-aware-covering-test.md) for the precise, execution-aware definition of "covering test."

**Layer 3 — Structural review** (`speckit.agentic.code-review`) Test infrastructure, class structure, marker correctness, and assertion resilience cannot be verified by automated metrics. Code review is not redundant with coverage — it catches orthogonal failure classes. Make it routine, not exceptional.

**Layer 4 — Mutation testing** (future) Verifies that tests *assert correctly*, not just that they *execute*. If a test still passes after a production line is deleted or mutated, the test is not doing its job. This layer is not currently implemented; it is the logical next step when Layer 1–3 leave residual uncertainty.

Treat test infrastructure (`conftest.py`, fixtures, helpers) as production code. It deserves the same review discipline as `src/`.

## Consequences

### Positive

- The definition of "done" is explicit and multi-layered. A green CI run means Layers 1–2 pass; Layer 3 is a human gate at PR time.
- Feature coverage output becomes a required read, not a pass/fail signal. Unexpected zeros in the requirement table are actionable findings.
- Separating the layers clarifies what each tool is good for: coverage finds execution gaps; feature coverage finds requirement gaps; code review finds structural and assertion quality gaps.

### Negative

- "100% coverage" is no longer a sufficient statement of confidence on its own. Teams that equate coverage percentage with quality will find this framing unfamiliar.
- Layer 3 (code review) is a human or agent cost per PR. It cannot be fully automated.
- Layer 4 (mutation testing) adds test-suite runtime. It is deferred until the test suite is stable enough to absorb the cost.
