# Documentation

- **Purpose**: Entry point and orientation for all project documentation.
- **TTL**: long -- updated when folders are added, removed, or repurposed.
- **Author(s)**: Anyone maintaining the docs tree.
- **Audience(s)**: New humans and agents orienting to the project; readers navigating between folders.

## Folders

| Folder       | What lives here                       | TTL       |
| ------------ | ------------------------------------- | --------- |
| `features/`  | User stories with acceptance criteria | long      |
| `plans/`     | Roadmap dashboard + plan rubric       | short     |
| `decisions/` | ADRs (immutable once accepted)        | immutable |
| `design/`    | The system as it currently is         | long      |
| `guides/`    | How to use the system                 | long      |
| `notes.md`   | Scratch pad (pruned aggressively)     | short     |

## Relationships

```text
features/ (what) --drives--> plans/ (work) --produces--> decisions/ (why)
    |                                                          |
    +<-------------------design/ (how)<------------------------+
```

- **features/** define capabilities the system must provide
- **design/** describes how those capabilities are implemented
- **plans/** GPS dashboard indexing active `.specify/specs/` plans; rubric for plan quality
- **decisions/** record trade-offs encountered during implementation
- **guides/** explain how to use the system for humans and agents
