# FSDC evidence ingestion policy

No proprietary or unlicensed FAITH datasets are committed to this public hackathon repository. HACK-002 accepts a user-supplied JSON array of records with the required fields in `config/faith_agent_registry.json`, plus `sectors` and `finding`. Only `ADMISSIBLE` records from the requested sector may enter model prompts.

Boké science remains `NOT_FIELD_VALIDATED` at this phase, so the default empty-evidence run **abstains**, rather than falsely claiming that the application has connected to a validated live FSDC backend. Do not change statuses to ADMISSIBLE merely to make a demo run.

The test suite creates artificial fixtures internally, clearly marked as TEST-ONLY and not scientific measurements.

Model-generated outputs are `GENERATED_UNVERIFIED`, and still require mechanical citation verification, human review and provenance QA in HACK-003.
