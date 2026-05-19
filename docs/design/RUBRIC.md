# Design Document Rubric

Evaluative criteria for design documents.

## Cold-Start Readability

### A reader with no prior context can act on it

The document does not assume familiarity with prior conversations or sessions.

### States current truth, not history

Describes the system as-built, not the journey to get there. History belongs in ADRs.

### Diagrams carry their weight

Every diagram communicates something that prose alone would obscure. Decorative diagrams are noise.

## Correctness

### Matches code

Concepts, names, and relationships described in the design doc exist in the codebase.

### Concepts named in the doc exist in code

If the doc names a "Registry" class, a Registry exists in the source.

## Scope and Framing

### One concern per document

A design doc that covers both data modeling and deployment topology should be split.

### Links, not copies

When referencing information from another doc, link to it. Duplicated content drifts.

## Signals that a design doc should be revised

- A concept in the doc has been renamed or removed from code
- The doc describes a planned state rather than the current state
- Multiple unrelated concerns are covered in one document
