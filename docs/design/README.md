# Design Documents

- **Purpose**: The system as it currently is. Bridge between decisions (WHY) and code (WHAT). A stale design doc is a defect.
- **TTL**: long -- updated alongside code as the system evolves.
- **Author(s)**: Updated alongside code when design changes.
- **Audience(s)**: Agents understanding intent before changing implementation; humans onboarding.

See `RUBRIC.md` in this folder for the criteria a design doc must meet.

## Document Format

Each design document should include:

- **Title** -- what this document describes (a subsystem, a data model, a workflow)
- **Overview** -- one-paragraph summary of the component and its role in the system
- **Current Design** -- how it works today: key abstractions, data flow, relationships to other components
- **Interfaces** -- public API, configuration, or integration points that other components depend on
- **Constraints and Invariants** -- rules that must hold (e.g., "all writes go through the event bus")
- **See Also** -- links to related ADRs, feature docs, or other design docs

Diagrams (Mermaid preferred) are encouraged when they clarify relationships that prose alone would obscure.

## Organization

- **Conceptual**: Domain models, core abstractions, key relationships
- **Technical**: Architecture, data flow, infrastructure
- **Features**: UI workflows, integration points, user-facing behavior
