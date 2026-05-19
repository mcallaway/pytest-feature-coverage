______________________________________________________________________

## Agentic Workflow: Driving Ideas

> This section is added by the agentic-workflow preset. It captures the foundational ideas that shape how this project manages knowledge.

### Information Has a Time-to-Live

Some statements are meant to be true forever — a decision was made on a date, and these alternatives were rejected. Some are meant to be true until the system changes — the design as it currently stands. Some are meant to be true until the work completes — an in-flight plan. Some are meant to be true for the rest of an afternoon — a session note.

Storing these the same way, in the same place, with the same review discipline, is what causes documentation to drift, conflict, and rot. The `docs/` tree separates information by how long it is meant to live.

### Authors and Audiences Can Each Be Human or Agent

A plan written today by a human-and-agent pair will be read tomorrow by a different agent in a fresh session. A design doc written today will be read months later by a human joining the project. A decision recorded in a moment will be consulted years later by readers who were not there.

Every artifact is written so the readers it actually expects — human or agent, near or distant — can act on it without the original author present.

### Durable Shared Understanding

When asked to create something:

1. Consider whether what is being asked is well formulated and clear
1. Ask clarifying questions if needed
1. Once you believe you understand, restate what you think the shared intent is
1. Read `./docs` and consider if what is being asked is additive or a change

### AGENTS.md Layering

This project uses layered AGENTS.md files that provide increasingly specific instructions:

- `AGENTS.md` (root) -- guiding principles and project overview
- Directory-level AGENTS.md files -- conventions specific to that area (src/, tests/, docs/)

Each layer adds to (never overrides) the layers above. Project-specific additions go in `AGENTS.local.md` at the root.

### Documentation Scheme

The `docs/` tree provides project-level knowledge that persists across features:

| Folder       | What lives here                       | TTL       |
| ------------ | ------------------------------------- | --------- |
| `features/`  | User stories with acceptance criteria | long      |
| `plans/`     | Roadmap dashboard + plan rubric       | short     |
| `decisions/` | ADRs (immutable once accepted)        | immutable |
| `design/`    | The system as it currently is         | long      |
| `guides/`    | How to use the system                 | long      |

Run `/speckit.agentic.scaffold` to create this structure if it does not exist.

### Relationship to Constitution

The constitution defines project principles. AGENTS.md files translate those principles into actionable rules for agents. The `docs/` tree captures the knowledge that accumulates as principles are applied to real work.

```text
Constitution (values) --> AGENTS.md (rules) --> docs/ (accumulated knowledge)
```
