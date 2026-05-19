# ADR Rubric

Evaluative criteria for architecture decision records.

## Worth Recording

### The decision is hard to reverse

If the decision is trivially changeable later, it may not need an ADR.

### Alternatives were genuinely considered

At least two alternatives were evaluated. Straw-man alternatives (included only to be rejected) weaken the record.

## Ages Well

### Context reads correctly months later

A reader unfamiliar with the project can understand why the decision was made from the context alone.

### Consequences are two-sided

Both benefits and drawbacks are listed. An ADR with only positive consequences is a sales pitch, not a record.

### Decision is stated imperatively and specifically

- Weak: "We should probably use a database"
- Strong: "Use PostgreSQL 16 for the primary data store"

## Stays Current

### Status reflects reality

An accepted ADR whose decision was later reversed should be marked Superseded with a link to the new ADR.

## Signals that an ADR should be revised

- Context section references "we" without explaining who or why
- Consequences section lists only benefits
- Decision uses hedging language ("might," "should consider")
- Status is Accepted but the decision is no longer followed
