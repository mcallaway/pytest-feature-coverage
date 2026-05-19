# Documentation Conventions

## Format

- Write in Markdown with Mermaid for diagrams
- Plain ASCII: no em-dashes, no smart-quotes
- Do not wrap long lines (one sentence or clause per line is fine)
- Prefer bullet lists to numbered lists
- Blank lines after headings and around code fences
- Code blocks must have a language qualifier (e.g., `python`, `bash`)
- Fix all linter warnings

## Tooling

- **mdformat**: auto-formatter. Config in `.mdformat.toml`.
- **markdownlint-cli2**: linter. Config in `.markdownlint.yaml` and `.markdownlint-cli2.yaml`.
- Run `mise run lint:markdown` before committing markdown changes.

## When Making Changes

- Update existing docs or deprecate them if the system changed
- Update docs/plans/README.md if priorities shifted
- Create an ADR if an architectural decision was made
