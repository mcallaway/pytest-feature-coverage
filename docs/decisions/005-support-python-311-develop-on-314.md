# ADR-005: Support Python >=3.11 While Developing on 3.14

- **Status**: Accepted
- **Date**: 2026-08-24

## Context

The package previously required Python >=3.14. That floor matches the local toolchain (`mise` pins 3.14) but excludes consumers still on maintained 3.11 and 3.12 runtimes. The plugin source does not use 3.12+ language features, and primary dependencies (pytest 9+, pydantic 2+, PyYAML) already support 3.11.

Two needs conflict if collapsed into one version pin:

1. Developers want a current local runtime (3.14) for day-to-day work.
1. Consumers need a broader install floor (>=3.11) with evidence that the floor is real.

## Decision

Declare `requires-python = ">=3.11"`.

Keep the local toolchain on Python 3.14 (`mise.toml`, publish job).

Type-check against the support floor (`[tool.ty.environment] python-version = "3.11"`) so APIs unavailable on 3.11 fail in CI before consumers hit them.

Run PR validation on both 3.11 and 3.14 so the declared floor and the development runtime are both exercised.

## Consequences

### Positive

- Installable on common maintained Python versions without forcing consumers onto 3.14.
- Local development stays on the preferred current runtime.
- The support claim is backed by CI on the minimum and on the development version.

### Negative

- PR CI runtime roughly doubles (matrix of two Python versions).
- Developers must avoid 3.12+ syntax and stdlib APIs even while coding under 3.14; the type checker and 3.11 CI job are the safety net, not the local interpreter alone.
