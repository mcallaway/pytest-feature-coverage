# Guide: Reviewing Tests and Reading Reports

## Introduction

This guide is for someone who knows Python but doesn't live in testing frameworks full-time. Its purpose is to help you review AI-generated tests with enough discipline to catch problems that automated metrics miss — and to understand what the reports produced by this project are actually telling you.

By the end of this guide you will be able to:

- Run the test suite and understand what each report means
- Spot the most common structural problems in a test file
- Know what questions to ask when reviewing AI-generated tests

## Prerequisites

- Python familiarity (reading and writing at a basic level)
- `mise` installed (`mise run --help` works)
- The project checked out and dependencies installed (`uv sync`)

## The Layered Model

No single metric tells you whether your code works. Tests provide confidence through layers — each layer catches a different class of problem:

| Layer              | Command                                      | What it catches                                         | What it misses                                      |
| ------------------ | -------------------------------------------- | ------------------------------------------------------- | --------------------------------------------------- |
| Execution coverage | `mise run test:coverage`                     | Lines and branches that never run                       | Incorrectly structured tests, fragile assertions    |
| Feature coverage   | `mise run test:features`                     | Requirements with no covering test                      | Whether those tests actually verify the requirement |
| Structural review  | code review or `speckit.agentic.code-review` | Wrong class structure, dead code, misleading assertions | Nothing — this is the last line of defense          |
| Mutation testing   | (future)                                     | Tests that pass even when production code is broken     | —                                                   |

A 100% coverage number tells you Layer 1 is green. It says nothing about Layers 2–4. See [ADR-003](../decisions/003-what-tested-means.md) for the full rationale.

## Reading `mise run test:coverage`

Run it:

```shell
mise run test:coverage
```

You will see a table like:

```text
Name                                    Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------------------------
src/pytest_feature_coverage/matrix.py     39      0      8      0   100%
src/pytest_feature_coverage/plugin.py     32      0     10      0   100%
...
TOTAL                                    233      0     68      0   100%
```

**What the columns mean:**

- `Stmts` — number of executable statements in the file
- `Miss` — statements that never ran during the test session
- `Branch` — number of decision points (if/else, loops) in the file
- `BrPart` — branches where only one direction was taken
- `Cover` — percentage of statements and branches that executed

**What to look for:**

- Any file below 80% is worth investigating. A low number means large portions of your code are never exercised — bugs there are invisible.
- `BrPart > 0` means a condition always evaluates the same way. Common causes: an error path never triggered, or a default value always used.
- A file at 100% is not necessarily correct — it just means all lines ran.

**What this report cannot tell you:**

- Whether the test that executed a line actually *asserted* anything about it
- Whether test files themselves are correctly structured
- Whether a requirement is covered (that is Layer 2)

## Reading `mise run test:features`

Run it:

```shell
mise run test:features
```

You will see a table like:

```text
Feature: feature-coverage-plugin (001)

  YAML_SCHEMA
    ✓ 1: Feature YAML files conform to schema         [3 tests]
    ✓ 2: Invalid YAML produces a clear error          [1 test]
    ✓ 3: Duplicate feature names produce a clear error [1 test]

  ...

Overall: 18/18 requirements covered (100.0%)
```

**What to look for:**

- **Any requirement showing 0 tests is a red flag** — even if overall coverage is 100%. It means no test has been annotated with that requirement ID. This could mean: the feature isn't tested, or the test exists but the `@pytest.mark.req()` annotation is missing or wrong.
- A requirement covered by only 1 test is acceptable but worth noting for critical paths. Consider whether that single test covers both the happy path and the error path.
- The overall percentage dropping between runs (on a stable branch) means a test was removed or a `req()` annotation was deleted.

**The irony:** This project's own code review session found a bug — a missing class declaration — that caused `COVERAGE_REPORT.1` to show 0 covering tests. Layer 1 (source coverage) was 100%. Layer 2 (feature coverage) was the signal that something was wrong. The lesson: read the table, not just the pass/fail.

## Spotting Structural Problems in Test Files

When you open a test file — especially one written by an AI agent — these are the patterns that most commonly cause silent failures.

### 1. The orphaned `pytestmark`

A class-level `pytestmark` applies a marker to every test in that class. If the class declaration is accidentally omitted, the `pytestmark` assignment is just a variable assignment inside the *previous* class — silently overwriting its marker:

```python
# WRONG — TestJsonReporter class declaration is missing
class TestTextReporter:
    pytestmark = pytest.mark.req('feature.COVERAGE_REPORT.1')

    def test_something(self): ...
    def test_another(self): ...

    """T033: Unit tests for JSON reporter."""   # ← floating docstring, does nothing

    pytestmark = pytest.mark.req('feature.OUTPUT_FORMATS.1')  # ← OVERWRITES above!

    def test_json_structure(self): ...   # ← still inside TestTextReporter
```

```python
# CORRECT
class TestTextReporter:
    pytestmark = pytest.mark.req('feature.COVERAGE_REPORT.1')

    def test_something(self): ...


class TestJsonReporter:          # ← class declaration present
    pytestmark = pytest.mark.req('feature.OUTPUT_FORMATS.1')

    def test_json_structure(self): ...
```

**How to spot it:** A floating string literal between methods is a dead docstring — it executes and is immediately discarded. If you see one, ask whether a `class` declaration was intended above it.

### 2. Assertions that prove nothing

A test that executes code but never asserts anything will always pass:

```python
# WRONG — runs the function, proves nothing
def test_render():
    result = render_text(report)
```

```python
# CORRECT — asserts something specific and meaningful
def test_render():
    lines = render_text(report)
    assert '✓ 1: Does thing' in '\n'.join(lines)
```

**How to spot it:** Scan each test for at least one `assert` statement. A test with no `assert` (and no `pytest.raises`) is not testing anything.

### 3. Assertions that are too broad

A test can have an `assert` and still be nearly useless:

```python
# WEAK — just checks the function returns something
assert result is not None
assert len(lines) > 0
```

Good assertions check the *content* of the output, not just that output exists. Ask: "if I deleted the logic this test is meant to cover, would this assertion catch it?"

### 4. Mocks hiding real behavior

A mock replaces a real object with a fake one that returns whatever you tell it to. This is sometimes necessary, but it means you are testing your assumptions about the dependency, not the real interaction:

```python
# SUSPICIOUS — are we testing the plugin, or just our assumptions about MagicMock?
config = MagicMock()
config.getoption.return_value = 80
```

For simple cases, a `types.SimpleNamespace` with a plain callable is better — it makes the stub explicit and contains no magic:

```python
# BETTER — intent is clear, no hidden behavior
config = types.SimpleNamespace()
config.getoption = lambda *_a, **_kw: 80
```

The rule in this project: prefer `SimpleNamespace` stubs. Only use `MagicMock` when you genuinely need features like call tracking that cannot be replicated simply.

### 5. Fragile test infrastructure

`conftest.py` and test helper functions are production code for your tests. They deserve the same scrutiny. A common pattern to watch for: exception handling that looks defensive but is actually dead code:

```python
# DEAD CODE — addini does not raise ValueError on duplicates
try:
    parser.addini(name, **kwargs)
except ValueError:
    pass  # never reached
```

When reviewing `conftest.py`, ask: is every `try/except` actually reachable? Is every helper function used?

## A Checklist for Reviewing AI-Generated Tests

When an agent produces a new test file, work through these questions before accepting it:

1. **Does every test have at least one meaningful `assert`?** Scan for `assert` statements. Empty tests or `assert result is not None` are not testing behavior.

1. **Does every test class have a `class` declaration?** Look for floating docstrings or `pytestmark` assignments that appear between methods without a preceding `class` line.

1. **Do the `req()` markers match real requirement IDs?** Run `mise run test:features` and check that no requirement shows 0 covering tests. Cross-check the markers in the file against the IDs in `features/`.

1. **Is `conftest.py` or any test helper treated as production code?** If the agent modified `conftest.py`, review it with the same care you would give `plugin.py`. Look for dead exception handlers and unused fixtures.

1. **Are mocks necessary?** If you see `MagicMock`, ask whether `types.SimpleNamespace` would do the job. If `MagicMock` is used, ask what the test would fail to catch if the real implementation changed.

1. **Are assertions resilient to incidental output?** If a test extracts data from stdout or a string, check that the extraction logic handles variation. A test that parses `stdout[stdout.index('{'):]` will break on any output that contains a `{` before the JSON block.

1. **Does source coverage still pass?** `mise run test:coverage` should report 100% (or whatever the established floor is). A drop means new code was added without corresponding tests.

## See Also

- [ADR-003: What "Tested" Means in This Project](../decisions/003-what-tested-means.md)
- [ADR-002: Plugin Hook Coverage Strategy](../decisions/002-plugin-hook-coverage-strategy.md)
- [tests/AGENTS.md](../../tests/AGENTS.md) — rules for agents writing tests
- [002-usage.md](002-usage.md) — how to use the plugin in your own project
