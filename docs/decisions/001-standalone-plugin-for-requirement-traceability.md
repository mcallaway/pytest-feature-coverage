# ADR-001: Create a Standalone pytest Plugin for Requirement Traceability

- **Status**: Accepted
- **Date**: 2026-05-19

## Context

During May 2026, work on a Python project template (Copier-based) surfaced a gap: tests had feature-level markers but there was no machine-verifiable mapping from individual requirements to specific tests. Coverage tools like `pytest-cov` answer "did tests execute these lines?" — not "do tests cover these declared requirements?"

Around the same time, the [ACAI Specsmaxxing post](https://www.answer.ai/posts/2025-04-08-specsmaxxing.html) described a pattern of YAML-defined requirements linked to test annotations and scanned by a coverage reporter. The pattern was appealing; the ACAI-specific tooling was not a fit for this environment.

Two options were considered:

1. Embed requirement-traceability logic directly in the project template (Copier), so each repo that used the template would inherit it.
1. Build a standalone, installable pytest plugin that any Python project could adopt independently of how it was scaffolded.

## Decision

Build `pytest-feature-coverage` as a **standalone pytest plugin**, published to the internal Artifactory index, implementing the ACAI pattern without ACAI tooling:

- Requirements are defined in `*.feature.yaml` files (Pydantic-validated schema).
- Tests are annotated with `@pytest.mark.req(*ids)` markers.
- A scanner maps markers to requirement IDs at collection time.
- A reporter computes and prints a deterministic coverage matrix.
- A CI threshold gate (`--feature-coverage-min`) fails the suite if coverage drops below a configured floor.
- No AI at runtime — coverage computation is purely deterministic.

The plugin was shipped as v0.1.1 within the same week it was started (May 19–20, 2026).

## Consequences

### Positive

- Any Python project can adopt requirement traceability by adding one dependency and one INI setting — no template coupling.
- The coverage report is deterministic and CI-checkable; it cannot vary between runs for the same test suite.
- Splitting into a standalone project created clear boundaries: the plugin owns the schema, scanner, matrix, and reporters; consuming projects own their feature YAML files and marker annotations.
- The plugin became part of a broader developer-experience toolchain alongside `python-devex-standards` and `speckit-agentic-workflow`.

### Negative

- As a standalone project, the plugin accrues its own maintenance burden (versioning, docs, CI, compatibility with pytest releases).
- Coverage quality depends entirely on consistent marker discipline in consuming projects — a requirement is counted covered when a tagged test is *collected*, not when it *passes*. Incomplete tagging produces false confidence.
- Documentation debt accumulated quickly after initial shipment; user-guide coverage lagged behind feature development.
